#!/usr/bin/env python3
"""
HealthPlan Navigator - Main Entry Point
Gold Standard Healthcare Analytics Pipeline

Interactive launcher for healthcare plan analysis with statistical rigor.
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

# Add src to Python path for development
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def show_welcome():
    """Display welcome message and system status"""
    print("=" * 70)
    print("🏥 HEALTHPLAN NAVIGATOR v1.1.2")
    print("Gold Standard Healthcare Analytics Pipeline")
    print("=" * 70)
    print()
    print("✅ Statistical Rigor: 95% confidence intervals")
    print("✅ AI Intelligence: Claude Code + MCP integration")
    print("✅ Mathematical Certainty: Monte Carlo simulations")
    print("✅ Zero Cost: Max plan + local processing")
    print()

def show_menu():
    """Display interactive menu options"""
    print("📋 SELECT AN OPTION:")
    print()
    print("1. 🚀 Run Demo with Sample Data")
    print("   - Process sample healthcare plans")
    print("   - Generate statistical reports")
    print("   - View confidence intervals")
    print()
    print("2. 📊 Analyze Your Documents")
    print("   - Process your healthcare plan documents")
    print("   - Generate personalized analysis")
    print("   - Export multi-format reports")
    print()
    print("3. 🧠 Claude Code + MCP Integration")
    print("   - Use AI intelligence for analysis")
    print("   - Process with local MCP servers")
    print("   - Generate insights with uncertainty quantification")
    print()
    print("4. 🔬 Run Statistical Validation")
    print("   - Verify gold standard compliance")
    print("   - Check statistical rigor")
    print("   - Generate compliance report")
    print()
    print("5. 💻 Launch CLI Interface")
    print("   - Command line tools")
    print("   - Batch processing")
    print("   - Advanced options")
    print()
    print("0. ❌ Exit")
    print()

def run_demo():
    """Run demonstration with sample data"""
    print("\n🚀 RUNNING DEMO WITH SAMPLE DATA")
    print("=" * 50)
    
    try:
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
        
        print("\n✅ Demo completed successfully!")
        print("\nResults saved to:")
        print("- ./reports/ (all generated reports)")
        print("- ./gold_standard_report.json (compliance validation)")
        
    except ImportError as e:
        print(f"\n❌ Missing dependencies for demo: {e}")
        print("\nTry: pip install -r requirements.txt")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("\nCheck logs for details")

def analyze_documents():
    """Analyze user's healthcare documents"""
    print("\n📊 ANALYZE YOUR DOCUMENTS")
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
                print(f"\n❌ Directory not found: {doc_path}")
                print("Create personal_documents/ and add your plan documents")
                return
        elif choice == "2":
            doc_path = input("Enter document directory path: ").strip()
            doc_path = Path(doc_path)
            if not doc_path.exists():
                print(f"\n❌ Directory not found: {doc_path}")
                return
        elif choice == "3":
            print("\n🌐 Using live Healthcare.gov API data")
            zipcode = input("Enter your ZIP code: ").strip()
            if len(zipcode) != 5 or not zipcode.isdigit():
                print("❌ Invalid ZIP code. Please enter 5 digits.")
                return
            doc_path = None
        else:
            print("❌ Invalid choice")
            return
        
        # Import and run analyzer
        from healthplan_navigator.analyzer import HealthPlanAnalyzer
        from healthplan_navigator.core.models import Client, PersonalInfo
        
        print("\n🔄 Initializing analyzer with statistical validation...")
        analyzer = HealthPlanAnalyzer(confidence_level=0.95)
        
        if choice == "3":
            print(f"\n🌐 Fetching plans for ZIP code: {zipcode}")
            # Would implement API fetching here
            print("❌ Live API integration requires configuration")
            print("Use documents for now, or check MCP integration")
        else:
            print(f"\n📁 Processing documents from: {doc_path}")
            print("❌ Document processing requires client profile setup")
            print("Use demo mode for complete example")
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("Ensure all dependencies are installed")
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")

def run_claude_mcp():
    """Run Claude Code + MCP integration"""
    print("\n🧠 CLAUDE CODE + MCP INTEGRATION")
    print("=" * 45)
    
    print("\nThis mode uses:")
    print("✅ Local MCP servers for document extraction")
    print("✅ Claude Code for AI analysis (free with Max plan)")
    print("✅ Statistical validation with confidence intervals")
    print()
    
    # Check MCP configuration
    mcp_config = project_root / ".mcp.json"
    if not mcp_config.exists():
        print("❌ MCP configuration not found")
        print("\nTo set up MCP integration:")
        print("1. Install MCP dependencies: pip install mcp")
        print("2. Configure servers in Claude Code:")
        print("   claude mcp add --scope project docling uvx -- --from=docling-mcp docling-mcp-server --transport stdio")
        print("   claude mcp add --scope project pymupdf4llm uvx -- pymupdf4llm-mcp@latest stdio")
        print("   claude mcp add --scope project chroma uvx -- chroma-mcp --client-type persistent --data-dir ./vectors")
        print("3. Verify in Claude Code: /mcp")
        return
    
    print("✅ MCP configuration found")
    print("\nNext steps:")
    print("1. Open Claude Code in this directory")
    print("2. Run /mcp to verify server connections")
    print("3. Process documents through Claude Code interface")
    print("4. Results will include statistical validation")
    
    print("\n📁 Workspace structure:")
    workspace = project_root / "claude_workspace"
    if workspace.exists():
        print(f"✅ {workspace}")
        for subdir in ["queue", "results", "processed"]:
            subdir_path = workspace / subdir
            status = "✅" if subdir_path.exists() else "❌"
            print(f"{status} {subdir_path}")
    else:
        print(f"❌ Workspace not found: {workspace}")
        print("Run: python setup_workspace.py")

def run_statistical_validation():
    """Run gold standard statistical validation"""
    print("\n🔬 STATISTICAL VALIDATION")
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
        
        print("🔄 Running tests...")
        report = generate_gold_standard_report()
        
        print(f"\n📊 Validation Status: {report['overall_status']}")
        
        if report['overall_status'] == 'GOLD_STANDARD_COMPLIANT':
            print("🏆 CONGRATULATIONS! Pipeline meets gold standards")
        else:
            print("⚠️ Improvements needed for full compliance")
            if report['recommendations']:
                print("\nRecommendations:")
                for i, rec in enumerate(report['recommendations'], 1):
                    print(f"  {i}. {rec}")
        
        print(f"\n📄 Full report saved: gold_standard_report.json")
        
    except ImportError as e:
        print(f"\n❌ Missing dependencies: {e}")
        print("Install with: pip install -r requirements-dev.txt")
    except Exception as e:
        print(f"\n❌ Validation failed: {e}")

def launch_cli():
    """Launch CLI interface"""
    print("\n💻 LAUNCHING CLI INTERFACE")
    print("=" * 35)
    
    try:
        from healthplan_navigator.cli import main as cli_main
        cli_main()
    except ImportError as e:
        print(f"\n❌ CLI not available: {e}")
        print("CLI module needs to be implemented")
    except Exception as e:
        print(f"\n❌ CLI failed: {e}")

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
    parser.add_argument('--version', action='version', version='HealthPlan Navigator v1.1.2')
    
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
                print("\n👋 Thank you for using HealthPlan Navigator!")
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
                print("❌ Invalid choice. Please select 0-5.")
            
            # Wait for user before showing menu again
            if choice != '0':
                input("\nPress Enter to continue...")
                print("\n" + "="*70 + "\n")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            print("Please report this issue on GitHub")

if __name__ == "__main__":
    main()