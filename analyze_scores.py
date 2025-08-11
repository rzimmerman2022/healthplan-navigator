#!/usr/bin/env python3
"""Analyze why scores are identical"""

import json

with open('reports/analysis_export_20250811_133519.json') as f:
    data = json.load(f)

# Check variety in extracted data
plans = data['plan_analyses'][:10]
print('EXTRACTED DATA VARIETY CHECK:')
print('='*50)

premiums = [p['plan']['monthly_premium'] for p in plans]
deductibles = [p['plan']['deductible'] for p in plans]
oop_maxes = [p['plan']['oop_max'] for p in plans]
scores = [p['scores']['overall_weighted'] for p in plans]

print(f'Unique premiums: {len(set(premiums))} out of {len(premiums)}')
print(f'Premium values: {premiums[:5]}')
print('')
print(f'Unique deductibles: {len(set(deductibles))} out of {len(deductibles)}')
print(f'Deductible values: {deductibles[:5]}')
print('')
print(f'Unique OOP maxes: {len(set(oop_maxes))} out of {len(oop_maxes)}')
print(f'OOP max values: {oop_maxes[:5]}')
print('')
print(f'Unique scores: {len(set(scores))} out of {len(scores)}')
print(f'Score values: {scores[:5]}')

# Check what's causing identical scores
print('\n' + '='*50)
print('SCORE BREAKDOWN FOR TOP 3 PLANS:')
print('='*50)

for i, p in enumerate(plans[:3], 1):
    print(f'\nPlan {i}: {p["plan"]["marketing_name"]}')
    print(f'  Premium: ${p["plan"]["monthly_premium"]}')
    print(f'  Deductible: ${p["plan"]["deductible"]}')
    print(f'  OOP Max: ${p["plan"]["oop_max"]}')
    print(f'  Scores breakdown:')
    for metric, score in p['scores'].items():
        if metric != 'overall_weighted':
            print(f'    {metric}: {score}')