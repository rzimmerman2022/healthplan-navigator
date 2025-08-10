# API Documentation
**Last Updated**: 2025-08-10  
**Version**: 1.1.2  
**Description**: Comprehensive API reference for HealthPlan Navigator

> **HealthPlan Navigator v1.1.2** - Gold Standard Healthcare Analytics API

## Table of Contents
1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Core Classes](#core-classes)
4. [Analysis Methods](#analysis-methods)
5. [Statistical Features](#statistical-features)
6. [Examples](#examples)

## Overview

The HealthPlan Navigator API provides programmatic access to healthcare plan analysis with statistical rigor and mathematical certainty. All API methods include confidence intervals and uncertainty quantification.

## Quick Start

```python
from healthplan_navigator.analyzer import HealthPlanAnalyzer
from healthplan_navigator.core.models import Client, PersonalInfo, MedicalProfile

# Initialize with statistical validation
analyzer = HealthPlanAnalyzer(confidence_level=0.95)

# Create client profile
client = Client(
    personal=PersonalInfo(...),
    medical_profile=MedicalProfile(...)
)

# Analyze with uncertainty quantification
report = analyzer.analyze(client, plans, enable_statistics=True)
```

## Core Classes

### HealthPlanAnalyzer

Main interface for healthcare plan analysis.

#### Constructor

```python
HealthPlanAnalyzer(
    confidence_level: float = 0.95,
    api_keys: Optional[Dict[str, str]] = None,
    enable_mcp: bool = True
)
```

**Parameters:**
- `confidence_level` (float): Statistical confidence level (0.90, 0.95, 0.99)
- `api_keys` (dict, optional): API keys for external integrations
- `enable_mcp` (bool): Enable MCP server integration

#### Methods

##### analyze()

Perform comprehensive healthcare plan analysis with statistical validation.

```python
analyze(
    client: Client,
    plans: Optional[List[Plan]] = None,
    healthcare_gov_fetch: bool = False,
    formats: List[str] = ['summary', 'csv', 'json', 'html'],
    enable_statistics: bool = True,
    monte_carlo_runs: int = 10000
) -> AnalysisReport
```

**Parameters:**
- `client` (Client): Client profile with personal and medical information
- `plans` (List[Plan], optional): Plans to analyze (if None, will fetch from documents/API)
- `healthcare_gov_fetch` (bool): Fetch live data from Healthcare.gov API  
- `formats` (List[str]): Output formats to generate
- `enable_statistics` (bool): Include confidence intervals and uncertainty quantification
- `monte_carlo_runs` (int): Number of Monte Carlo simulation iterations

**Returns:**
- `AnalysisReport`: Complete analysis with statistical validation

**Example:**
```python
report = analyzer.analyze(
    client=my_client,
    enable_statistics=True,
    monte_carlo_runs=10000
)

# Access results with confidence intervals
top_plan = report.top_recommendations[0]
print(f"Score: {top_plan.metrics.weighted_total_score}")
print(f"95% CI: [{top_plan.ci_lower:.2f}, {top_plan.ci_upper:.2f}]")
print(f"P-value vs next plan: {report.statistical_tests['rank_1_vs_2'].p_value}")
```

##### validate_api_access()

Test API connectivity and authentication.

```python
validate_api_access() -> Dict[str, bool]
```

**Returns:**
- `Dict[str, bool]`: Status of each API integration

### Statistical Classes

#### HealthcareStatisticalValidator

Provides statistical validation and uncertainty quantification.

```python
from healthplan_navigator.analytics.statistical_validator import HealthcareStatisticalValidator

validator = HealthcareStatisticalValidator(confidence_level=0.95)
```

##### calculate_confidence_interval()

Calculate confidence intervals using bootstrap or parametric methods.

```python
calculate_confidence_interval(
    data: np.ndarray,
    method: str = 'bootstrap'
) -> Tuple[float, float]
```

**Parameters:**
- `data` (array): Sample data
- `method` (str): 'bootstrap', 't-distribution', or 'normal'

**Returns:**
- `Tuple[float, float]`: Lower and upper confidence bounds

##### test_hypothesis()

Perform hypothesis testing between groups.

```python
test_hypothesis(
    group1: np.ndarray,
    group2: np.ndarray,
    test_type: str = 'auto'
) -> StatisticalResult
```

**Parameters:**
- `group1`, `group2` (array): Data groups to compare
- `test_type` (str): 'auto', 't-test', 'mann-whitney', or 'welch'

**Returns:**
- `StatisticalResult`: Test results with p-value and effect size

##### monte_carlo_simulation()

Run Monte Carlo cost simulations.

```python
monte_carlo_simulation(
    base_params: Dict,
    variations: Dict[str, Tuple[float, float]],
    n_simulations: int = 10000
) -> Dict
```

**Parameters:**
- `base_params` (dict): Base parameter values
- `variations` (dict): Parameter variation ranges
- `n_simulations` (int): Number of simulation runs

**Returns:**
- `Dict`: Simulation results with percentiles and confidence intervals

## Data Models

### Client

Complete client profile for analysis.

```python
@dataclass
class Client:
    personal: PersonalInfo
    medical_profile: MedicalProfile
    priorities: Priorities
```

### PersonalInfo

Personal demographic information.

```python
@dataclass
class PersonalInfo:
    full_name: str
    dob: str  # YYYY-MM-DD format
    zipcode: str  # 5-digit ZIP code
    household_size: int
    annual_income: float
    csr_eligible: bool = False
```

### MedicalProfile

Medical history and current healthcare needs.

```python
@dataclass
class MedicalProfile:
    providers: List[Provider]
    medications: List[Medication]
    conditions: List[str] = field(default_factory=list)
    utilization: Optional[UtilizationProfile] = None
```

### Provider

Healthcare provider information.

```python
@dataclass
class Provider:
    name: str
    specialty: str
    npi: Optional[str] = None
    priority: Priority = Priority.NICE_TO_KEEP
    visit_frequency: int = 1  # per year
```

### Plan

Healthcare plan details with cost-sharing information.

```python
@dataclass
class Plan:
    plan_id: str
    marketing_name: str
    issuer: str
    metal_level: MetalLevel
    plan_type: PlanType
    monthly_premium: float
    deductible: float
    oop_max: float
    # ... additional fields
```

### AnalysisReport

Complete analysis results with statistical validation.

```python
@dataclass
class AnalysisReport:
    client: Client
    plan_analyses: List[PlanAnalysis]
    top_recommendations: List[PlanAnalysis]
    statistical_tests: Dict[str, StatisticalResult]
    uncertainty_analysis: Dict[str, float]
    monte_carlo_results: Optional[Dict] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### PlanAnalysis

Individual plan analysis with confidence intervals.

```python
@dataclass
class PlanAnalysis:
    plan: Plan
    metrics: ScoringMetrics
    estimated_annual_cost: float
    ci_lower: float  # Confidence interval lower bound
    ci_upper: float  # Confidence interval upper bound
    provider_coverage_details: Dict[str, bool]
    medication_coverage_details: Dict[str, str]
    statistical_significance: Optional[float] = None  # p-value vs baseline
```

### ScoringMetrics

Detailed scoring breakdown with uncertainty.

```python
@dataclass
class ScoringMetrics:
    provider_network_score: float
    medication_coverage_score: float
    total_cost_score: float
    financial_protection_score: float
    administrative_simplicity_score: float
    plan_quality_score: float
    weighted_total_score: float
    
    # Statistical validation
    confidence_intervals: Dict[str, Tuple[float, float]] = field(default_factory=dict)
    standard_errors: Dict[str, float] = field(default_factory=dict)
```

## Statistical Output Format

All analysis results include statistical validation:

```json
{
  "plan_analysis": {
    "plan_id": "PLAN123",
    "scores": {
      "provider_network": {
        "value": 8.5,
        "ci_lower": 7.8,
        "ci_upper": 9.2,
        "standard_error": 0.35
      },
      "medication_coverage": {
        "value": 7.2,
        "ci_lower": 6.5,
        "ci_upper": 7.9,
        "standard_error": 0.28
      }
    },
    "statistical_tests": {
      "normality": {
        "shapiro_wilk_p": 0.087,
        "anderson_darling": "normal"
      },
      "vs_second_ranked": {
        "p_value": 0.024,
        "test": "welch_t_test",
        "effect_size": 0.52,
        "significant": true
      }
    },
    "monte_carlo_cost": {
      "mean": 7554.22,
      "ci_lower": 5810.94,
      "ci_upper": 9472.56,
      "percentiles": {
        "5th": 4231.45,
        "25th": 6102.33,
        "50th": 7445.67,
        "75th": 8891.24,
        "95th": 11234.78
      }
    }
  }
}
```

## Integration APIs

### Healthcare.gov API

Fetch live marketplace data.

```python
from healthplan_navigator.integrations.healthcare_gov import HealthcareGovAPI

api = HealthcareGovAPI(api_key="your_key")
plans = api.fetch_plans(
    zipcode="85001",
    metal_levels=["Bronze", "Silver", "Gold"],
    plan_types=["HMO", "PPO"]
)
```

### NPPES Provider Registry

Validate provider networks.

```python
from healthplan_navigator.integrations.providers import ProviderNetworkIntegration

provider_api = ProviderNetworkIntegration()
results = provider_api.search_providers(
    specialty="Primary Care",
    location="85001"
)
```

### RxNorm Medication Database

Check medication coverage and alternatives.

```python
from healthplan_navigator.integrations.medications import MedicationIntegration

med_api = MedicationIntegration()
coverage = med_api.check_medication_coverage(medication, formulary)
alternatives = med_api.find_generic_alternatives(medication)
```

## MCP Integration

### MCP Server Configuration

Configure local MCP servers for document processing.

```json
{
  "mcpServers": {
    "docling": {
      "command": "uvx",
      "args": ["--from=docling-mcp", "docling-mcp-server", "--transport", "stdio"]
    },
    "pymupdf4llm": {
      "command": "uvx", 
      "args": ["pymupdf4llm-mcp@latest", "stdio"]
    },
    "chroma": {
      "command": "uvx",
      "args": ["chroma-mcp", "--client-type", "persistent", "--data-dir", "./vectors"]
    }
  }
}
```

### Claude Code Integration

Use Claude Code with MCP servers for AI-powered analysis.

```python
# Create batch instructions for Claude Code
from healthplan_navigator.claude_orchestrator import ClaudeHealthcareOrchestrator

orchestrator = ClaudeHealthcareOrchestrator()
batches = orchestrator.create_analysis_batch(plans, batch_size=25)

# Process through Claude Code interface
# Results include statistical validation and uncertainty quantification
```

## Error Handling

All API methods include comprehensive error handling:

```python
from healthplan_navigator.core.exceptions import (
    HealthPlanAnalysisError,
    StatisticalValidationError,
    DataQualityError
)

try:
    report = analyzer.analyze(client, plans)
except StatisticalValidationError as e:
    print(f"Statistical validation failed: {e}")
    # Handle insufficient data for confidence intervals
except DataQualityError as e:
    print(f"Data quality issue: {e}")
    # Handle missing or invalid plan data
except HealthPlanAnalysisError as e:
    print(f"Analysis error: {e}")
    # Handle general analysis failures
```

## Rate Limits and Usage

### API Rate Limits

- Healthcare.gov API: 100 requests/hour
- NPPES Registry: 1000 requests/hour  
- RxNorm Database: No limit (public API)

### Statistical Computation Limits

- Monte Carlo simulations: Up to 50,000 iterations
- Bootstrap resampling: Up to 20,000 iterations
- Hypothesis testing: Multiple comparison correction applied

### Memory Requirements

- Basic analysis: 100MB RAM per 100 plans
- Statistical validation: 500MB RAM for full suite
- Monte Carlo simulations: 1GB RAM for 10,000 iterations

## Testing and Validation

### Unit Tests

```bash
# Run specific test modules
python -m pytest tests/test_analyzer.py
python -m pytest tests/test_statistical_validator.py
python -m pytest tests/test_integrations.py
```

### Gold Standard Validation

```bash
# Verify compliance with industry standards
python tests/test_gold_standard.py

# Expected output:
# ✅ Statistical Rigor: PASSED
# ✅ Scoring Validation: PASSED  
# ✅ MCP Configuration: PASSED
# ✅ Data Quality: PASSED
```

### Performance Testing

```python
import time
from healthplan_navigator.analyzer import HealthPlanAnalyzer

analyzer = HealthPlanAnalyzer()

# Benchmark analysis performance
start_time = time.time()
report = analyzer.analyze(client, large_plan_set)
analysis_time = time.time() - start_time

print(f"Analyzed {len(large_plan_set)} plans in {analysis_time:.2f} seconds")
# Expected: < 2 seconds per 100 plans with statistical validation
```

## Changelog

### v1.1.2 (Current)
- Added statistical validation with confidence intervals
- Implemented Monte Carlo cost simulations
- Enhanced MCP integration for Claude Code
- Fixed security vulnerabilities (SQL injection, input validation)

### v1.1.0 
- Added live API integrations (Healthcare.gov, NPPES, RxNorm)
- Implemented comprehensive reporting suite
- Added caching and performance optimizations

### v1.0.0
- Initial release with core healthcare plan analysis
- 6-metric scoring algorithm
- Multi-format report generation

## Support

- **Documentation**: [README.md](../README.md)
- **Issues**: [GitHub Issues](https://github.com/your-org/healthplan-navigator/issues)
- **API Questions**: Use the `api` label on GitHub issues
- **Statistical Validation**: Use the `statistics` label on GitHub issues

---

*Last updated: 2025-08-09 - HealthPlan Navigator v1.1.2*