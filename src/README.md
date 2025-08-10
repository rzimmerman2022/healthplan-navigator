# Source Code Directory
**Last Updated**: 2025-08-10  
**Version**: 1.1.2  
**Description**: Source code structure and navigation guide

## Overview

This directory contains the complete source code for the HealthPlan Navigator system. The code is organized in a modular architecture following Python best practices for healthcare analytics applications.

## Directory Structure

```
src/
└── healthplan_navigator/           # Main application package
    ├── __init__.py                # Package initialization
    ├── analyzer.py                # Main analysis orchestrator (PRIMARY ENTRY POINT)
    ├── cli.py                     # Command-line interface
    │
    ├── core/                      # Core business logic and data models
    │   ├── __init__.py
    │   ├── models.py              # Data models (Client, Plan, AnalysisReport)
    │   ├── ingest.py              # Document parsing and data extraction
    │   └── score.py               # Scoring algorithms and calculations
    │
    ├── analysis/                  # Analysis engine and statistical processing
    │   ├── __init__.py
    │   └── engine.py              # 6-metric analysis engine
    │
    ├── analytics/                 # Statistical validation and gold standard compliance
    │   └── statistical_validator.py  # Statistical framework and validation
    │
    ├── integrations/             # External API integrations
    │   ├── __init__.py
    │   ├── healthcare_gov.py     # Healthcare.gov marketplace integration
    │   ├── medications.py        # RxNorm medication database integration
    │   └── providers.py          # NPPES provider network integration
    │
    └── output/                    # Report generation and formatting
        ├── __init__.py
        └── report.py              # Multi-format report generation
```

## Entry Points

### Primary Entry Point
**`analyzer.py`** - Main analysis orchestrator
- Class: `HealthPlanAnalyzer`
- Purpose: Unified interface for complete healthcare plan analysis
- Usage: Import this for programmatic access
```python
from src.healthplan_navigator.analyzer import HealthPlanAnalyzer
analyzer = HealthPlanAnalyzer(confidence_level=0.95)
```

### Secondary Entry Points
**`cli.py`** - Command-line interface
- Function: `main()`
- Purpose: Command-line tools and batch processing
- Usage: Called by setup.py console scripts

### Root Entry Point
**`../main.py`** - Interactive launcher (outside src/)
- Purpose: User-friendly interactive menu system
- Usage: `python main.py` from repository root

## Core Modules

### 1. Core Package (`core/`)
**`models.py`** - Data structures and validation
- `Client`: Personal information and medical profile
- `Plan`: Healthcare plan details and benefits
- `AnalysisReport`: Analysis results with statistical validation
- `PersonalInfo`, `MedicalProfile`, `Priorities`: Supporting models

**`ingest.py`** - Document processing engine
- `DocumentParser`: Multi-format document parsing (PDF, DOCX, JSON)
- Handles Healthcare.gov plan documents and user uploads
- Robust error handling and format detection

**`score.py`** - Scoring algorithms
- 6-metric scoring system implementation
- Weighted scoring with confidence intervals
- Statistical validation integration

### 2. Analysis Package (`analysis/`)
**`engine.py`** - Analysis processing engine
- `AnalysisEngine`: Core analysis orchestration
- Plan comparison and ranking algorithms
- Integration with statistical validation framework

### 3. Analytics Package (`analytics/`)
**`statistical_validator.py`** - Gold standard compliance
- `HealthcareStatisticalValidator`: Statistical rigor enforcement
- Confidence interval calculations
- Monte Carlo simulations
- Hypothesis testing and power analysis

### 4. Integrations Package (`integrations/`)
**`healthcare_gov.py`** - Marketplace integration
- Live plan data fetching from Healthcare.gov
- CMS public data API integration
- Rate limiting and caching

**`medications.py`** - Drug coverage analysis
- RxNorm database integration
- Formulary checking and drug coverage scoring
- Medication cost analysis

**`providers.py`** - Provider network validation
- NPPES provider registry integration
- Network adequacy scoring
- Provider availability analysis

### 5. Output Package (`output/`)
**`report.py`** - Report generation
- Multi-format output (Markdown, CSV, JSON, HTML)
- Statistical visualization with confidence intervals
- Professional formatting and templates

## Import Patterns

### Standard Usage Pattern
```python
# Main entry point - recommended for most users
from src.healthplan_navigator.analyzer import HealthPlanAnalyzer
from src.healthplan_navigator.core.models import Client, PersonalInfo, MedicalProfile

# Initialize analyzer with statistical validation
analyzer = HealthPlanAnalyzer(confidence_level=0.95)

# Create client profile
client = Client(
    personal=PersonalInfo(...),
    medical_profile=MedicalProfile(...)
)

# Run analysis
report = analyzer.analyze(client, enable_statistics=True)
```

### Advanced Usage Pattern
```python
# Direct access to individual components
from src.healthplan_navigator.core.ingest import DocumentParser
from src.healthplan_navigator.analysis.engine import AnalysisEngine
from src.healthplan_navigator.output.report import ReportGenerator
from src.healthplan_navigator.analytics.statistical_validator import HealthcareStatisticalValidator

# Custom workflow
parser = DocumentParser()
engine = AnalysisEngine()
validator = HealthcareStatisticalValidator()
generator = ReportGenerator()
```

### Command-Line Usage
```python
# CLI access
from src.healthplan_navigator.cli import main as cli_main
cli_main()  # Programmatic CLI access
```

## Development Workflow

### 1. Adding New Features
1. **Data Models**: Add new models to `core/models.py`
2. **Analysis Logic**: Extend `analysis/engine.py`
3. **Statistical Validation**: Update `analytics/statistical_validator.py`
4. **API Integration**: Add new integrations to `integrations/`
5. **Output Formats**: Extend `output/report.py`

### 2. Testing New Components
```python
# Import the main analyzer for integration testing
from src.healthplan_navigator.analyzer import HealthPlanAnalyzer
analyzer = HealthPlanAnalyzer()

# Test individual components
from src.healthplan_navigator.core.models import validate_zipcode
assert validate_zipcode("85001") == "85001"
```

### 3. Module Dependencies
```
analyzer.py
├── core.models
├── core.ingest
├── analysis.engine
├── output.report
└── integrations.*

analysis.engine
├── core.models
├── core.score
└── analytics.statistical_validator

integrations.*
├── core.models
└── external APIs (Healthcare.gov, NPPES, RxNorm)
```

## Configuration

### Module-Level Configuration
Most configuration is handled at the analyzer level:
```python
analyzer = HealthPlanAnalyzer(
    confidence_level=0.95,          # Statistical confidence level
    enable_caching=True,            # Enable API response caching
    monte_carlo_runs=10000,         # Statistical simulation iterations
    timeout_seconds=30              # API timeout
)
```

### Environment Variables
- `PYTHONPATH`: Must include project root for imports
- `HEALTHCARE_GOV_API_KEY`: Optional API key for enhanced data access
- `LOG_LEVEL`: Logging verbosity (DEBUG, INFO, WARNING, ERROR)

## Code Quality Standards

### Style Guidelines
- **Formatting**: Black code formatter
- **Type Hints**: Required for all public methods
- **Docstrings**: Google-style docstrings for all classes and methods
- **Import Order**: isort for consistent import organization

### Testing Requirements
- **Coverage**: >90% code coverage required
- **Unit Tests**: Test individual module functions
- **Integration Tests**: Test complete workflows through analyzer.py
- **Statistical Tests**: Validate confidence intervals and statistical claims

### Documentation Standards
- **README files**: Each major module should have usage documentation
- **Code Comments**: Explain complex algorithms and statistical methods
- **API Documentation**: Keep docs/API.md updated with public interface changes

## Performance Considerations

### Memory Usage
- Document parsing can consume significant memory for large PDF files
- Statistical simulations (Monte Carlo) require memory for iteration storage
- Consider chunked processing for batch operations

### Processing Time
- Analysis typically completes in 10-30 seconds for single client
- Network requests to external APIs can add 5-15 seconds
- Statistical validation adds 2-5 seconds for confidence interval calculation

### Optimization Opportunities
- **Caching**: API responses and document parsing results
- **Async Processing**: External API calls could be parallelized
- **Database Integration**: Future enhancement for large-scale deployments

---

For detailed API documentation, see [docs/API.md](../docs/API.md).
For architectural details, see [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md).
For usage examples, see [examples/](../examples/).

**Support**: For questions about source code organization or development, create an issue in the GitHub repository.