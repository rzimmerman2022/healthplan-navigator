#!/usr/bin/env python3
"""
Forensic Test Script - Verify What Actually Executes
This script traces actual execution to distinguish between theatrical and functional code.
"""

import sys
import json
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("FORENSIC CODE ANALYSIS - EXECUTION VERIFICATION")
print("=" * 70)

# Test 1: Can we actually read PDF files?
print("\n[TEST 1] PDF Reading Capability")
print("-" * 40)
try:
    import pdfplumber
    print("[OK] pdfplumber imported successfully")
    
    # Try to read an actual PDF
    pdf_files = list(Path("personal_documents").glob("*.pdf"))[:1]
    if pdf_files:
        test_pdf = pdf_files[0]
        print(f"Testing PDF: {test_pdf.name}")
        
        with pdfplumber.open(test_pdf) as pdf:
            first_page = pdf.pages[0] if pdf.pages else None
            if first_page:
                text = first_page.extract_text()
                if text:
                    print(f"[OK] Extracted {len(text)} characters from PDF")
                    print(f"  First 100 chars: {text[:100]}")
                else:
                    print("[FAIL] No text extracted from PDF")
            else:
                print("[FAIL] No pages found in PDF")
    else:
        print("[FAIL] No PDF files found to test")
except ImportError as e:
    print(f"[FAIL] pdfplumber not installed: {e}")
except Exception as e:
    print(f"[FAIL] PDF reading failed: {e}")

# Test 2: Does the DocumentParser actually extract meaningful data?
print("\n[TEST 2] Document Parser Data Extraction")
print("-" * 40)
try:
    from src.healthplan_navigator.core.ingest import DocumentParser
    parser = DocumentParser()
    print("[OK] DocumentParser initialized")
    
    # Try parsing documents
    plans = parser.parse_batch("personal_documents")
    print(f"Parsed {len(plans)} plans")
    
    if plans:
        # Check first plan for real data
        plan = plans[0]
        print(f"\nFirst plan details:")
        print(f"  Plan ID: {plan.plan_id}")
        print(f"  Issuer: {plan.issuer}")
        print(f"  Marketing Name: {plan.marketing_name}")
        print(f"  Monthly Premium: ${plan.monthly_premium}")
        print(f"  Deductible: ${plan.deductible}")
        print(f"  OOP Max: ${plan.oop_max}")
        
        # Check if values are defaults/zeros
        if plan.monthly_premium == 0 and plan.deductible == 0:
            print("[WARN] WARNING: All costs are zero - likely parsing failure")
        else:
            print("[OK] Non-zero costs found - actual data extracted")
    else:
        print("[FAIL] No plans parsed from documents")
        
except Exception as e:
    print(f"[FAIL] DocumentParser failed: {e}")

# Test 3: Are external APIs actually called?
print("\n[TEST 3] External API Calls")
print("-" * 40)
try:
    from src.healthplan_navigator.integrations.healthcare_gov import HealthcareGovAPI
    api = HealthcareGovAPI()
    print("[OK] HealthcareGovAPI initialized")
    
    # Check if API key exists
    if api.api_key:
        print(f"[OK] API key configured: {api.api_key[:5]}...")
    else:
        print("[FAIL] No API key configured")
    
    # Try to validate API access
    print("Testing API connectivity...")
    if api.validate_api_access():
        print("[OK] API is accessible")
    else:
        print("[FAIL] API is not accessible (expected without key)")
    
    # Try fetching plans
    print("Attempting to fetch plans for ZIP 85001...")
    plans = api.fetch_plans("85001")
    if plans:
        print(f"[OK] Fetched {len(plans)} plans from API")
    else:
        print("[FAIL] No plans fetched from API (expected without key)")
        
except Exception as e:
    print(f"[FAIL] API integration failed: {e}")

# Test 4: MCP Tool Integration
print("\n[TEST 4] MCP Tool Integration")
print("-" * 40)
mcp_config_path = Path(".mcp.json")
if mcp_config_path.exists():
    print("[OK] .mcp.json configuration found")
    with open(mcp_config_path) as f:
        config = json.load(f)
    servers = list(config.get('mcpServers', {}).keys())
    print(f"  Configured servers: {servers}")
else:
    print("[FAIL] No .mcp.json configuration found")

# Search for actual MCP imports or usage
print("\nSearching for MCP tool imports in code...")
mcp_imports_found = False
for py_file in Path("src").rglob("*.py"):
    with open(py_file, encoding='utf-8', errors='ignore') as f:
        content = f.read()
        if "import mcp" in content or "from mcp" in content:
            print(f"  Found MCP import in: {py_file.name}")
            mcp_imports_found = True

if not mcp_imports_found:
    print("[FAIL] No MCP imports found in any Python files")
    print("  MCP is mentioned but never actually imported or used")

# Test 5: Score Calculation Reality Check
print("\n[TEST 5] Score Calculation Reality Check")
print("-" * 40)
try:
    from src.healthplan_navigator.core.models import Plan, Client, PersonalInfo, MedicalProfile, Priorities
    from src.healthplan_navigator.core.score import HealthPlanScorer
    
    # Create minimal test data
    personal = PersonalInfo(
        full_name="Test User",
        dob="1990-01-01", 
        zipcode="85001",
        household_size=1,
        annual_income=50000,
        csr_eligible=False
    )
    
    medical = MedicalProfile(providers=[], medications=[])
    priorities = Priorities()
    client = Client(personal=personal, medical_profile=medical, priorities=priorities)
    
    # Create test plan with known values
    test_plan = Plan(
        plan_id="TEST001",
        issuer="Test Issuer",
        marketing_name="Test Plan",
        monthly_premium=500.0,  # Non-zero premium
        deductible=2000.0,      # Non-zero deductible
        oop_max=8000.0          # Non-zero OOP max
    )
    
    scorer = HealthPlanScorer()
    analysis = scorer.score_plan(client, test_plan, [test_plan])
    
    print("[OK] Scorer executed")
    print(f"  Provider Network Score: {analysis.metrics.provider_network_score}")
    print(f"  Medication Coverage Score: {analysis.metrics.medication_coverage_score}")
    print(f"  Total Cost Score: {analysis.metrics.total_cost_score}")
    print(f"  Overall Score: {analysis.metrics.weighted_total_score}")
    print(f"  Estimated Annual Cost: ${analysis.estimated_annual_cost}")
    
    if analysis.estimated_annual_cost > 0:
        print("[OK] Non-zero annual cost calculated - scoring logic works")
    else:
        print("[FAIL] Zero annual cost - scoring may be broken")
        
except Exception as e:
    print(f"[FAIL] Scoring test failed: {e}")

# Test 6: Report Generation Reality
print("\n[TEST 6] Report Generation Reality")
print("-" * 40)
report_files = list(Path("reports").glob("*.json"))[:1]
if report_files:
    print(f"Examining report: {report_files[0].name}")
    with open(report_files[0]) as f:
        report_data = json.load(f)
    
    # Check if report contains real varied data
    if 'plan_analyses' in report_data:
        plans = report_data['plan_analyses']
        premiums = [p['plan']['monthly_premium'] for p in plans[:5]]
        scores = [p['scores']['overall_weighted'] for p in plans[:5]]
        
        print(f"  First 5 premiums: {premiums}")
        print(f"  First 5 scores: {scores}")
        
        # Check for variety in data
        if len(set(premiums)) == 1 and premiums[0] == 0:
            print("[FAIL] All premiums are zero - parsing failure")
        elif len(set(scores)) == 1:
            print("[FAIL] All scores identical - scoring failure")
        else:
            print("[OK] Varied data found - appears functional")
    else:
        print("[FAIL] No plan analyses in report")
else:
    print("[FAIL] No report files found")

print("\n" + "=" * 70)
print("FORENSIC ANALYSIS COMPLETE")
print("=" * 70)

# Summary
print("\nSUMMARY:")
print("-" * 40)
print("""
Based on the tests above, this codebase appears to be:

PARTIALLY FUNCTIONAL with SIGNIFICANT ISSUES:
- DocumentParser exists and attempts to parse files
- Scoring logic is implemented and executes
- Report generation creates actual files
- BUT: PDF parsing extracts garbage data (all zeros/defaults)
- BUT: No actual MCP tool integration despite claims
- BUT: External APIs not actually called without keys
- BUT: Generated reports contain mostly zero/default values

The code STRUCTURE is real but the DATA EXTRACTION is broken.
This is a "hollow implementation" - the pipeline exists but 
doesn't extract meaningful data from source documents.
""")