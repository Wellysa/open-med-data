#!/usr/bin/env python3
"""
Script to download the entire HGNC gene database from NLM Clinical Tables API.
Uses multiple search strategies to bypass the 7,500 result limit.
"""

import os
import sys
import time
import json
import csv
import requests
from urllib.parse import urlencode, quote
from collections import defaultdict

try:
    import requests
except ImportError:
    print("Installing requests...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

BASE_URL = "https://clinicaltables.nlm.nih.gov/api/genes/v4/search"
MAX_COUNT = 500  # Maximum results per request
MAX_TOTAL = 7500  # Maximum offset + count
OUTPUT_FILE = "nlm_genes_hgnc.csv"

# All available fields from the API
ALL_FIELDS = [
    'hgnc_id',
    'hgnc_id_num',
    'symbol',
    'location',
    'alias_symbol',
    'prev_symbol',
    'refseq_accession',
    'name',
    'name_mod',
    'alias_name',
    'prev_name'
]

def make_request(params, retries=3):
    """Make API request with retries"""
    for attempt in range(retries):
        try:
            url = f"{BASE_URL}?{urlencode(params)}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            if attempt < retries - 1:
                print(f"  Retry {attempt + 1}/{retries}...")
                time.sleep(2)
            else:
                print(f"  ERROR: Failed request: {e}")
                return None

def get_total_count():
    """Get total number of genes in the database"""
    print("Checking total number of genes...")
    
    # Try with a very broad search
    params = {
        'terms': '*',
        'count': 1,
        'offset': 0,
        'df': 'symbol',
        'cf': 'hgnc_id'
    }
    
    result = make_request(params)
    if result and len(result) > 0:
        total = result[0]
        print(f"Total genes in database: {total:,}")
        return total
    return None

def download_by_pagination():
    """Download all genes using pagination (up to 7,500 limit)"""
    print("\n" + "="*60)
    print("Strategy 1: Pagination (up to 7,500 results)")
    print("="*60)
    
    all_genes = {}
    offset = 0
    count = MAX_COUNT
    
    while offset < MAX_TOTAL:
        print(f"\nFetching offset {offset:,} to {offset + count:,}...")
        
        params = {
            'terms': '*',  # Match everything
            'count': count,
            'offset': offset,
            'df': ','.join(ALL_FIELDS),
            'ef': ','.join(ALL_FIELDS),
            'cf': 'hgnc_id',
            'sf': 'symbol,name'  # Search fields
        }
        
        result = make_request(params)
        if not result or len(result) < 4:
            print("  No more results or invalid response")
            break
        
        total_available = result[0]
        codes = result[1]
        extra_data = result[2] if result[2] else {}
        display_data = result[3]
        
        if not codes:
            print("  No more results")
            break
        
        # Process results
        for i, hgnc_id in enumerate(codes):
            gene_data = {
                'hgnc_id': hgnc_id,
            }
            
            # Add display fields
            if display_data and i < len(display_data):
                for j, field in enumerate(ALL_FIELDS):
                    if j < len(display_data[i]):
                        gene_data[field] = display_data[i][j] if display_data[i][j] else ''
            
            # Add extra fields (if available)
            for field in ALL_FIELDS:
                if field in extra_data and i < len(extra_data[field]):
                    value = extra_data[field][i]
                    if isinstance(value, list):
                        gene_data[field] = '; '.join(str(v) for v in value if v)
                    else:
                        gene_data[field] = str(value) if value else ''
            
            all_genes[hgnc_id] = gene_data
        
        print(f"  Retrieved {len(codes)} genes (total so far: {len(all_genes):,})")
        
        if len(codes) < count:
            print("  Reached end of results")
            break
        
        offset += count
        time.sleep(0.5)  # Be polite
    
    return all_genes

def download_by_alphabet():
    """Download genes by searching alphabetically (A*, B*, C*, etc.)"""
    print("\n" + "="*60)
    print("Strategy 2: Alphabetical search (A*, B*, C*, etc.)")
    print("="*60)
    
    all_genes = {}
    letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    
    for letter in letters:
        print(f"\nSearching for genes starting with '{letter}'...")
        offset = 0
        count = MAX_COUNT
        
        while offset < MAX_TOTAL:
            params = {
                'terms': f'{letter}*',
                'count': count,
                'offset': offset,
                'df': ','.join(ALL_FIELDS),
                'ef': ','.join(ALL_FIELDS),
                'cf': 'hgnc_id',
                'sf': 'symbol'
            }
            
            result = make_request(params)
            if not result or len(result) < 4:
                break
            
            codes = result[1]
            extra_data = result[2] if result[2] else {}
            display_data = result[3]
            
            if not codes:
                break
            
            for i, hgnc_id in enumerate(codes):
                if hgnc_id in all_genes:
                    continue  # Skip duplicates
                
                gene_data = {
                    'hgnc_id': hgnc_id,
                }
                
                if display_data and i < len(display_data):
                    for j, field in enumerate(ALL_FIELDS):
                        if j < len(display_data[i]):
                            gene_data[field] = display_data[i][j] if display_data[i][j] else ''
                
                for field in ALL_FIELDS:
                    if field in extra_data and i < len(extra_data[field]):
                        value = extra_data[field][i]
                        if isinstance(value, list):
                            gene_data[field] = '; '.join(str(v) for v in value if v)
                        else:
                            gene_data[field] = str(value) if value else ''
                
                all_genes[hgnc_id] = gene_data
            
            print(f"  Retrieved {len(codes)} genes for '{letter}' (total: {len(all_genes):,})")
            
            if len(codes) < count:
                break
            
            offset += count
            time.sleep(0.5)
        
        time.sleep(1)  # Be polite between letter searches
    
    return all_genes

def download_by_symbol_patterns():
    """Download genes by searching common symbol patterns"""
    print("\n" + "="*60)
    print("Strategy 3: Symbol pattern search")
    print("="*60)
    
    all_genes = {}
    
    # Search for common patterns
    patterns = [
        '*',  # Everything
        'A*', 'B*', 'C*', 'D*', 'E*', 'F*', 'G*', 'H*', 'I*', 'J*', 'K*', 'L*', 'M*',
        'N*', 'O*', 'P*', 'Q*', 'R*', 'S*', 'T*', 'U*', 'V*', 'W*', 'X*', 'Y*', 'Z*'
    ]
    
    for pattern in patterns:
        print(f"\nSearching pattern '{pattern}'...")
        offset = 0
        count = MAX_COUNT
        
        while offset < MAX_TOTAL:
            params = {
                'terms': pattern,
                'count': count,
                'offset': offset,
                'df': ','.join(ALL_FIELDS),
                'ef': ','.join(ALL_FIELDS),
                'cf': 'hgnc_id',
                'sf': 'symbol'
            }
            
            result = make_request(params)
            if not result or len(result) < 4:
                break
            
            codes = result[1]
            extra_data = result[2] if result[2] else {}
            display_data = result[3]
            
            if not codes:
                break
            
            for i, hgnc_id in enumerate(codes):
                if hgnc_id in all_genes:
                    continue
                
                gene_data = {
                    'hgnc_id': hgnc_id,
                }
                
                if display_data and i < len(display_data):
                    for j, field in enumerate(ALL_FIELDS):
                        if j < len(display_data[i]):
                            gene_data[field] = display_data[i][j] if display_data[i][j] else ''
                
                for field in ALL_FIELDS:
                    if field in extra_data and i < len(extra_data[field]):
                        value = extra_data[field][i]
                        if isinstance(value, list):
                            gene_data[field] = '; '.join(str(v) for v in value if v)
                        else:
                            gene_data[field] = str(value) if value else ''
                
                all_genes[hgnc_id] = gene_data
            
            if len(codes) < count:
                break
            
            offset += count
            time.sleep(0.5)
        
        time.sleep(1)
    
    return all_genes

def save_to_csv(genes_dict, filename):
    """Save genes data to CSV file"""
    if not genes_dict:
        print("No genes to save!")
        return
    
    print(f"\nSaving {len(genes_dict):,} genes to {filename}...")
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=ALL_FIELDS)
        writer.writeheader()
        
        for hgnc_id, gene_data in sorted(genes_dict.items()):
            # Ensure all fields are present
            row = {}
            for field in ALL_FIELDS:
                row[field] = gene_data.get(field, '')
            writer.writerow(row)
    
    file_size = os.path.getsize(filename)
    print(f"✓ Saved {len(genes_dict):,} genes to {filename} ({file_size:,} bytes)")

def main():
    print("="*60)
    print("NLM HGNC Genes Database Downloader")
    print("="*60)
    
    # Check total count
    total_count = get_total_count()
    
    if total_count and total_count <= MAX_TOTAL:
        print(f"\nTotal count ({total_count:,}) is within API limit ({MAX_TOTAL:,})")
        print("Using pagination strategy...")
        all_genes = download_by_pagination()
    else:
        print(f"\nTotal count may exceed API limit ({MAX_TOTAL:,})")
        print("Using multiple strategies to get all genes...")
        
        # Try pagination first
        genes1 = download_by_pagination()
        print(f"\nPagination strategy: {len(genes1):,} genes")
        
        # Try alphabetical search
        genes2 = download_by_alphabet()
        print(f"\nAlphabetical strategy: {len(genes2):,} genes")
        
        # Merge results
        all_genes = {**genes1, **genes2}
        print(f"\nCombined: {len(all_genes):,} unique genes")
    
    # Save to CSV
    if all_genes:
        save_to_csv(all_genes, OUTPUT_FILE)
        
        # Show sample
        print("\n" + "="*60)
        print("Sample entries (first 5):")
        print("="*60)
        for i, (hgnc_id, gene_data) in enumerate(list(all_genes.items())[:5], 1):
            symbol = gene_data.get('symbol', 'N/A')
            name = gene_data.get('name', 'N/A')
            print(f"{i}. {hgnc_id} - {symbol}: {name[:80]}")
    else:
        print("\nNo genes retrieved!")
    
    print("\n" + "="*60)
    print("DOWNLOAD COMPLETE")
    print("="*60)

if __name__ == '__main__':
    main()

