#!/usr/bin/env python3
"""Script to check progress of downloading clinical tables"""

import os
import csv

# Expected record counts
EXPECTED = {
    'ucum': 759,
    'cytogenetic_locations': 862,
    'pharmvar_star_alleles': 1019,
    'drug_ingredients': 2329,
    'rxterms': 9366,
    'icd9cm_diagnoses': 14567,
    'icd9cm_procedures': 3882,
    'icd11_codes': 34194,
    'medical_conditions': 2418,
    'major_surgeries_implants': 284
}

# File mappings
FILES = {
    'ucum': 'nlm/ucum.csv',
    'cytogenetic_locations': 'nlm/cytogenetic_locations.csv',
    'pharmvar_star_alleles': 'nlm/pharmvar_star_alleles.csv',
    'drug_ingredients': 'nlm/drug_ingredients.csv',
    'rxterms': 'nlm/rxterms.csv',
    'icd9cm_diagnoses': 'nlm/icd9cm_diagnoses.csv',
    'icd9cm_procedures': 'nlm/icd9cm_procedures.csv',
    'icd11_codes': 'nlm/icd11_codes.csv',
    'medical_conditions': 'nlm/medical_conditions.csv',
    'major_surgeries_implants': 'nlm/major_surgeries_implants.csv'
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
    print("STATUS POBIERANIA TABEL CLINICAL TABLES")
    print("="*70)
    print()
    
    phase1_complete = 0
    phase2_complete = 0
    phase1_total = 5
    phase2_total = 5
    
    phase1_tables = ['ucum', 'cytogenetic_locations', 'pharmvar_star_alleles', 
                     'drug_ingredients', 'rxterms']
    phase2_tables = ['icd9cm_diagnoses', 'icd9cm_procedures', 'icd11_codes',
                     'medical_conditions', 'major_surgeries_implants']
    
    print("FAZA 1 - Małe tabele referencyjne:")
    print("-"*70)
    for name in phase1_tables:
        filepath = FILES[name]
        expected = EXPECTED[name]
        actual = count_records(filepath)
        status = "OK" if actual >= expected * 0.9 else ("..." if actual > 0 else "NO")
        exists = "TAK" if os.path.exists(filepath) else "NIE"
        print(f"{name:30s} | {actual:6d}/{expected:6d} | {status:3s} | Plik: {exists}")
        if actual >= expected * 0.9:
            phase1_complete += 1
    
    print()
    print("FAZA 2 - Średnie tabele kliniczne:")
    print("-"*70)
    for name in phase2_tables:
        filepath = FILES[name]
        expected = EXPECTED[name]
        actual = count_records(filepath)
        status = "OK" if actual >= expected * 0.9 else ("..." if actual > 0 else "NO")
        exists = "TAK" if os.path.exists(filepath) else "NIE"
        print(f"{name:30s} | {actual:6d}/{expected:6d} | {status:3s} | Plik: {exists}")
        if actual >= expected * 0.9:
            phase2_complete += 1
    
    print()
    print("="*70)
    print(f"POSTĘP: FAZA 1: {phase1_complete}/{phase1_total} | FAZA 2: {phase2_complete}/{phase2_total}")
    print("="*70)
    
    # Check for any files that might be in progress
    all_csv_files = [f for f in os.listdir('nlm') if f.endswith('.csv')]
    print(f"\nWszystkie pliki CSV w nlm/: {len(all_csv_files)}")
    for f in sorted(all_csv_files):
        size = os.path.getsize(f'nlm/{f}')
        print(f"  {f:40s} - {size:>10,} bytes")

if __name__ == '__main__':
    main()
