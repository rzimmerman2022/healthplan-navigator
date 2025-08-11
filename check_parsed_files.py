#!/usr/bin/env python3
"""Check which files are being parsed with real values"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from healthplan_navigator.core.ingest import DocumentParser

parser = DocumentParser()
documents_dir = Path("personal_documents")

# Track successes and failures
successful = []
zero_premium = []
failed = []

for file_path in documents_dir.glob("*"):
    if file_path.suffix.lower() in ['.pdf', '.docx']:
        try:
            plan = parser.parse_document(str(file_path))
            if plan:
                if plan.monthly_premium > 0 or plan.deductible > 0 or plan.oop_max > 0:
                    successful.append({
                        'file': file_path.name,
                        'premium': plan.monthly_premium,
                        'deductible': plan.deductible,
                        'oop_max': plan.oop_max
                    })
                else:
                    zero_premium.append(file_path.name)
            else:
                failed.append(file_path.name)
        except Exception as e:
            failed.append(f"{file_path.name} (error: {e})")

print("PARSING RESULTS SUMMARY")
print("="*60)
print(f"Successfully parsed with values: {len(successful)}")
print(f"Parsed but all zeros: {len(zero_premium)}")
print(f"Failed to parse: {len(failed)}")

print("\n" + "="*60)
print("FILES WITH ACTUAL VALUES:")
print("="*60)
for item in successful:
    print(f"\n{item['file']}")
    print(f"  Premium: ${item['premium']}")
    print(f"  Deductible: ${item['deductible']}")
    print(f"  OOP Max: ${item['oop_max']}")

if zero_premium:
    print("\n" + "="*60)
    print("FILES WITH ALL ZEROS (need fixing):")
    print("="*60)
    for file in zero_premium[:10]:  # Show first 10
        print(f"  - {file}")