#!/usr/bin/env python3
"""
HealthPlan Navigator - Verified Main Pipeline
Minimal, best-practice pipeline with mandatory execution proofs.
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

#!/usr/bin/env python3
"""
HealthPlan Navigator - Verified Main Pipeline
Minimal, best-practice pipeline with mandatory execution proofs.
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
    print("ACTUALLY ENTERING: create_verified_client")
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
            Provider(name="Dr. Sarah Martinez", specialty="Primary Care", priority=Priority.MUST_KEEP, visit_frequency=2),
            Provider(name="Dr. James Wilson", specialty="Cardiology", priority=Priority.MUST_KEEP, visit_frequency=2),
            Provider(name="Dr. Emily Chen", specialty="Dermatology", priority=Priority.NICE_TO_KEEP, visit_frequency=1)
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
    print("REAL INPUTS: {}".format(client))
    return client

def main():
    print("ACTUALLY ENTERING: main")
    start_time = time.time()
    client = create_verified_client()

    print("Parsing healthcare plan documents...")
    parser = DocumentParser()
    documents_dir = Path(__file__).parent / "personal_documents"
    plans = parser.parse_batch(str(documents_dir))
    print("ACTUALLY RETURNING: {} plans parsed".format(len(plans)))
    if not plans:
        print("FAILURE: No plans were parsed. Make sure you have PDF/DOCX files in the directory.")
        return

    print("Successfully parsed {} plans:".format(len(plans)))
    for i, plan in enumerate(plans[:5], 1):
        print("   {}. {} ({}) - ${:.2f}/month".format(i, plan.marketing_name, plan.issuer, plan.monthly_premium))
    if len(plans) > 5:
        print("   ... and {} more plans".format(len(plans) - 5))

    print("Analyzing plans with 6-metric scoring system...")
    engine = AnalysisEngine()
    report = engine.analyze_plans(client, plans)
    print("ACTUALLY RETURNING: Analysis report with {} plan analyses".format(len(report.plan_analyses)))

    print("Generating reports...")
    report_gen = ReportGenerator("./reports")
    summary_file = Path("./reports") / "executive_summary_{}.md".format(report.generated_at.strftime('%Y%m%d_%H%M%S'))
    summary = report_gen.generate_executive_summary(report)
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    print("ACTUALLY RETURNING: Executive summary written to {}".format(summary_file))

    csv_file = report_gen.generate_scoring_matrix_csv(report)
    json_file = report_gen.generate_json_export(report)
    html_file = report_gen.generate_html_dashboard(report)
    print("ACTUALLY RETURNING: CSV: {}, JSON: {}, HTML: {}".format(csv_file, json_file, html_file))

    print("SCORING MATRIX PREVIEW:")
    print("-" * 100)
    print("{:<4} {:<30} {:<8} {:<8} {:<10} {:<6} {:<12}".format('Rank', 'Plan Name', 'Score', 'Provider', 'Medication', 'Cost', 'Annual Cost'))
    print("-" * 100)
    for i, analysis in enumerate(report.plan_analyses[:10], 1):
        name = analysis.plan.marketing_name[:28] + ".." if len(analysis.plan.marketing_name) > 30 else analysis.plan.marketing_name
        print("{:<4} {:<30} {:>6.1f}/10 {:>6.1f}/10 {:>8.1f}/10 {:>4.1f}/10 ${:>10,.0f}".format(
            i, name, analysis.metrics.weighted_total_score, analysis.metrics.provider_network_score,
            analysis.metrics.medication_coverage_score, analysis.metrics.total_cost_score,
            analysis.estimated_annual_cost))
    print("-" * 100)

    print("RECOMMENDATION: Choose {}".format(report.top_recommendations[0].plan.marketing_name))
    print("   This plan scored {:.1f}/10 overall".format(report.top_recommendations[0].metrics.weighted_total_score))
    print("   Best balance of provider access, medication coverage, and cost")

    print("Demo complete! Check the './reports' directory for detailed analysis files.")
    end_time = time.time()
    print("TOTAL EXECUTION TIME: {:.2f} seconds".format(end_time - start_time))

if __name__ == "__main__":
    main()

        # Import here to avoid import errors if dependencies missing
        from examples.demo import main as demo_main
        
        print("\nStarting healthcare plan analysis demo...")
        print("This will:")
        print("- Load sample client profile")
        print("- Process healthcare plan documents")
        print("- Generate statistical analysis with 95% CI")
        print("- Create multi-format reports")
        print()
        
        # Run the demo
        demo_main()
        
        print("\n+ Demo completed successfully!")
        print("\nResults saved to:")
        print("- ./reports/ (all generated reports)")
        print("- ./gold_standard_report.json (compliance validation)")
        
    except ImportError as e:
        print(f"\n- Missing dependencies for demo: {e}")
        print("\nTry: pip install -r requirements.txt")
    except Exception as e:
        print(f"\n- Demo failed: {e}")
        print("\nCheck logs for details")

def analyze_documents():
    """Analyze user's healthcare documents"""
    print("\nANALYZE YOUR DOCUMENTS")
    print("=" * 40)
    
    print("\nDocument Analysis Options:")
    print("1. Process documents from personal_documents/ folder")
    print("2. Specify custom document path")
    print("3. Use live Healthcare.gov API data")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    try:
        if choice == "1":
            doc_path = project_root / "personal_documents"
            if not doc_path.exists():
                print(f"\n- Directory not found: {doc_path}")
                print("Create personal_documents/ and add your plan documents")
                return
        elif choice == "2":
            doc_path = input("Enter document directory path: ").strip()
            doc_path = Path(doc_path)
            if not doc_path.exists():
                print(f"\n Directory not found: {doc_path}")
                return
        elif choice == "3":
            print("\n Using live Healthcare.gov API data")
            zipcode = input("Enter your ZIP code: ").strip()
            if len(zipcode) != 5 or not zipcode.isdigit():
                print(" Invalid ZIP code. Please enter 5 digits.")
                return
            doc_path = None
        else:
            print(" Invalid choice")
            return
        
        # Import and run analyzer
        from healthplan_navigator.analyzer import HealthPlanAnalyzer
        from healthplan_navigator.core.models import Client, PersonalInfo
        
        print("\n Initializing analyzer with statistical validation...")
        analyzer = HealthPlanAnalyzer(confidence_level=0.95)
        
        if choice == "3":
            print(f"\n Fetching plans for ZIP code: {zipcode}")
            # Would implement API fetching here
            print(" Live API integration requires configuration")
            print("Use documents for now, or check MCP integration")
        else:
            print(f"\n Processing documents from: {doc_path}")
            print(" Document processing requires client profile setup")
            print("Use demo mode for complete example")
        
    except ImportError as e:
        print(f"\n Import error: {e}")
        print("Ensure all dependencies are installed")
    except Exception as e:
        print(f"\n Analysis failed: {e}")

def run_claude_mcp():
    """Run Claude Code + MCP integration"""
    print("\n CLAUDE CODE + MCP INTEGRATION")
    print("=" * 45)
    
    print("\nThis mode uses:")
    print(" Local MCP servers for document extraction")
    print(" Claude Code for AI analysis (free with Max plan)")
    print(" Statistical validation with confidence intervals")
    print()
    
    # Check MCP configuration
    mcp_config = project_root / ".mcp.json"
    if not mcp_config.exists():
        print(" MCP configuration not found")
        print("\nTo set up MCP integration:")
        print("1. Install MCP dependencies: pip install mcp")
        print("2. Configure servers in Claude Code:")
        print("   claude mcp add --scope project docling uvx -- --from=docling-mcp docling-mcp-server --transport stdio")
        print("   claude mcp add --scope project pymupdf4llm uvx -- pymupdf4llm-mcp@latest stdio")
        print("   claude mcp add --scope project chroma uvx -- chroma-mcp --client-type persistent --data-dir ./vectors")
        print("3. Verify in Claude Code: /mcp")
        return
    
    print(" MCP configuration found")
    print("\nNext steps:")
    print("1. Open Claude Code in this directory")
    print("2. Run /mcp to verify server connections")
    print("3. Process documents through Claude Code interface")
    print("4. Results will include statistical validation")
    
    print("\n Workspace structure:")
    workspace = project_root / "claude_workspace"
    if workspace.exists():
        print(f" {workspace}")
        for subdir in ["queue", "results", "processed"]:
            subdir_path = workspace / subdir
            status = "" if subdir_path.exists() else ""
            print(f"{status} {subdir_path}")
    else:
        print(f" Workspace not found: {workspace}")
        print("Run: python setup_workspace.py")

def run_statistical_validation():
    """Run gold standard statistical validation"""
    print("\n STATISTICAL VALIDATION")
    print("=" * 35)
    
    try:
        from tests.test_gold_standard import generate_gold_standard_report
        
        print("\nRunning comprehensive validation suite...")
        print("This will test:")
        print("- Statistical rigor (confidence intervals, hypothesis testing)")
        print("- Scoring validation (distribution, outliers)")
        print("- MCP configuration (servers, workspace)")
        print("- Data quality framework (power, uncertainty)")
        print()
        
        print(" Running tests...")
        report = generate_gold_standard_report()
        
        print(f"\n Validation Status: {report['overall_status']}")
        
        if report['overall_status'] == 'GOLD_STANDARD_COMPLIANT':
            print(" CONGRATULATIONS! Pipeline meets gold standards")
        else:
            print(" Improvements needed for full compliance")
            if report['recommendations']:
                print("\nRecommendations:")
                for i, rec in enumerate(report['recommendations'], 1):
                    print(f"  {i}. {rec}")
        
        print(f"\n📄 Full report saved: gold_standard_report.json")
        
    except ImportError as e:
        print(f"\n Missing dependencies: {e}")
        print("Install with: pip install -r requirements-dev.txt")
    except Exception as e:
        print(f"\n Validation failed: {e}")

def launch_cli():
    """Launch CLI interface"""
    print("\n LAUNCHING CLI INTERFACE")
    print("=" * 35)
    
    try:
        from healthplan_navigator.cli import main as cli_main
        cli_main()
    except ImportError as e:
        print(f"\n CLI not available: {e}")
        print("CLI module needs to be implemented")
    except Exception as e:
        print(f"\n CLI failed: {e}")

def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(
        description="HealthPlan Navigator - Gold Standard Healthcare Analytics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py               Interactive menu
  python main.py --demo        Run demonstration
  python main.py --claude      Claude Code integration
  python main.py --validate    Statistical validation
  python main.py --cli         Command line interface
        """
    )
    
    parser.add_argument('--demo', action='store_true', 
                       help='Run demo with sample data')
    parser.add_argument('--claude', action='store_true',
                       help='Use Claude Code + MCP integration')
    parser.add_argument('--validate', action='store_true',
                       help='Run statistical validation tests')
    parser.add_argument('--cli', action='store_true',
                       help='Launch CLI interface')
    parser.add_argument('--version', action='version', version='HealthPlan Navigator v1.1.3')
    
    args = parser.parse_args()
    
    # Handle command line arguments
    if args.demo:
        show_welcome()
        run_demo()
        return
    elif args.claude:
        show_welcome()
        run_claude_mcp()
        return  
    elif args.validate:
        show_welcome()
        run_statistical_validation()
        return
    elif args.cli:
        show_welcome()
        launch_cli()
        return
    
    # Interactive menu mode
    show_welcome()
    
    while True:
        show_menu()
        
        try:
            choice = input("Enter your choice (0-5): ").strip()
            
            if choice == '0':
                print("\n Thank you for using HealthPlan Navigator!")
                print("For support: https://github.com/your-org/healthplan-navigator/issues")
                break
            elif choice == '1':
                run_demo()
            elif choice == '2':
                analyze_documents()
            elif choice == '3':
                run_claude_mcp()
            elif choice == '4':
                run_statistical_validation()
            elif choice == '5':
                launch_cli()
            else:
                print(" Invalid choice. Please select 0-5.")
            
            # Wait for user before showing menu again
            if choice != '0':
                input("\nPress Enter to continue...")
                print("\n" + "="*70 + "\n")
                
        except KeyboardInterrupt:
            print("\n\n Goodbye!")
            break
        except Exception as e:
            print(f"\n Unexpected error: {e}")
            print("Please report this issue on GitHub")

if __name__ == "__main__":
    main()