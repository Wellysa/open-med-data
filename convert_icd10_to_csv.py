#!/usr/bin/env python3
"""
Script to convert ICD-10-CM tabular PDF to CSV format.
"""

import re
import csv
import sys

try:
    import pdfplumber
except ImportError:
    print("Installing pdfplumber...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pdfplumber"])
    import pdfplumber

def extract_icd10_codes(pdf_path):
    """
    Extract ICD-10 codes and descriptions from PDF.
    """
    codes = []
    
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Processing {len(pdf.pages)} pages...")
        
        for page_num, page in enumerate(pdf.pages, 1):
            if page_num % 100 == 0:
                print(f"Processed {page_num} pages...")
            
            text = page.extract_text()
            if not text:
                continue
            
            # ICD-10 codes typically follow patterns like:
            # A00.0    Cholera due to Vibrio cholerae 01, biovar cholerae
            # A00.1    Cholera due to Vibrio cholerae 01, biovar eltor
            # Or sometimes with different spacing
            
            # Pattern 1: Code followed by description (most common)
            # Matches: A00.0, A00.1, Z99.9, etc.
            pattern1 = r'^([A-Z]\d{2}(?:\.\d+)?)\s+(.+?)(?=\n[A-Z]\d{2}|$)'
            
            # Pattern 2: More flexible - code with optional spaces
            pattern2 = r'([A-Z]\d{2}(?:\.\d+)?)\s{2,}(.+?)(?=\n(?:[A-Z]\d{2}|$))'
            
            lines = text.split('\n')
            current_code = None
            current_desc = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check if line starts with ICD-10 code pattern
                code_match = re.match(r'^([A-Z]\d{2}(?:\.\d+)?)\s+(.+)', line)
                if code_match:
                    # Save previous code if exists
                    if current_code:
                        desc = ' '.join(current_desc).strip()
                        if desc:
                            codes.append({
                                'code': current_code,
                                'description': desc
                            })
                    
                    current_code = code_match.group(1)
                    current_desc = [code_match.group(2)]
                elif current_code and line:
                    # Continuation of description
                    current_desc.append(line)
            
            # Save last code
            if current_code:
                desc = ' '.join(current_desc).strip()
                if desc:
                    codes.append({
                        'code': current_code,
                        'description': desc
                    })
    
    return codes

def main():
    pdf_path = 'nlm/docs/icd10cm-tabular-2022-April-1.pdf'
    output_path = 'icd10cm-tabular-2022.csv'
    
    print(f"Extracting ICD-10 codes from {pdf_path}...")
    codes = extract_icd10_codes(pdf_path)
    
    print(f"Found {len(codes)} ICD-10 codes")
    
    # Write to CSV
    print(f"Writing to {output_path}...")
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['code', 'description']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for code_data in codes:
            writer.writerow(code_data)
    
    print(f"Successfully created {output_path} with {len(codes)} entries")
    
    # Show first few entries
    print("\nFirst 10 entries:")
    for i, code_data in enumerate(codes[:10], 1):
        print(f"{i}. {code_data['code']}: {code_data['description'][:80]}...")

if __name__ == '__main__':
    main()

