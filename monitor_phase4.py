#!/usr/bin/env python3
"""Monitor progress of Phase 4 table downloads"""

import os
import csv
import time
from pathlib import Path

TABLES = {
    'disease_names': {
        'file': 'nlm/genetic_diseases.csv',
        'expected': 46108,
        'name': 'Genetic diseases'
    },
    'ncbi_genes': {
        'file': 'nlm/ncbi_genes.csv',
        'expected': 193685,
        'name': 'NCBI Genes'
    },
    'refseqs': {
        'file': 'nlm/refseq.csv',
        'expected': 82202,
        'name': 'RefSeq'
    }
}

def count_records(filename):
    """Count records in CSV file"""
    if not os.path.exists(filename):
        return 0
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            return sum(1 for row in reader) - 1  # Subtract header
    except Exception as e:
        return -1  # Error

def main():
    print("="*70)
    print("MONITOROWANIE POBIERANIA FAZY 4 - Tabele Genomiki")
    print("="*70)
    print()
    
    all_complete = True
    for key, info in TABLES.items():
        filepath = info['file']
        expected = info['expected']
        name = info['name']
        
        actual = count_records(filepath)
        status = "OK" if actual >= expected * 0.9 else ("..." if actual > 0 else "NO")
        exists = "TAK" if os.path.exists(filepath) else "NIE"
        progress = (actual / expected * 100) if expected > 0 else 0
        
        print(f"{name:30s} | {actual:8d}/{expected:8d} ({progress:5.1f}%) | {status:3s} | Plik: {exists}")
        
        if actual < expected * 0.9:
            all_complete = False
    
    print()
    print("="*70)
    if all_complete:
        print("WSZYSTKIE TABELE UKONCZONE!")
    else:
        print("Pobieranie w toku...")
    print("="*70)

if __name__ == '__main__':
    main()
