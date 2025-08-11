#!/usr/bin/env python3
"""
Analyze PDF format to understand why extraction is failing
"""

import pdfplumber
from pathlib import Path
import re

def clean_text(text):
    """Clean text for safe printing"""
    # Remove problematic unicode characters
    return ''.join(char if ord(char) < 128 else '?' for char in text)

def analyze_pdf_format():
    pdf_files = [
        "HealthGov_2025_Gold_AMB_HMO_Easy_Pricing_080124.pdf",
        "HealthGov_2025_Silver_CSR_BCBS_HMO_Easy_Pricing_420167.pdf",
        "HealthGov_2025_Plan_Overview_Page1_545935.pdf"
    ]
    
    for pdf_name in pdf_files:
        pdf_path = Path("personal_documents") / pdf_name
        if not pdf_path.exists():
            continue
            
        print(f"\n{'='*70}")
        print(f"ANALYZING: {pdf_name}")
        print('='*70)
        
        with pdfplumber.open(pdf_path) as pdf:
            if not pdf.pages:
                print("No pages found")
                continue
                
            # Get text from first page
            text = pdf.pages[0].extract_text() or ""
            text = clean_text(text)
            
            # Show structure
            print("\nFIRST 600 CHARACTERS:")
            print(text[:600])
            
            # Look for key patterns
            print("\n" + "="*50)
            print("SEARCHING FOR KEY VALUES:")
            print("="*50)
            
            # Search for different premium patterns
            patterns = [
                (r'\$(\d+(?:\.\d{2})?)\s*(?:/\s*)?(?:per\s*)?month', 'Monthly Premium Pattern 1'),
                (r'Premium.*?\$(\d+(?:\.\d{2})?)', 'Premium Pattern 2'),
                (r'Monthly premium.*?\$(\d+(?:\.\d{2})?)', 'Monthly Premium Pattern 3'),
                (r'(\d+(?:\.\d{2})?)\s*/month', 'Per Month Pattern'),
                (r'Deductible.*?\$(\d+(?:,\d{3})?(?:\.\d{2})?)', 'Deductible Pattern'),
                (r'Out-of-pocket maximum.*?\$(\d+(?:,\d{3})?(?:\.\d{2})?)', 'OOP Max Pattern'),
            ]
            
            for pattern, name in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    print(f"\n[FOUND] {name}:")
                    for match in matches[:3]:  # Show first 3 matches
                        print(f"  -> ${match}")
            
            # Show lines containing dollar amounts
            print("\n" + "="*50)
            print("ALL LINES WITH DOLLAR AMOUNTS:")
            print("="*50)
            lines = text.split('\n')
            for line in lines:
                if '$' in line and len(line) < 100:
                    print(f"  {line.strip()}")
            
            # Look for plan name/ID
            print("\n" + "="*50)
            print("POTENTIAL PLAN IDENTIFIERS:")
            print("="*50)
            
            # Common plan ID patterns
            id_patterns = [
                r'Plan ID[:\s]+([A-Z0-9]+)',
                r'([0-9]{5,}AZ[0-9]+)',  # Healthcare.gov format
                r'ID#?\s*([0-9]{6,})',
            ]
            
            for pattern in id_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    print(f"  Plan ID found: {matches[0]}")
                    break

if __name__ == "__main__":
    analyze_pdf_format()