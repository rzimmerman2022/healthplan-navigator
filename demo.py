#!/usr/bin/env python3
"""
HealthPlan Navigator Demo Script
Demonstrates the complete workflow with your actual healthcare plan documents.
"""

import sys
from pathlib import Path

# Add the project to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from healthplan_navigator.core.ingest import DocumentParser
from healthplan_navigator.core.models import Client, PersonalInfo, MedicalProfile, Priorities, Provider, Medication, Priority
from healthplan_navigator.analysis.engine import AnalysisEngine
from healthplan_navigator.output.report import ReportGenerator


def create_ryan_client() -> Client:
    """Create a realistic client profile for Ryan."""
    personal = PersonalInfo(
        full_name="Ryan Healthcare Research",
        dob="1990-03-15",
        zipcode="85001",  # Arizona ZIP
        household_size=1,
        annual_income=85000,
        csr_eligible=False
    )
    
    medical_profile = MedicalProfile(
        providers=[
            Provider(
                name="Dr. Sarah Martinez",
                specialty="Primary Care",
                priority=Priority.MUST_KEEP,
                visit_frequency=2
            ),
            Provider(
                name="Dr. James Wilson",
                specialty="Cardiology",
                priority=Priority.MUST_KEEP,
                visit_frequency=2
            ),
            Provider(
                name="Dr. Emily Chen",
                specialty="Dermatology",
                priority=Priority.NICE_TO_KEEP,
                visit_frequency=1
            )
        ],
        medications=[
            Medication(
                name="Metformin",
                dosage="500mg",
                frequency="Daily",
                annual_doses=365
            ),
            Medication(
                name="Lisinopril",
                dosage="10mg", 
                frequency="Daily",
                annual_doses=365
            )
        ]
    )
    
    priorities = Priorities(
        keep_providers=5,
        minimize_total_cost=4,
        predictable_costs=4,
        avoid_prior_auth=3,
        simple_admin=3
    )
    
    return Client(
        personal=personal,
        medical_profile=medical_profile,
        priorities=priorities
    )


def main():
    """Run the complete analysis on your healthcare documents."""
    print("HealthPlan Navigator Demo")
    print("=" * 50)
    
    # Create client profile
    print("Creating client profile...")
    client = create_ryan_client()
    print(f"Client: {client.personal.full_name}")
    print(f"   Providers: {len(client.medical_profile.providers)}")
    print(f"   Medications: {len(client.medical_profile.medications)}")
    
    # Parse documents
    print("\nParsing healthcare plan documents...")
    parser = DocumentParser()
    documents_dir = Path(__file__).parent / "personal_documents"
    
    # Parse all PDF and DOCX files in the personal_documents directory
    plans = parser.parse_batch(str(documents_dir))
    
    if not plans:
        print("❌ No plans were parsed. Make sure you have PDF/DOCX files in the directory.")
        return
    
    print(f"Successfully parsed {len(plans)} plans:")
    for i, plan in enumerate(plans[:5], 1):  # Show first 5
        print(f"   {i}. {plan.marketing_name} ({plan.issuer}) - ${plan.monthly_premium:.2f}/month")
    if len(plans) > 5:
        print(f"   ... and {len(plans) - 5} more plans")
    
    # Analyze plans
    print("\nAnalyzing plans with 6-metric scoring system...")
    engine = AnalysisEngine()
    report = engine.analyze_plans(client, plans)
    
    print("Analysis complete!")
    
    # Show top 3 recommendations
    print("\nTOP 3 RECOMMENDATIONS:")
    for i, rec in enumerate(report.top_recommendations[:3], 1):
        medal = ["1st", "2nd", "3rd"][i-1]
        print(f"\n{medal} {rec.plan.marketing_name}")
        print(f"   Overall Score: {rec.metrics.weighted_total_score:.1f}/10")
        print(f"   Monthly Premium: ${rec.plan.monthly_premium:.2f}")
        print(f"   Estimated Annual Cost: ${rec.estimated_annual_cost:,.2f}")
        print(f"   Provider Network: {rec.metrics.provider_network_score:.1f}/10")
        print(f"   Medication Coverage: {rec.metrics.medication_coverage_score:.1f}/10")
        print(f"   Total Cost: {rec.metrics.total_cost_score:.1f}/10")
    
    # Generate reports
    print("\nGenerating reports...")
    report_gen = ReportGenerator("./reports")
    
    # Generate all report formats
    summary_file = Path("./reports") / f"executive_summary_{report.generated_at.strftime('%Y%m%d_%H%M%S')}.md"
    summary = report_gen.generate_executive_summary(report)
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    csv_file = report_gen.generate_scoring_matrix_csv(report)
    json_file = report_gen.generate_json_export(report)
    html_file = report_gen.generate_html_dashboard(report)
    
    print("\nGENERATED REPORTS:")
    print(f"   - Executive Summary: {summary_file}")
    print(f"   - Scoring Matrix (CSV): {csv_file}")
    print(f"   - Data Export (JSON): {json_file}")
    print(f"   - Interactive Dashboard: {html_file}")
    
    # Show scoring matrix preview
    print("\nSCORING MATRIX PREVIEW:")
    print("-" * 100)
    print(f"{'Rank':<4} {'Plan Name':<30} {'Score':<8} {'Provider':<8} {'Medication':<10} {'Cost':<6} {'Annual Cost':<12}")
    print("-" * 100)
    
    for i, analysis in enumerate(report.plan_analyses[:10], 1):
        name = analysis.plan.marketing_name[:28] + ".." if len(analysis.plan.marketing_name) > 30 else analysis.plan.marketing_name
        print(f"{i:<4} {name:<30} {analysis.metrics.weighted_total_score:>6.1f}/10 "
              f"{analysis.metrics.provider_network_score:>6.1f}/10 "
              f"{analysis.metrics.medication_coverage_score:>8.1f}/10 "
              f"{analysis.metrics.total_cost_score:>4.1f}/10 "
              f"${analysis.estimated_annual_cost:>10,.0f}")
    
    print("-" * 100)
    print(f"\nRECOMMENDATION: Choose {report.top_recommendations[0].plan.marketing_name}")
    print(f"   This plan scored {report.top_recommendations[0].metrics.weighted_total_score:.1f}/10 overall")
    print(f"   Best balance of provider access, medication coverage, and cost")
    
    print(f"\nDemo complete! Check the './reports' directory for detailed analysis files.")


if __name__ == '__main__':
    main()