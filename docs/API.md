# HealthPlan Navigator API Reference v1.1.0

## 📚 Table of Contents
1. [Overview](#overview)
2. [Core Architecture](#core-architecture)
3. [API Modules](#api-modules)
   - [analyzer](#healthplan_navigatoranalyzer)
   - [core.models](#healthplan_navigatorcoremodels)
   - [core.ingest](#healthplan_navigatorcoreingest)
   - [core.score](#healthplan_navigatorcorescore)
   - [analysis.engine](#healthplan_navigatoranalysisengine)
   - [integrations](#healthplan_navigatorintegrations)
   - [output.report](#healthplan_navigatoroutputreport)
4. [Data Types & Enums](#data-types--enums)
5. [Usage Examples](#usage-examples)
6. [Error Handling](#error-handling)
7. [Extension Guide](#extension-guide)
8. [Performance Optimization](#performance-optimization)
9. [API Integration Patterns](#api-integration-patterns)

## Overview

The HealthPlan Navigator API v1.1.0 provides a comprehensive programmatic interface for healthcare plan analysis with **live API integration capabilities**. This document details every class, method, data structure, and integration point available for developers and AI coding assistants.

### 🚀 New in v1.1.0
- **Unified HealthPlanAnalyzer Interface**: Single entry point for all functionality
- **Live API Integrations**: Healthcare.gov, NPPES, RxNorm, GoodRx
- **Enhanced Provider Matching**: Fuzzy string matching algorithms
- **Medication Intelligence**: Generic alternatives and pricing
- **Production Infrastructure**: Caching, rate limiting, error handling

### Package Structure
```
healthplan_navigator/
├── __init__.py                    # Package exports and version info
├── analyzer.py                    # NEW: Unified orchestrator interface
├── core/                          # Core functionality and models
│   ├── __init__.py               # Core module exports
│   ├── models.py                 # Data models and structures
│   ├── ingest.py                 # Document parsing engines
│   └── score.py                  # Scoring algorithms
├── analysis/                      # Analysis engine
│   ├── __init__.py               # Analysis exports
│   └── engine.py                 # Orchestration logic
├── integrations/                  # NEW: External API integrations
│   ├── __init__.py               # Integration exports
│   ├── healthcare_gov.py         # Healthcare.gov marketplace API
│   ├── providers.py              # NPPES provider registry
│   └── medications.py            # RxNorm and GoodRx APIs
├── output/                        # Report generation
│   ├── __init__.py               # Output exports
│   └── report.py                 # Multi-format generators
└── cli.py                        # Command-line interface
```

## Core Architecture

### Design Principles
- **Type Safety**: Extensive use of Python dataclasses and type hints
- **Immutability**: Data models are immutable where possible
- **Separation of Concerns**: Clear module boundaries
- **Extensibility**: Easy to add new parsers, scorers, and integrations
- **Error Resilience**: Graceful degradation with fallbacks
- **Performance**: Caching and parallel processing capabilities

### Data Flow
```
[Client Profile] → [Document/API Ingestion] → [Scoring Engine] → [Analysis] → [Reports]
       ↓                    ↓                       ↓                ↓            ↓
   Personal Info      Local Files or           6-Metric Scores   Ranking    Multiple Formats
   Medical Profile    Live API Data            Normalization     Insights   MD/CSV/JSON/HTML
   Priorities         Parsing/Transform        Weighting         Warnings   Visualizations
```

## API Modules

### `healthplan_navigator.analyzer`
**NEW in v1.1.0** - Unified orchestration interface combining all functionality.

#### Class: `HealthPlanAnalyzer`
Main orchestrator providing a single interface for the complete analysis pipeline.

```python
class HealthPlanAnalyzer:
    """
    Unified orchestrator for healthcare plan analysis with API integration.
    
    This class provides a single interface for:
    - Plan document ingestion (PDF, DOCX, JSON, CSV)
    - Live API data fetching (Healthcare.gov, NPPES, RxNorm)
    - Comprehensive scoring and ranking
    - Multi-format report generation
    
    Attributes:
        parser (DocumentParser): Document parsing engine
        engine (AnalysisEngine): Analysis orchestration
        report_generator (ReportGenerator): Report generation
        healthcare_gov_api (HealthcareGovAPI): Marketplace API client
        provider_integration (ProviderNetworkIntegration): NPPES integration
        medication_integration (MedicationIntegration): Drug API integration
    
    Example:
        >>> analyzer = HealthPlanAnalyzer(
        ...     api_keys={'healthcare_gov': 'KEY', 'goodrx': 'KEY'}
        ... )
        >>> report = analyzer.analyze(
        ...     client=client,
        ...     healthcare_gov_fetch=True,  # Use live API
        ...     formats=['summary', 'csv', 'json', 'html']
        ... )
    """
    
    def __init__(self, output_dir: str = "./reports", 
                 api_keys: Optional[Dict[str, str]] = None):
        """
        Initialize the HealthPlanAnalyzer with optional API keys.
        
        Args:
            output_dir: Directory for generated reports
            api_keys: Dictionary of API keys for various services
                - 'healthcare_gov': Healthcare.gov API key
                - 'nppes': NPPES API key (optional, public API)
                - 'goodrx': GoodRx API key
        
        Example:
            >>> analyzer = HealthPlanAnalyzer(
            ...     output_dir="./my_reports",
            ...     api_keys={'healthcare_gov': 'abc123'}
            ... )
        """
    
    def analyze(self, 
                client: Client,
                plan_sources: Optional[Union[str, List[str]]] = None,
                healthcare_gov_fetch: bool = False,
                formats: List[str] = None) -> AnalysisReport:
        """
        Run complete analysis pipeline with live API integration.
        
        Args:
            client: Client profile for analysis
            plan_sources: Path(s) to plan files or directory (optional)
            healthcare_gov_fetch: Whether to fetch plans from Healthcare.gov API
            formats: Report formats to generate ['summary', 'csv', 'json', 'html']
        
        Returns:
            AnalysisReport with all scored and ranked plans
        
        Example:
            >>> # Local document analysis
            >>> report = analyzer.analyze(
            ...     client=client,
            ...     plan_sources='./documents/',
            ...     formats=['summary', 'csv']
            ... )
            
            >>> # Live API analysis
            >>> report = analyzer.analyze(
            ...     client=client,
            ...     healthcare_gov_fetch=True,
            ...     formats=['all']
            ... )
        """
    
    def analyze_single_plan(self, client: Client, plan: Plan) -> Dict[str, Any]:
        """
        Analyze a single plan for quick assessment.
        
        Args:
            client: Client profile
            plan: Single plan to analyze
        
        Returns:
            Dictionary with plan analysis results including scores,
            estimated costs, strengths, and concerns
        """
    
    def get_scoring_matrix(self, report: AnalysisReport) -> List[Dict]:
        """
        Get scoring matrix for all analyzed plans.
        
        Returns:
            List of dictionaries with plan names and all metric scores
        """
    
    def get_comparison_summary(self, report: AnalysisReport) -> Dict:
        """
        Get comparison summary of analyzed plans.
        
        Returns:
            Dictionary with comparison data including best plans
            by category, key insights, and warnings
        """
```

### `healthplan_navigator.core.models`

Core data models using Python dataclasses for type safety.

#### Class: `Client`
Complete healthcare consumer profile.

```python
@dataclass
class Client:
    """
    Complete healthcare consumer profile combining personal, medical, and priority data.
    
    This is the primary input for plan analysis, containing all information
    needed to evaluate healthcare plans for an individual or family.
    
    Attributes:
        personal (PersonalInfo): Demographic and eligibility information
        medical_profile (MedicalProfile): Healthcare providers and medications
        priorities (Priorities): Decision-making priorities and preferences
    
    Class Methods:
        from_json(file_path): Load client from JSON file
        from_dict(data): Create client from dictionary
        validate(): Validate all client data
    
    Example:
        >>> client = Client(
        ...     personal=PersonalInfo(
        ...         full_name="John Doe",
        ...         dob="1980-01-15",
        ...         zipcode="85001",
        ...         household_size=2,
        ...         annual_income=75000,
        ...         csr_eligible=False
        ...     ),
        ...     medical_profile=MedicalProfile(
        ...         providers=[...],
        ...         medications=[...],
        ...         special_treatments=[]
        ...     ),
        ...     priorities=Priorities(
        ...         keep_providers=5,
        ...         minimize_total_cost=4
        ...     )
        ... )
    """
    personal: PersonalInfo
    medical_profile: MedicalProfile
    priorities: Priorities
    
    def validate(self) -> List[str]:
        """
        Validate client data and return list of validation errors.
        
        Returns:
            List of validation error messages (empty if valid)
        """
    
    def get_age(self) -> int:
        """Calculate current age from date of birth."""
    
    def get_fpl_percentage(self) -> float:
        """Calculate income as percentage of Federal Poverty Level."""
    
    def estimate_annual_utilization(self) -> Dict[str, int]:
        """
        Estimate annual healthcare utilization based on profile.
        
        Returns:
            Dictionary with estimated visits, procedures, and prescriptions
        """
```

#### Class: `Plan`
Healthcare insurance plan with comprehensive details.

```python
@dataclass
class Plan:
    """
    Healthcare insurance plan with all relevant details for analysis.
    
    Represents a complete health insurance plan including costs, coverage,
    network, formulary, and quality metrics. Supports both local document
    data and live API data.
    
    Attributes:
        plan_id (str): Unique plan identifier
        issuer (str): Insurance company name
        marketing_name (str): Plan marketing name
        plan_type (PlanType): HMO, PPO, EPO, POS, or HDHP
        metal_level (MetalLevel): Bronze, Silver, Gold, or Platinum
        monthly_premium (float): Monthly premium cost
        deductible (float): Individual deductible
        oop_max (float): Individual out-of-pocket maximum
        copay_primary (float): Primary care visit copay
        copay_specialist (float): Specialist visit copay
        copay_er (float): Emergency room copay
        coinsurance (float): Coinsurance percentage (0-1)
        provider_network (Optional[ProviderNetwork]): Network details
        drug_formulary (Optional[DrugFormulary]): Medication coverage
        quality_rating (float): CMS quality rating (0-5)
        customer_rating (float): Customer satisfaction rating (0-5)
    
    Methods:
        is_provider_in_network(provider): Check provider coverage
        get_medication_tier(medication): Get formulary tier
        estimate_annual_cost(client): Estimate total annual costs
        validate(): Validate plan data
    
    Example:
        >>> plan = Plan(
        ...     plan_id="12345-GOLD-HMO",
        ...     issuer="BlueCross BlueShield",
        ...     marketing_name="Gold HMO Select",
        ...     plan_type=PlanType.HMO,
        ...     metal_level=MetalLevel.GOLD,
        ...     monthly_premium=450.00,
        ...     deductible=1500.00,
        ...     oop_max=6000.00,
        ...     copay_primary=25.00,
        ...     copay_specialist=50.00,
        ...     copay_er=300.00,
        ...     coinsurance=0.20
        ... )
    """
```

### `healthplan_navigator.integrations`

**NEW in v1.1.0** - Live API integration modules.

#### Module: `healthcare_gov`
Healthcare.gov marketplace API integration.

```python
class HealthcareGovAPI:
    """
    Interface for Healthcare.gov marketplace API with fallback to CMS public data.
    
    Handles authentication, rate limiting, caching, and data transformation
    for fetching plan data from the federal marketplace. Includes automatic
    fallback to CMS public datasets when API keys are unavailable.
    
    Attributes:
        BASE_URL: Healthcare.gov API base URL
        CMS_QHP_URL: CMS public data endpoint (no auth required)
        session: Configured requests session with retry logic
        cache_dir: Directory for caching API responses
    
    Example:
        >>> api = HealthcareGovAPI(api_key="your_key")
        >>> plans = api.fetch_plans(
        ...     zipcode="85001",
        ...     metal_levels=["Silver", "Gold"],
        ...     plan_types=["HMO", "PPO"]
        ... )
    """
    
    def fetch_plans(self, 
                   zipcode: str,
                   county_fips: Optional[str] = None,
                   metal_levels: Optional[List[str]] = None,
                   plan_types: Optional[List[str]] = None,
                   year: Optional[int] = None) -> List[Plan]:
        """
        Fetch available plans for a given location.
        
        First attempts to use CMS public data (no auth required), then
        falls back to authenticated Healthcare.gov API if available.
        
        Args:
            zipcode: 5-digit ZIP code
            county_fips: County FIPS code for more accurate results
            metal_levels: Filter by metal levels
            plan_types: Filter by plan types
            year: Plan year (defaults to current year)
        
        Returns:
            List of Plan objects available in the specified area
        """
    
    def fetch_provider_network(self, plan_id: str) -> Optional[ProviderNetwork]:
        """
        Fetch provider network details for a specific plan.
        
        Args:
            plan_id: Healthcare.gov plan ID
        
        Returns:
            ProviderNetwork object or None if not available
        """
    
    def fetch_drug_formulary(self, plan_id: str) -> Optional[DrugFormulary]:
        """
        Fetch drug formulary for a specific plan.
        
        Args:
            plan_id: Healthcare.gov plan ID
        
        Returns:
            DrugFormulary object or None if not available
        """
    
    def validate_api_access(self) -> bool:
        """
        Validate API access and credentials.
        
        Returns:
            True if API is accessible (including public endpoints)
        """
```

#### Module: `providers`
NPPES provider registry integration with fuzzy matching.

```python
class ProviderNetworkIntegration:
    """
    Provider network validation using NPPES registry with fuzzy matching.
    
    Integrates with the National Provider Identifier (NPI) registry for
    real-time provider verification. Includes fuzzy string matching for
    handling name variations and geographic proximity analysis.
    
    Attributes:
        NPPES_API_URL: Public NPPES registry endpoint (no auth required)
        session: HTTP session for API calls
        provider_cache: Local cache of provider data
    
    Example:
        >>> provider_api = ProviderNetworkIntegration()
        >>> providers = provider_api.search_providers(
        ...     specialty="Cardiology",
        ...     location="85001",
        ...     radius_miles=25
        ... )
        >>> coverage = provider_api.calculate_network_coverage(
        ...     client_providers, network
        ... )
    """
    
    def search_providers(self, 
                        specialty: Optional[str] = None,
                        location: Optional[str] = None,
                        radius_miles: int = 25) -> List[Dict]:
        """
        Search NPPES registry for providers.
        
        Uses the public NPPES API to search for healthcare providers
        by specialty and location. No authentication required.
        
        Args:
            specialty: Medical specialty to search for
            location: ZIP code or city/state
            radius_miles: Search radius in miles
        
        Returns:
            List of provider dictionaries with NPI, name, specialty, address
        """
    
    def check_provider_in_network(self, 
                                  provider: Provider, 
                                  network: ProviderNetwork,
                                  fuzzy_match: bool = True) -> bool:
        """
        Check if a provider is in a specific network using fuzzy matching.
        
        Args:
            provider: Provider to check
            network: Network to search in
            fuzzy_match: Whether to use fuzzy string matching (85% threshold)
        
        Returns:
            True if provider is found in network
        """
    
    def calculate_network_coverage(self, 
                                   client_providers: List[Provider],
                                   network: ProviderNetwork) -> Dict[str, Any]:
        """
        Calculate comprehensive network coverage statistics.
        
        Args:
            client_providers: Client's current providers
            network: Network to evaluate
        
        Returns:
            Dictionary with coverage percentages, must-keep coverage,
            and provider-by-provider breakdown
        """
    
    def estimate_network_size(self, network: ProviderNetwork) -> str:
        """
        Estimate the size/breadth of a provider network.
        
        Returns:
            'Large', 'Medium', 'Small', or 'Unknown'
        """
```

#### Module: `medications`
RxNorm drug database and GoodRx pricing integration.

```python
class MedicationIntegration:
    """
    Medication analysis using RxNorm database and pricing APIs.
    
    Integrates with RxNorm for drug information and generic alternatives,
    and GoodRx for pricing (when API key available). Includes formulary
    checking and annual cost calculations.
    
    Attributes:
        RXNORM_API_URL: Public RxNorm API endpoint (no auth required)
        OPENFDA_API_URL: Public FDA drug database endpoint
        goodrx_api_key: Optional GoodRx API key for pricing
        drug_cache: Local cache of drug information
        price_cache: Local cache of pricing data
    
    Example:
        >>> med_api = MedicationIntegration(goodrx_api_key="key")
        >>> alternatives = med_api.find_generic_alternatives(medication)
        >>> coverage = med_api.check_medication_coverage(medication, formulary)
        >>> price = med_api.get_medication_price(medication, "85001")
    """
    
    def check_medication_coverage(self, 
                                  medication: Medication,
                                  formulary: DrugFormulary) -> Dict[str, Any]:
        """
        Check if a medication is covered by a formulary.
        
        Args:
            medication: Medication to check
            formulary: Plan's drug formulary
        
        Returns:
            Dictionary with coverage status, tier, copay, and restrictions
        """
    
    def find_generic_alternatives(self, medication: Medication) -> List[Dict[str, str]]:
        """
        Find generic alternatives using RxNorm API.
        
        Queries the public RxNorm database for generic equivalents
        and therapeutic alternatives.
        
        Args:
            medication: Brand medication
        
        Returns:
            List of generic alternatives with names, RxCUI codes,
            and potential savings estimates
        """
    
    def get_medication_price(self, 
                            medication: Medication,
                            zipcode: str,
                            quantity: int = 30) -> Dict[str, float]:
        """
        Get medication prices from various sources.
        
        Args:
            medication: Medication to price
            zipcode: Location for pricing
            quantity: Quantity (default 30-day supply)
        
        Returns:
            Dictionary with cash price, GoodRx price (if available),
            and insurance copay estimates by tier
        """
    
    def calculate_annual_medication_cost(self, 
                                        medications: List[Medication],
                                        formulary: DrugFormulary,
                                        plan_copays: Dict[str, float]) -> float:
        """
        Calculate estimated annual medication costs for a plan.
        
        Args:
            medications: List of client medications
            formulary: Plan's drug formulary
            plan_copays: Plan's copay structure by tier
        
        Returns:
            Estimated annual medication cost in USD
        """
```

### `healthplan_navigator.core.score`

Sophisticated 6-metric scoring system implementation.

#### Class: `HealthPlanScorer`
Implements weighted scoring across six key metrics.

```python
class HealthPlanScorer:
    """
    Healthcare plan scoring engine with configurable weights.
    
    Implements a sophisticated 6-metric scoring system where each
    metric is scored 0-10 and weighted to produce an overall score.
    Supports custom weights for different prioritization strategies.
    
    Default Weights:
        - Provider Network: 30%
        - Medication Coverage: 25%
        - Total Cost: 20%
        - Financial Protection: 10%
        - Administrative Simplicity: 10%
        - Plan Quality: 5%
    
    Example:
        >>> # Default scorer
        >>> scorer = HealthPlanScorer()
        
        >>> # Custom weights emphasizing providers
        >>> custom_weights = {
        ...     'provider_network': 0.40,
        ...     'medication_coverage': 0.20,
        ...     'total_cost': 0.20,
        ...     'financial_protection': 0.10,
        ...     'administrative_simplicity': 0.05,
        ...     'plan_quality': 0.05
        ... }
        >>> scorer = HealthPlanScorer(weights=custom_weights)
    """
    
    def score_plan(self, client: Client, plan: Plan, 
                   all_plans: List[Plan]) -> PlanAnalysis:
        """
        Score a single plan for a client with detailed analysis.
        
        Performs comprehensive scoring across all metrics, calculates
        weighted total, identifies strengths and concerns, and estimates
        total annual costs.
        
        Args:
            client: Client profile with requirements
            plan: Plan to score
            all_plans: All plans for cost normalization
        
        Returns:
            PlanAnalysis with scores, cost breakdown, and insights
        """
```

## Data Types & Enums

### Enumerations

```python
from enum import Enum

class MetalLevel(Enum):
    """Health plan metal levels per ACA standards."""
    BRONZE = "Bronze"
    SILVER = "Silver"
    GOLD = "Gold"
    PLATINUM = "Platinum"
    CATASTROPHIC = "Catastrophic"

class PlanType(Enum):
    """Health plan network types."""
    HMO = "HMO"  # Health Maintenance Organization
    PPO = "PPO"  # Preferred Provider Organization
    EPO = "EPO"  # Exclusive Provider Organization
    POS = "POS"  # Point of Service
    HDHP = "HDHP"  # High Deductible Health Plan

class Priority(Enum):
    """Provider priority levels for network analysis."""
    MUST_KEEP = "must-keep"
    NICE_TO_KEEP = "nice-to-keep"
    OPTIONAL = "optional"
```

### Type Aliases

```python
from typing import TypeAlias

# Identifiers
PlanID: TypeAlias = str
ProviderNPI: TypeAlias = str
DrugRxCUI: TypeAlias = str

# Scoring
Score: TypeAlias = float  # 0.0 to 10.0
Weight: TypeAlias = float  # 0.0 to 1.0

# Financial
Money: TypeAlias = float  # USD amount
Percentage: TypeAlias = float  # 0.0 to 1.0
```

## Usage Examples

### Example 1: Complete Analysis with Live API Data

```python
from healthplan_navigator.analyzer import HealthPlanAnalyzer
from healthplan_navigator.core.models import Client, PersonalInfo, MedicalProfile, Priorities, Provider, Medication, Priority

# Create comprehensive client profile
personal = PersonalInfo(
    full_name="Jane Smith",
    dob="1978-06-15",
    zipcode="85001",
    household_size=3,
    annual_income=85000,
    csr_eligible=False
)

medical = MedicalProfile(
    providers=[
        Provider(
            name="Dr. Sarah Chen, MD",
            specialty="Primary Care",
            priority=Priority.MUST_KEEP,
            visit_frequency=4
        ),
        Provider(
            name="Dr. Michael Rodriguez, MD", 
            specialty="Cardiology",
            priority=Priority.MUST_KEEP,
            visit_frequency=2
        )
    ],
    medications=[
        Medication(
            name="Metformin",
            dosage="500mg",
            frequency="Twice daily",
            annual_doses=730
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
    keep_providers=5,  # Highest priority
    minimize_total_cost=4,
    predictable_costs=3,
    avoid_prior_auth=4,
    simple_admin=3
)

client = Client(personal=personal, medical_profile=medical, priorities=priorities)

# Initialize analyzer with API keys
analyzer = HealthPlanAnalyzer(
    output_dir="./analysis_results",
    api_keys={
        'healthcare_gov': 'your_api_key',  # Optional
        'goodrx': 'your_goodrx_key'  # Optional
    }
)

# Run analysis with live API data
report = analyzer.analyze(
    client=client,
    healthcare_gov_fetch=True,  # Fetch from Healthcare.gov
    formats=['summary', 'csv', 'json', 'html']
)

# Access results
print(f"Analyzed {len(report.plan_analyses)} plans")
print(f"Top recommendation: {report.plan_analyses[0].plan.marketing_name}")
print(f"Score: {report.plan_analyses[0].metrics.weighted_total_score:.1f}/10")
print(f"Estimated annual cost: ${report.plan_analyses[0].estimated_annual_cost:,.0f}")

# Check provider coverage
top_plan = report.plan_analyses[0]
for provider in client.medical_profile.providers:
    in_network = top_plan.plan.provider_network and \
                 any(provider.name in p for p in top_plan.plan.provider_network.providers)
    print(f"{provider.name}: {'✅ In-Network' if in_network else '❌ Out-of-Network'}")
```

### Example 2: API Integration Testing

```python
from healthplan_navigator.analyzer import HealthPlanAnalyzer

# Test API connectivity
analyzer = HealthPlanAnalyzer()

print("API Integration Status:")
print("-" * 40)

# Healthcare.gov API
hc_status = analyzer.healthcare_gov_api.validate_api_access()
print(f"Healthcare.gov: {'✅ Connected' if hc_status else '🔑 API Key Required'}")

# Test provider search (NPPES - public API)
providers = analyzer.provider_integration.search_providers(
    specialty="Primary Care",
    location="85001"
)
print(f"NPPES Registry: ✅ Found {len(providers)} providers")

# Test medication lookup (RxNorm - public API)
from healthplan_navigator.core.models import Medication
med = Medication(name="Lipitor", dosage="20mg", frequency="Daily", annual_doses=365)
alternatives = analyzer.medication_integration.find_generic_alternatives(med)
print(f"RxNorm Database: ✅ Found {len(alternatives)} alternatives")

# Test with fallback data
print("\nFallback Mechanisms:")
plans = analyzer.healthcare_gov_api.fetch_plans(zipcode="85001")
print(f"CMS Public Data: {'✅ Available' if plans else '❌ Not Available'}")
```

### Example 3: Custom Scoring Strategy

```python
from healthplan_navigator.analyzer import HealthPlanAnalyzer
from healthplan_navigator.core.score import HealthPlanScorer

# Create scorer with custom weights for cost-conscious analysis
cost_focused_weights = {
    'provider_network': 0.20,      # Reduced from 0.30
    'medication_coverage': 0.20,   # Reduced from 0.25
    'total_cost': 0.35,           # Increased from 0.20
    'financial_protection': 0.15,  # Increased from 0.10
    'administrative_simplicity': 0.05,  # Reduced from 0.10
    'plan_quality': 0.05          # Same
}

# Validate weights sum to 1.0
assert abs(sum(cost_focused_weights.values()) - 1.0) < 0.001

# Create custom scorer
custom_scorer = HealthPlanScorer(weights=cost_focused_weights)

# Use in analysis
analyzer = HealthPlanAnalyzer()
analyzer.engine.scorer = custom_scorer

# Run analysis with cost focus
report = analyzer.analyze(
    client=client,
    plan_sources="./documents/",
    formats=['summary']
)

print("Cost-Focused Analysis Results:")
for i, analysis in enumerate(report.plan_analyses[:3], 1):
    print(f"{i}. {analysis.plan.marketing_name}")
    print(f"   Cost Score: {analysis.metrics.total_cost_score:.1f}/10")
    print(f"   Annual Cost: ${analysis.estimated_annual_cost:,.0f}")
```

### Example 4: Batch Processing with Parallel Execution

```python
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import json

def analyze_client_profile(client_file: str, output_dir: str):
    """Analyze plans for a single client."""
    from healthplan_navigator.analyzer import HealthPlanAnalyzer
    from healthplan_navigator.core.models import Client
    
    # Load client
    with open(client_file, 'r') as f:
        client_data = json.load(f)
    client = Client.from_dict(client_data['client'])
    
    # Initialize analyzer
    analyzer = HealthPlanAnalyzer(output_dir=output_dir)
    
    # Run analysis with API data
    report = analyzer.analyze(
        client=client,
        healthcare_gov_fetch=True,
        formats=['summary', 'csv']
    )
    
    return {
        'client': Path(client_file).stem,
        'plans_analyzed': len(report.plan_analyses),
        'top_plan': report.plan_analyses[0].plan.marketing_name,
        'score': report.plan_analyses[0].metrics.weighted_total_score
    }

# Process multiple clients in parallel
client_files = list(Path('./clients/').glob('*.json'))

with ProcessPoolExecutor(max_workers=4) as executor:
    futures = [
        executor.submit(analyze_client_profile, str(cf), f"./output/{cf.stem}/")
        for cf in client_files
    ]
    
    results = [future.result() for future in futures]
    
# Summary report
print("Batch Analysis Complete:")
print("-" * 50)
for result in results:
    print(f"Client: {result['client']}")
    print(f"  Plans Analyzed: {result['plans_analyzed']}")
    print(f"  Recommendation: {result['top_plan']} ({result['score']:.1f}/10)")
    print()
```

## Error Handling

### Comprehensive Error Management

```python
from healthplan_navigator.analyzer import HealthPlanAnalyzer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_analysis_with_fallbacks(client, documents_dir):
    """
    Perform analysis with comprehensive error handling and fallbacks.
    """
    analyzer = HealthPlanAnalyzer()
    report = None
    
    try:
        # Try live API first
        logger.info("Attempting Healthcare.gov API fetch...")
        report = analyzer.analyze(
            client=client,
            healthcare_gov_fetch=True,
            formats=['summary']
        )
        logger.info(f"Success: Analyzed {len(report.plan_analyses)} plans from API")
        
    except Exception as api_error:
        logger.warning(f"API fetch failed: {api_error}")
        logger.info("Falling back to local documents...")
        
        try:
            # Fallback to local documents
            report = analyzer.analyze(
                client=client,
                plan_sources=documents_dir,
                formats=['summary']
            )
            logger.info(f"Success: Analyzed {len(report.plan_analyses)} local plans")
            
        except Exception as local_error:
            logger.error(f"Local analysis also failed: {local_error}")
            
            # Last resort - return error report
            return {
                'status': 'error',
                'errors': [str(api_error), str(local_error)],
                'recommendation': 'Please check plan documents and try again'
            }
    
    return {
        'status': 'success',
        'report': report,
        'top_plan': report.plan_analyses[0] if report.plan_analyses else None
    }
```

### API-Specific Error Handling

```python
from healthplan_navigator.integrations.healthcare_gov import HealthcareGovAPI
import time

class RobustHealthcareGovAPI(HealthcareGovAPI):
    """
    Enhanced API client with robust error handling and retries.
    """
    
    def fetch_plans_with_retry(self, zipcode: str, max_retries: int = 3):
        """
        Fetch plans with exponential backoff retry strategy.
        """
        for attempt in range(max_retries):
            try:
                plans = self.fetch_plans(zipcode)
                if plans:
                    return plans
                    
            except Exception as e:
                wait_time = 2 ** attempt  # Exponential backoff
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error("All retry attempts exhausted")
                    raise
        
        return []
```

## Extension Guide

### Adding Custom Metrics

```python
from dataclasses import dataclass
from healthplan_navigator.core.models import ScoringMetrics
from healthplan_navigator.core.score import HealthPlanScorer

@dataclass
class ExtendedMetrics(ScoringMetrics):
    """Extended metrics including telehealth and mental health coverage."""
    telehealth_score: float = 0.0
    mental_health_score: float = 0.0

class ExtendedScorer(HealthPlanScorer):
    """Enhanced scorer with additional metrics."""
    
    DEFAULT_WEIGHTS = {
        'provider_network': 0.25,
        'medication_coverage': 0.20,
        'total_cost': 0.15,
        'financial_protection': 0.10,
        'administrative_simplicity': 0.10,
        'plan_quality': 0.05,
        'telehealth': 0.10,  # New
        'mental_health': 0.05  # New
    }
    
    def _score_telehealth(self, plan: Plan) -> float:
        """Score telehealth coverage (0-10)."""
        score = 0.0
        
        # Check for telehealth offerings
        if hasattr(plan, 'offers_telehealth') and plan.offers_telehealth:
            score += 5.0
            
            # Bonus for low/no copay
            if hasattr(plan, 'telehealth_copay'):
                if plan.telehealth_copay == 0:
                    score += 5.0
                elif plan.telehealth_copay <= 25:
                    score += 3.0
                else:
                    score += 1.0
        
        return min(score, 10.0)
    
    def _score_mental_health(self, plan: Plan) -> float:
        """Score mental health coverage (0-10)."""
        score = 5.0  # Base score
        
        # Check for mental health benefits
        if hasattr(plan, 'mental_health_copay'):
            if plan.mental_health_copay <= plan.copay_primary:
                score += 3.0  # Mental health parity
            
            if plan.mental_health_copay <= 50:
                score += 2.0  # Affordable access
        
        return min(score, 10.0)
```

### Custom API Integration

```python
from typing import List, Optional
import requests

class CustomInsuranceAPI:
    """
    Integration with a custom insurance provider API.
    """
    
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
    
    def fetch_provider_plans(self, provider_id: str) -> List[Plan]:
        """
        Fetch plans from a specific insurance provider.
        """
        response = self.session.get(
            f"{self.base_url}/providers/{provider_id}/plans",
            timeout=30
        )
        
        if response.status_code == 200:
            return self._transform_to_plans(response.json())
        else:
            raise Exception(f"API error: {response.status_code}")
    
    def _transform_to_plans(self, api_data: dict) -> List[Plan]:
        """Transform API response to Plan objects."""
        plans = []
        
        for plan_data in api_data.get('plans', []):
            plan = Plan(
                plan_id=plan_data['id'],
                issuer=plan_data['carrier'],
                marketing_name=plan_data['name'],
                plan_type=PlanType[plan_data['type'].upper()],
                metal_level=MetalLevel[plan_data['tier'].upper()],
                monthly_premium=float(plan_data['premium']),
                deductible=float(plan_data['deductible']),
                oop_max=float(plan_data['oop_max']),
                # Map additional fields...
            )
            plans.append(plan)
        
        return plans
```

## Performance Optimization

### Caching Strategy

```python
from functools import lru_cache
from typing import Tuple
import hashlib
import pickle

class CachedAnalyzer(HealthPlanAnalyzer):
    """
    Analyzer with intelligent caching for repeated operations.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._score_cache = {}
        self._api_cache = {}
    
    def _get_cache_key(self, client: Client, plan: Plan) -> str:
        """Generate stable cache key for client-plan pair."""
        # Create hashable representation
        client_str = f"{client.personal.zipcode}:{len(client.medical_profile.providers)}:{len(client.medical_profile.medications)}"
        plan_str = f"{plan.plan_id}:{plan.monthly_premium}:{plan.deductible}"
        combined = f"{client_str}|{plan_str}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    @lru_cache(maxsize=256)
    def _cached_score_plan(self, cache_key: str) -> PlanAnalysis:
        """Cached scoring with LRU eviction."""
        # Reconstruct objects from cache key (simplified)
        # In production, store serialized objects
        return self.engine.scorer.score_plan(...)
    
    def analyze(self, client: Client, **kwargs) -> AnalysisReport:
        """Analyze with caching."""
        # Check if we've analyzed this exact client recently
        client_hash = self._get_client_hash(client)
        
        if client_hash in self._api_cache:
            cached_data = self._api_cache[client_hash]
            age = time.time() - cached_data['timestamp']
            
            if age < 3600:  # 1 hour cache
                logger.info("Using cached analysis results")
                return cached_data['report']
        
        # Perform analysis
        report = super().analyze(client, **kwargs)
        
        # Cache results
        self._api_cache[client_hash] = {
            'report': report,
            'timestamp': time.time()
        }
        
        return report
```

### Parallel Processing

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio

class ParallelAnalyzer(HealthPlanAnalyzer):
    """
    Analyzer with parallel processing capabilities.
    """
    
    def analyze_parallel(self, client: Client, plan_sources: List[str]) -> AnalysisReport:
        """
        Analyze multiple plan sources in parallel.
        """
        plans = []
        
        # Parse documents in parallel
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(self.parser.parse_document, source): source
                for source in plan_sources
            }
            
            for future in as_completed(futures):
                try:
                    plan = future.result(timeout=10)
                    if plan:
                        plans.append(plan)
                except Exception as e:
                    logger.error(f"Failed to parse {futures[future]}: {e}")
        
        # Score plans in parallel
        with ThreadPoolExecutor(max_workers=5) as executor:
            score_futures = {
                executor.submit(self.engine.scorer.score_plan, client, plan, plans): plan
                for plan in plans
            }
            
            analyses = []
            for future in as_completed(score_futures):
                try:
                    analysis = future.result(timeout=5)
                    analyses.append(analysis)
                except Exception as e:
                    logger.error(f"Failed to score plan: {e}")
        
        # Sort and create report
        analyses.sort(key=lambda a: a.metrics.weighted_total_score, reverse=True)
        
        return AnalysisReport(
            client=client,
            plan_analyses=analyses,
            generated_at=datetime.now()
        )
```

### Memory-Efficient Streaming

```python
from typing import Generator
import gc

class StreamingAnalyzer(HealthPlanAnalyzer):
    """
    Memory-efficient analyzer for large datasets.
    """
    
    def analyze_streaming(self, 
                         client: Client,
                         plan_sources: List[str],
                         batch_size: int = 10) -> Generator[PlanAnalysis, None, None]:
        """
        Stream analysis results to minimize memory usage.
        
        Processes plans in batches and yields results immediately,
        allowing garbage collection between batches.
        """
        for i in range(0, len(plan_sources), batch_size):
            batch = plan_sources[i:i + batch_size]
            
            # Process batch
            plans = []
            for source in batch:
                plan = self.parser.parse_document(source)
                if plan:
                    plans.append(plan)
            
            # Score and yield
            for plan in plans:
                analysis = self.engine.scorer.score_plan(client, plan, plans)
                yield analysis
            
            # Clear batch from memory
            del plans
            gc.collect()
    
    def generate_streaming_report(self, analyses: Generator) -> None:
        """
        Generate report from streaming results.
        """
        # Write header
        with open('streaming_report.csv', 'w') as f:
            f.write('Plan Name,Score,Annual Cost\n')
            
            # Process results as they arrive
            for analysis in analyses:
                f.write(f"{analysis.plan.marketing_name},")
                f.write(f"{analysis.metrics.weighted_total_score:.1f},")
                f.write(f"{analysis.estimated_annual_cost:.0f}\n")
```

## API Integration Patterns

### Resilient API Client Pattern

```python
from typing import Optional, Callable
import functools

def with_fallback(fallback_func: Callable):
    """
    Decorator for API methods with automatic fallback.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                if result:
                    return result
            except Exception as e:
                logger.warning(f"{func.__name__} failed: {e}")
            
            # Use fallback
            logger.info(f"Using fallback for {func.__name__}")
            return fallback_func(*args, **kwargs)
        
        return wrapper
    return decorator

class ResilientHealthcareAPI:
    """
    API client with automatic fallbacks and resilience patterns.
    """
    
    @with_fallback(lambda self, zip: self._fetch_cached_plans(zip))
    def fetch_plans(self, zipcode: str) -> List[Plan]:
        """Fetch with automatic cache fallback."""
        # Try live API
        return self._fetch_live_plans(zipcode)
    
    def _fetch_cached_plans(self, zipcode: str) -> List[Plan]:
        """Fallback to cached data."""
        cache_file = self.cache_dir / f"plans_{zipcode}.json"
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                return self._transform_to_plans(json.load(f))
        return []
    
    @with_fallback(lambda self: False)
    def validate_api_access(self) -> bool:
        """Validate with graceful failure."""
        response = self.session.get(f"{self.base_url}/health", timeout=5)
        return response.status_code == 200
```

### Circuit Breaker Pattern

```python
from enum import Enum
import time

class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, skip calls
    HALF_OPEN = "half_open"  # Testing recovery

class CircuitBreaker:
    """
    Circuit breaker for API calls to prevent cascading failures.
    """
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    def call(self, func: Callable, *args, **kwargs):
        """
        Execute function with circuit breaker protection.
        """
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
            
        except Exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to retry."""
        return (
            self.last_failure_time and
            time.time() - self.last_failure_time >= self.recovery_timeout
        )
    
    def _on_success(self):
        """Reset circuit breaker on success."""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        """Handle failure and potentially open circuit."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning("Circuit breaker opened due to repeated failures")
```

---

## 📚 Complete API Reference Summary

This comprehensive API documentation for HealthPlan Navigator v1.1.0 provides:

- **Complete Module Documentation**: Every class, method, and attribute
- **Live API Integration**: Healthcare.gov, NPPES, RxNorm, GoodRx
- **Type Safety**: Extensive type hints and enumerations
- **Real-World Examples**: Production-ready code samples
- **Error Handling**: Comprehensive error management strategies
- **Performance Patterns**: Caching, parallel processing, streaming
- **Extension Guide**: How to add custom metrics and integrations
- **Best Practices**: Circuit breakers, fallbacks, resilience patterns

The system is **production-ready** with intelligent fallbacks ensuring functionality even without API keys, while providing enhanced capabilities when live data sources are available.