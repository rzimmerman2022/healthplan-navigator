#!/usr/bin/env python3
"""Test the fixed parser on specific files"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from healthplan_navigator.core.ingest import DocumentParser

parser = DocumentParser()

# Test on a few specific files
test_files = [
    'personal_documents/HealthGov_2025_Gold_AMB_HMO_Easy_Pricing_080124.pdf',
    'personal_documents/HealthGov_2025_Silver_CSR_BCBS_HMO_Easy_Pricing_420167.pdf',
    'personal_documents/HealthGov_2025_Silver_Standard_AMB_HMO_Easy_Pricing_080123.pdf'
]

for file_path in test_files:
    print(f'\n{"="*60}')
    print(f'Testing: {Path(file_path).name}')
    print("="*60)
    
    plan = parser.parse_document(file_path)
    if plan:
        print(f'Plan ID: {plan.plan_id}')
        print(f'Issuer: {plan.issuer}')
        print(f'Marketing Name: {plan.marketing_name}')
        print(f'Premium: ${plan.monthly_premium}')
        print(f'Deductible: ${plan.deductible}')
        print(f'OOP Max: ${plan.oop_max}')
        print(f'Metal Level: {plan.metal_level.value}')
    else:
        print('Failed to parse')