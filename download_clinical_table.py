#!/usr/bin/env python3
"""
Universal script to download data from NLM Clinical Tables Search Service API.
Supports multiple tables with different configurations.
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

# API Configuration
MAX_COUNT = 500  # Maximum results per request
MAX_TOTAL = 7500  # Maximum offset + count (API limit)
REQUEST_DELAY = 0.5  # Delay between requests (seconds)

# Table configurations
TABLE_CONFIGS = {
    'ucum': {
        'api_path': '/api/ucum/v3/search',
        'output_file': 'nlm/ucum.csv',
        'search_fields': 'code,name',
        'display_fields': 'code,name',
        'value_cols': [0],  # Code is the primary identifier
        'tokens': ['/', '.'],  # Special token separators
        'estimated_size': 759
    },
    'cytogenetic_locs': {
        'api_path': '/api/cytogenetic_locs/v3/search',
        'output_file': 'nlm/cytogenetic_locations.csv',
        'search_fields': 'location',
        'display_fields': 'location',
        'value_cols': [0],
        'estimated_size': 862
    },
    'star_alleles': {
        'api_path': '/api/star_alleles/v3/search',
        'output_file': 'nlm/pharmvar_star_alleles.csv',
        'search_fields': 'StarAlleleName',
        'display_fields': 'StarAlleleName,cDNANucleotideChanges,GeneNucleotideChange,OtherNames,ProteinChange',
        'value_cols': [0],
        'estimated_size': 1019
    },
    'drug_ingredients': {
        'api_path': '/api/drug_ingredients/v3/search',
        'output_file': 'nlm/drug_ingredients.csv',
        'search_fields': 'name,code',
        'display_fields': 'name,code',
        'value_cols': [0],
        'estimated_size': 2329
    },
    'rxterms': {
        'api_path': '/api/rxterms/v3/search',
        'output_file': 'nlm/rxterms.csv',
        'search_fields': 'STR',
        'display_fields': 'STR,STRENGTHS_AND_FORMS',
        'value_cols': [0],
        'estimated_size': 9366
    },
    # Phase 2 tables
    'icd9cm_dx': {
        'api_path': '/api/icd9cm_dx/v3/search',
        'output_file': 'nlm/icd9cm_diagnoses.csv',
        'search_fields': 'code,name',
        'display_fields': 'code,name',
        'value_cols': [0],
        'estimated_size': 14567
    },
    'icd9cm_sg': {
        'api_path': '/api/icd9cm_sg/v3/search',
        'output_file': 'nlm/icd9cm_procedures.csv',
        'search_fields': 'code,name',
        'display_fields': 'code,name',
        'value_cols': [0],
        'estimated_size': 3882
    },
    'icd11_codes': {
        'api_path': '/api/icd11_codes/v3/search',
        'output_file': 'nlm/icd11_codes.csv',
        'search_fields': 'code,title',
        'display_fields': 'code,title,type',
        'value_cols': [0],
        'estimated_size': 34194
    },
    'conditions': {
        'api_path': '/api/conditions/v3/search',
        'output_file': 'nlm/medical_conditions.csv',
        'search_fields': 'name',
        'display_fields': 'name',
        'value_cols': [0],
        'estimated_size': 2418
    },
    'procedures': {
        'api_path': '/api/procedures/v3/search',
        'output_file': 'nlm/major_surgeries_implants.csv',
        'search_fields': 'name',
        'display_fields': 'name',
        'value_cols': [0],
        'estimated_size': 284
    },
    # Phase 3 tables
    'hpo': {
        'api_path': '/api/hpo/v3/search',
        'output_file': 'nlm/hpo.csv',
        'search_fields': 'id,name',
        'display_fields': 'id,name',
        'value_cols': [0, 1],
        'estimated_size': 19903
    }
}

def make_request(base_url, params, retries=3):
    """Make API request with retries"""
    for attempt in range(retries):
        try:
            url = f"{base_url}?{urlencode(params)}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            if attempt < retries - 1:
                print(f"  Retry {attempt + 1}/{retries}...")
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                print(f"  ERROR: Failed request: {e}")
                return None

def get_total_count(base_url, config):
    """Get total number of records in the database"""
    print("Checking total number of records...")
    
    params = {
        'terms': '*',
        'count': 1,
        'offset': 0
    }
    
    if config.get('search_fields'):
        params['sf'] = config['search_fields']
    
    result = make_request(base_url, params)
    if result and len(result) > 0:
        total = result[0]
        print(f"Total records in database: {total:,}")
        return total
    return None

def download_by_pagination(base_url, config):
    """Download all records using pagination (up to 7,500 limit)"""
    print("\n" + "="*60)
    print("Strategy: Pagination (up to 7,500 results)")
    print("="*60)
    
    all_records = []
    seen_codes = set()
    offset = 0
    count = MAX_COUNT
    
    # Try different search terms - some APIs don't support wildcards
    search_terms = ['*', '']
    if 'star_alleles' in config.get('api_path', ''):
        search_terms = ['CYP', 'UGT', 'SLCO', 'ABCB', 'ABCG', 'SLC', 'NAT', 'TPMT', 'DPYD', '']  # Common gene prefixes
    elif 'icd9cm' in config.get('api_path', '') or 'icd11' in config.get('api_path', ''):
        # ICD codes - try numbers and letters
        search_terms = ['*', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    elif 'conditions' in config.get('api_path', '') or 'procedures' in config.get('api_path', ''):
        # Medical conditions/procedures - try letters
        search_terms = ['*', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    elif 'hpo' in config.get('api_path', ''):
        # HPO - Human Phenotype Ontology - try HP: prefix and letters
        search_terms = ['*', 'HP:', 'HP:0', 'HP:1', 'HP:2', 'HP:3', 'HP:4', 'HP:5', 'HP:6', 'HP:7', 'HP:8', 'HP:9']
        # Also try letters for names
        search_terms.extend(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'])
    
    for search_term in search_terms:
        if search_term == '' and offset > 0:
            continue  # Only try empty search once
        offset = 0
        
        while offset < MAX_TOTAL:
            print(f"\nFetching offset {offset:,} to {offset + count:,} (term: '{search_term if search_term else '(empty)'}')...")
            
            params = {
                'terms': search_term if search_term else '',
                'count': count,
                'offset': offset
            }
            
            if config.get('search_fields'):
                params['sf'] = config['search_fields']
            
            if config.get('display_fields'):
                params['df'] = config['display_fields']
            
            if config.get('tokens'):
                params['tokens'] = ','.join(config['tokens'])
            
            result = make_request(base_url, params)
            if not result or len(result) < 2:
                print("  No more results or invalid response")
                break
            
            total_available = result[0]
            codes = result[1]
            extra_data = result[2] if len(result) > 2 and result[2] else {}
            display_data = result[3] if len(result) > 3 and result[3] else []
            
            if not codes:
                print("  No more results")
                break
            
            # Process results
            for i, code in enumerate(codes):
                # Skip duplicates
                if code in seen_codes:
                    continue
                seen_codes.add(code)
                
                record = {
                    'code': code,
                }
                
                # Add display fields
                if display_data and i < len(display_data):
                    fields = config.get('display_fields', '').split(',')
                    for j, field in enumerate(fields):
                        field_name = field.strip()
                        if j < len(display_data[i]):
                            value = display_data[i][j] if display_data[i][j] else ''
                            # Don't overwrite 'code' if it's already set
                            if field_name.lower() != 'code' or 'code' not in record:
                                record[field_name] = value
                
                # Add extra fields (if available)
                if extra_data:
                    for field, values in extra_data.items():
                        if i < len(values):
                            value = values[i]
                            if isinstance(value, list):
                                record[field] = '; '.join(str(v) for v in value if v)
                            else:
                                record[field] = str(value) if value else ''
                
                all_records.append(record)
            
            print(f"  Retrieved {len(codes)} records (total so far: {len(all_records):,})")
            
            if len(codes) < count:
                print("  Reached end of results for this search term")
                break
            
            offset += count
            time.sleep(REQUEST_DELAY)
        
        # If we got results with this term, continue with it; otherwise try next term
        if len(all_records) > 0 and offset >= MAX_TOTAL:
            break  # Reached limit, try next search term
        elif len(all_records) == 0 and search_term != search_terms[-1]:
            continue  # No results, try next search term
        else:
            break  # Got results or tried all terms
    
    return all_records

def download_by_alphabet(base_url, config):
    """Download records by searching alphabetically (A*, B*, C*, etc.)"""
    print("\n" + "="*60)
    print("Strategy: Alphabetical search (A*, B*, C*, etc.)")
    print("="*60)
    
    all_records = []
    seen_codes = set()
    # Include special characters that might be in codes
    letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789[/()._-'
    
    for letter in letters:
        print(f"\nSearching for records starting with '{letter}'...")
        offset = 0
        count = MAX_COUNT
        
        while offset < MAX_TOTAL:
            params = {
                'terms': f'{letter}*',
                'count': count,
                'offset': offset
            }
            
            if config.get('search_fields'):
                params['sf'] = config['search_fields']
            
            if config.get('display_fields'):
                params['df'] = config['display_fields']
            
            result = make_request(base_url, params)
            if not result or len(result) < 2:
                break
            
            codes = result[1]
            extra_data = result[2] if len(result) > 2 and result[2] else {}
            display_data = result[3] if len(result) > 3 and result[3] else []
            
            if not codes:
                break
            
            for i, code in enumerate(codes):
                if code in seen_codes:
                    continue
                seen_codes.add(code)
                
                record = {
                    'code': code,
                }
                
                if display_data and i < len(display_data):
                    fields = config.get('display_fields', '').split(',')
                    for j, field in enumerate(fields):
                        field_name = field.strip()
                        if j < len(display_data[i]):
                            value = display_data[i][j] if display_data[i][j] else ''
                            # Don't overwrite 'code' if it's already set
                            if field_name.lower() != 'code' or 'code' not in record:
                                record[field_name] = value
                
                if extra_data:
                    for field, values in extra_data.items():
                        if i < len(values):
                            value = values[i]
                            if isinstance(value, list):
                                record[field] = '; '.join(str(v) for v in value if v)
                            else:
                                record[field] = str(value) if value else ''
                
                all_records.append(record)
            
            print(f"  Retrieved {len(codes)} records for '{letter}' (total: {len(all_records):,})")
            
            if len(codes) < count:
                break
            
            offset += count
            time.sleep(REQUEST_DELAY)
        
        time.sleep(1)  # Be polite between letter searches
    
    return all_records

def download_by_patterns(base_url, config):
    """Download records by searching with various patterns"""
    print("\n" + "="*60)
    print("Strategy: Pattern search (various search patterns)")
    print("="*60)
    
    all_records = []
    seen_codes = set()
    
    # Try various search patterns
    patterns = []
    
    # Add table-specific patterns
    if 'ucum' in config.get('api_path', ''):
        # UCUM has codes with special characters - try key patterns
        patterns = ['-', '!', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
        patterns.extend(['cal', 'deg', 'mol', 'rad', 'sr', 'Hz', 'N', 'J', 'W', 'V', 'A', 'C', 'F', 'H', 'K', 'S', 'T'])
    elif 'star_alleles' in config.get('api_path', ''):
        # Star alleles start with CYP or other gene names
        patterns = ['CYP', '*', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
        patterns.extend(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'])
    elif 'cytogenetic' in config.get('api_path', ''):
        # Cytogenetic locations are like "1p36.33" - start with numbers
        patterns = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', 'X', 'Y']
    else:
        # For other tables, try standard patterns
        patterns = ['*']
        # Add all letters and numbers
        patterns.extend([chr(i) for i in range(ord('A'), ord('Z')+1)])
        patterns.extend([chr(i) for i in range(ord('0'), ord('9')+1)])
    
    for pattern in patterns:
        # Skip patterns that are unlikely to work
        if pattern in ['*', '**', '']:
            continue
            
        print(f"\nSearching pattern '{pattern}'...", end='', flush=True)
        offset = 0
        count = MAX_COUNT
        pattern_found = 0
        
        while offset < MAX_TOTAL:
            # For single character patterns, use wildcard
            search_term = f'{pattern}*' if len(pattern) == 1 else pattern
            
            params = {
                'terms': search_term,
                'count': count,
                'offset': offset
            }
            
            if config.get('search_fields'):
                params['sf'] = config['search_fields']
            
            if config.get('display_fields'):
                params['df'] = config['display_fields']
            
            if config.get('tokens'):
                params['tokens'] = ','.join(config['tokens'])
            
            result = make_request(base_url, params)
            if not result or len(result) < 2:
                break
            
            codes = result[1]
            if not codes:
                break
            
            extra_data = result[2] if len(result) > 2 and result[2] else {}
            display_data = result[3] if len(result) > 3 and result[3] else []
            
            for i, code in enumerate(codes):
                if code in seen_codes:
                    continue
                seen_codes.add(code)
                
                record = {
                    'code': code,
                }
                
                if display_data and i < len(display_data):
                    fields = config.get('display_fields', '').split(',')
                    for j, field in enumerate(fields):
                        field_name = field.strip()
                        if j < len(display_data[i]):
                            value = display_data[i][j] if display_data[i][j] else ''
                            if field_name.lower() != 'code' or 'code' not in record:
                                record[field_name] = value
                
                if extra_data:
                    for field, values in extra_data.items():
                        if i < len(values):
                            value = values[i]
                            if isinstance(value, list):
                                record[field] = '; '.join(str(v) for v in value if v)
                            else:
                                record[field] = str(value) if value else ''
                
                all_records.append(record)
                pattern_found += 1
            
            if len(codes) < count:
                break
            
            offset += count
            time.sleep(REQUEST_DELAY)
        
        if pattern_found > 0:
            print(f" found {pattern_found} records")
        else:
            print(" -")
        
        time.sleep(0.2)  # Shorter delay between patterns
    
    return all_records

def save_to_csv(records, filename, config):
    """Save records data to CSV file"""
    if not records:
        print("No records to save!")
        return
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    print(f"\nSaving {len(records):,} records to {filename}...")
    
    # Get all unique field names from records
    all_fields = set()
    for record in records:
        all_fields.update(record.keys())
    
    # Ensure 'code' is first
    fieldnames = ['code'] + sorted([f for f in all_fields if f != 'code'])
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for record in records:
            # Ensure all fields are present
            row = {}
            for field in fieldnames:
                row[field] = record.get(field, '')
            writer.writerow(row)
    
    file_size = os.path.getsize(filename)
    print(f"OK: Saved {len(records):,} records to {filename} ({file_size:,} bytes)")

def download_table(table_name):
    """Download a specific table"""
    if table_name not in TABLE_CONFIGS:
        print(f"ERROR: Unknown table '{table_name}'")
        print(f"Available tables: {', '.join(TABLE_CONFIGS.keys())}")
        return False
    
    config = TABLE_CONFIGS[table_name]
    base_url = f"https://clinicaltables.nlm.nih.gov{config['api_path']}"
    output_file = config['output_file']
    
    print("="*60)
    print(f"Downloading: {table_name.upper()}")
    print(f"API: {base_url}")
    print(f"Output: {output_file}")
    print("="*60)
    
    # Check total count
    total_count = get_total_count(base_url, config)
    
    # Download records
    # Always try multiple strategies to maximize coverage
    print(f"\nUsing multiple strategies to get all records...")
    
    # Strategy 1: Try with wildcard search and pagination
    records1 = download_by_pagination(base_url, config)
    print(f"\nPagination strategy: {len(records1):,} records")
    
    # Strategy 2: Try alphabetical search
    records2 = download_by_alphabet(base_url, config)
    print(f"\nAlphabetical strategy: {len(records2):,} records")
    
    # Strategy 3: Try searching with common patterns
    records3 = download_by_patterns(base_url, config)
    print(f"\nPattern search strategy: {len(records3):,} records")
    
    # Merge results (remove duplicates by code)
    seen_codes = set()
    all_records = []
    
    # Add records from pagination
    for record in records1:
        code = record.get('code', '')
        if code and code not in seen_codes:
            seen_codes.add(code)
            all_records.append(record)
        elif not code:
            # If no code, use first value as identifier
            first_val = str(list(record.values())[0]) if record.values() else ''
            if first_val and first_val not in seen_codes:
                seen_codes.add(first_val)
                all_records.append(record)
    
    # Add records from alphabetical search
    for record in records2:
        code = record.get('code', '')
        if code and code not in seen_codes:
            seen_codes.add(code)
            all_records.append(record)
        elif not code:
            first_val = str(list(record.values())[0]) if record.values() else ''
            if first_val and first_val not in seen_codes:
                seen_codes.add(first_val)
                all_records.append(record)
    
    # Add records from pattern search
    for record in records3:
        code = record.get('code', '')
        if code and code not in seen_codes:
            seen_codes.add(code)
            all_records.append(record)
        elif not code:
            first_val = str(list(record.values())[0]) if record.values() else ''
            if first_val and first_val not in seen_codes:
                seen_codes.add(first_val)
                all_records.append(record)
    
    print(f"\nCombined: {len(all_records):,} unique records")
    
    # Save to CSV
    if all_records:
        save_to_csv(all_records, output_file, config)
        
        # Show sample
        print("\n" + "="*60)
        print("Sample entries (first 5):")
        print("="*60)
        for i, record in enumerate(all_records[:5], 1):
            code = record.get('code', 'N/A')
            # Show first few fields
            fields_shown = []
            for key, value in list(record.items())[:3]:
                if key != 'code' and value:
                    fields_shown.append(f"{key}={value[:50]}")
            print(f"{i}. {code}: {', '.join(fields_shown)}")
    else:
        print("\nNo records retrieved!")
        return False
    
    print("\n" + "="*60)
    print("DOWNLOAD COMPLETE")
    print("="*60)
    return True

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python download_clinical_table.py <table_name>")
        print("\nAvailable tables:")
        for table_name, config in TABLE_CONFIGS.items():
            size = config.get('estimated_size', '?')
            print(f"  {table_name:20s} - {size:,} records (est.)")
        print("\nOr use 'all' to download all tables in phase 1")
        return
    
    table_arg = sys.argv[1].lower()
    
    if table_arg == 'all':
        # Download all phase 1, 2 and 3 tables
        phase1_tables = ['ucum', 'cytogenetic_locs', 'star_alleles', 'drug_ingredients', 'rxterms']
        phase2_tables = ['icd9cm_dx', 'icd9cm_sg', 'icd11_codes', 'conditions', 'procedures']
        phase3_tables = ['hpo']
        all_tables = phase1_tables + phase2_tables + phase3_tables
        print("="*60)
        print("Downloading all Phase 1, Phase 2 and Phase 3 tables")
        print("="*60)
        
        for table_name in all_tables:
            print(f"\n\n{'='*60}")
            print(f"Processing table {all_tables.index(table_name) + 1}/{len(all_tables)}: {table_name}")
            print(f"{'='*60}\n")
            
            success = download_table(table_name)
            if not success:
                print(f"WARNING: Failed to download {table_name}")
            
            # Delay between tables
            if all_tables.index(table_name) < len(all_tables) - 1:
                print("\nWaiting 5 seconds before next table...")
                time.sleep(5)
        
        print("\n" + "="*60)
        print("ALL PHASE 1, PHASE 2 AND PHASE 3 TABLES DOWNLOAD COMPLETE")
        print("="*60)
    else:
        download_table(table_arg)

if __name__ == '__main__':
    main()
