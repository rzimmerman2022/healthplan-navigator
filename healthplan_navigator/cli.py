#!/usr/bin/env python3
"""
HealthPlan Navigator CLI
Command-line interface for healthcare plan analysis and ranking.
"""

import argparse
import json
from pathlib import Path
from typing import Optional

from .core.ingest import DocumentParser
from .core.models import Client, PersonalInfo, MedicalProfile, Priorities, Provider, Medication, Priority
from .analysis.engine import AnalysisEngine
from .output.report import ReportGenerator


def create_sample_client() -> Client:
    """Create a sample client for testing purposes."""
    personal = PersonalInfo(
        full_name="Sample Client",
        dob="1985-06-15",
        zipcode="85001",
        household_size=2,
        annual_income=75000,
        csr_eligible=False
    )
    
    medical_profile = MedicalProfile(
        providers=[
            Provider(
                name="Dr. Smith",
                specialty="Primary Care",
                priority=Priority.MUST_KEEP,
                visit_frequency=2
            ),
            Provider(
                name="Dr. Johnson",
                specialty="Cardiology",
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
            )
        ]
    )
    
    priorities = Priorities(
        keep_providers=5,
        minimize_total_cost=4,
        predictable_costs=3,
        avoid_prior_auth=4,
        simple_admin=3
    )
    
    return Client(
        personal=personal,
        medical_profile=medical_profile,
        priorities=priorities
    )


def load_client_from_json(file_path: str) -> Optional[Client]:
    """Load client data from JSON file."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Parse client data from JSON
        personal = PersonalInfo(**data['client']['personal'])
        
        # Parse providers
        providers = []
        for provider_data in data['client']['medical_profile'].get('providers', []):
            provider = Provider(
                name=provider_data['name'],
                specialty=provider_data['specialty'],
                priority=Priority(provider_data.get('priority', 'nice-to-keep')),
                visit_frequency=provider_data.get('visit_frequency', 1)
            )
            providers.append(provider)
        
        # Parse medications
        medications = []
        for med_data in data['client']['medical_profile'].get('medications', []):
            medication = Medication(
                name=med_data['name'],
                dosage=med_data.get('dosage', ''),
                frequency=med_data.get('frequency', ''),
                annual_doses=med_data.get('annual_doses', 1)
            )
            medications.append(medication)
        
        medical_profile = MedicalProfile(
            providers=providers,
            medications=medications
        )
        
        priorities = Priorities(**data['client'].get('priorities', {}))
        
        return Client(
            personal=personal,
            medical_profile=medical_profile,
            priorities=priorities
        )
    
    except Exception as e:
        print(f"Error loading client data: {e}")
        return None


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="HealthPlan Navigator - Analyze and rank healthcare plans",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze plans in personal_documents directory with sample client
  python -m healthplan_navigator.cli --sample-client --plans-dir ./personal_documents

  # Use custom client data and specific plan files
  python -m healthplan_navigator.cli --client client.json --plans ./personal_documents/plan1.pdf ./personal_documents/plan2.pdf

  # Batch processing with custom output directory
  python -m healthplan_navigator.cli --client client.json --plans-dir ./personal_documents --output ./results

  # Generate all report formats
  python -m healthplan_navigator.cli --sample-client --plans-dir ./personal_documents --format all
        """
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--client',
        type=str,
        help='Path to client JSON file'
    )
    input_group.add_argument(
        '--sample-client',
        action='store_true',
        help='Use sample client data for testing'
    )
    
    # Plan input options
    plan_group = parser.add_mutually_exclusive_group(required=True)
    plan_group.add_argument(
        '--plans',
        nargs='+',
        help='Specific plan files to analyze'
    )
    plan_group.add_argument(
        '--plans-dir',
        type=str,
        help='Directory containing plan documents'
    )
    
    # Output options
    parser.add_argument(
        '--output',
        type=str,
        default='./reports',
        help='Output directory for reports (default: ./reports)'
    )
    
    parser.add_argument(
        '--format',
        choices=['summary', 'csv', 'json', 'html', 'all'],
        default='all',
        help='Output format (default: all)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Load client data
    if args.sample_client:
        client = create_sample_client()
        print("Using sample client data for analysis")
    else:
        client = load_client_from_json(args.client)
        if not client:
            print(f"Failed to load client data from {args.client}")
            return 1
        print(f"Loaded client data for: {client.personal.full_name}")
    
    # Parse plan documents
    parser_obj = DocumentParser()
    plans = []
    
    if args.plans:
        print(f"Parsing {len(args.plans)} plan files...")
        for plan_file in args.plans:
            if args.verbose:
                print(f"  Parsing: {plan_file}")
            plan = parser_obj.parse_document(plan_file)
            if plan:
                plans.append(plan)
            elif args.verbose:
                print(f"    Failed to parse: {plan_file}")
    
    elif args.plans_dir:
        print(f"Parsing all plan documents in: {args.plans_dir}")
        plans = parser_obj.parse_batch(args.plans_dir)
    
    if not plans:
        print("No plans were successfully parsed. Please check your input files.")
        return 1
    
    print(f"Successfully parsed {len(plans)} plans")
    if args.verbose:
        for plan in plans:
            print(f"  - {plan.marketing_name} ({plan.issuer})")
    
    # Analyze plans
    print("Analyzing plans...")
    engine = AnalysisEngine()
    report = engine.analyze_plans(client, plans)
    
    print(f"Analysis complete! Top recommendation: {report.top_recommendations[0].plan.marketing_name}")
    print(f"Overall score: {report.top_recommendations[0].metrics.weighted_total_score:.1f}/10")
    
    # Generate reports
    report_gen = ReportGenerator(args.output)
    generated_files = []
    
    if args.format in ['summary', 'all']:
        summary = report_gen.generate_executive_summary(report)
        summary_file = Path(args.output) / f"executive_summary_{report.generated_at.strftime('%Y%m%d_%H%M%S')}.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        generated_files.append(summary_file)
        print(f"Executive summary: {summary_file}")
    
    if args.format in ['csv', 'all']:
        csv_file = report_gen.generate_scoring_matrix_csv(report)
        generated_files.append(csv_file)
        print(f"Scoring matrix CSV: {csv_file}")
    
    if args.format in ['json', 'all']:
        json_file = report_gen.generate_json_export(report)
        generated_files.append(json_file)
        print(f"JSON export: {json_file}")
    
    if args.format in ['html', 'all']:
        html_file = report_gen.generate_html_dashboard(report)
        generated_files.append(html_file)
        print(f"Interactive dashboard: {html_file}")
    
    print(f"\nAnalysis complete! Generated {len(generated_files)} report files in {args.output}")
    return 0


if __name__ == '__main__':
    exit(main())