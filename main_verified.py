#!/usr/bin/env python3
"""
HealthPlan Navigator - Verified Main Pipeline
Minimal working pipeline with execution proofs showing what ACTUALLY runs.
"""

import sys
import time
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from healthplan_navigator.core.ingest import DocumentParser
from healthplan_navigator.core.models import Client, PersonalInfo, MedicalProfile, Priorities, Provider, Medication, Priority
from healthplan_navigator.analysis.engine import AnalysisEngine
from healthplan_navigator.output.report import ReportGenerator

def create_verified_client():
    """Create client with execution proof"""
    print("[ENTER] create_verified_client")
    
    personal = PersonalInfo(
        full_name="Ryan Healthcare Research",
        dob="1990-03-15",
        zipcode="85001",
        household_size=1,
        annual_income=85000,
        csr_eligible=False
    )
    
    medical_profile = MedicalProfile(
        providers=[
            Provider(name="Dr. Sarah Martinez", specialty="Primary Care", 
                    priority=Priority.MUST_KEEP, visit_frequency=2),
            Provider(name="Dr. James Wilson", specialty="Cardiology", 
                    priority=Priority.MUST_KEEP, visit_frequency=2),
            Provider(name="Dr. Emily Chen", specialty="Dermatology", 
                    priority=Priority.NICE_TO_KEEP, visit_frequency=1)
        ],
        medications=[
            Medication(name="Metformin", dosage="500mg", frequency="Daily", annual_doses=365),
            Medication(name="Lisinopril", dosage="10mg", frequency="Daily", annual_doses=365)
        ]
    )
    
    priorities = Priorities(
        keep_providers=5,
        minimize_total_cost=4,
        predictable_costs=4,
        avoid_prior_auth=3,
        simple_admin=3
    )
    
    client = Client(personal=personal, medical_profile=medical_profile, priorities=priorities)
    print(f"[EXIT] Client created: {client.personal.full_name}")
    return client

def main():
    """Main pipeline with execution verification"""
    print("=" * 70)
    print("VERIFIED EXECUTION PIPELINE - WHAT ACTUALLY RUNS")
    print("=" * 70)
    
    start_time = time.time()
    
    # Step 1: Create client
    print("\n[STEP 1] Creating client profile...")
    client = create_verified_client()
    
    # Step 2: Parse documents
    print("\n[STEP 2] Parsing documents...")
    parser = DocumentParser()
    documents_dir = Path(__file__).parent / "personal_documents"
    
    print(f"[CALL] parser.parse_batch('{documents_dir}')")
    plans = parser.parse_batch(str(documents_dir))
    print(f"[RETURN] {len(plans)} plans parsed")
    
    if not plans:
        print("[ERROR] No plans parsed - check PDF extraction")
        return
    
    # Show what was actually extracted
    print("\n[DATA CHECK] First 3 plans extracted:")
    for i, plan in enumerate(plans[:3], 1):
        print(f"  {i}. {plan.marketing_name}")
        print(f"     Issuer: {plan.issuer}")
        print(f"     Premium: ${plan.monthly_premium}")
        print(f"     Deductible: ${plan.deductible}")
        
        # DATA VALIDATION
        if plan.monthly_premium == 0.0:
            print(f"     [WARNING] Zero premium - extraction likely failed!")
    
    # Step 3: Analyze plans
    print("\n[STEP 3] Running analysis engine...")
    engine = AnalysisEngine()
    
    print(f"[CALL] engine.analyze_plans(client, {len(plans)} plans)")
    report = engine.analyze_plans(client, plans)
    print(f"[RETURN] {len(report.plan_analyses)} analyses generated")
    
    # Show scoring results
    print("\n[SCORING CHECK] Top 3 recommendations:")
    for i, rec in enumerate(report.top_recommendations[:3], 1):
        print(f"  {i}. {rec.plan.marketing_name}")
        print(f"     Score: {rec.metrics.weighted_total_score}/10")
        print(f"     Annual Cost: ${rec.estimated_annual_cost}")
        
        # SCORE VALIDATION
        if rec.metrics.weighted_total_score == report.top_recommendations[0].metrics.weighted_total_score:
            if i > 1:
                print(f"     [WARNING] Identical score to #1 - suspicious!")
    
    # Step 4: Generate reports
    print("\n[STEP 4] Generating reports...")
    report_gen = ReportGenerator("./reports")
    
    # Generate files
    timestamp = report.generated_at.strftime('%Y%m%d_%H%M%S')
    
    print(f"[CALL] generate_executive_summary()")
    summary_file = Path("./reports") / f"executive_summary_{timestamp}.md"
    summary = report_gen.generate_executive_summary(report)
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    print(f"[RETURN] Written to {summary_file}")
    
    print(f"[CALL] generate_scoring_matrix_csv()")
    csv_file = report_gen.generate_scoring_matrix_csv(report)
    print(f"[RETURN] Written to {csv_file}")
    
    print(f"[CALL] generate_json_export()")
    json_file = report_gen.generate_json_export(report)
    print(f"[RETURN] Written to {json_file}")
    
    print(f"[CALL] generate_html_dashboard()")
    html_file = report_gen.generate_html_dashboard(report)
    print(f"[RETURN] Written to {html_file}")
    
    # Final summary
    end_time = time.time()
    print("\n" + "=" * 70)
    print("EXECUTION COMPLETE")
    print(f"Total time: {end_time - start_time:.2f} seconds")
    print("=" * 70)
    
    # Reality check
    print("\n[REALITY CHECK]")
    if all(p.monthly_premium == 0 for p in plans[:5]):
        print("[FAIL] All premiums are $0 - PDF extraction is broken")
    else:
        print("[OK] Non-zero premiums found")
        
    if len(set(a.metrics.weighted_total_score for a in report.plan_analyses[:5])) == 1:
        print("[FAIL] All plans have identical scores - scoring may be broken")
    else:
        print("[OK] Plans have different scores")
    
    print("\nCheck ./reports/ directory for generated files")

if __name__ == "__main__":
    main()