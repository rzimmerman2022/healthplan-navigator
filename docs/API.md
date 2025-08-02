# HealthPlan Navigator API Documentation

## Core Modules

### `healthplan_navigator.core.models`

Data models for the healthcare plan analysis system.

#### Classes

##### `Client`
Represents a healthcare consumer with their profile and requirements.

```python
@dataclass
class Client:
    personal: PersonalInfo
    medical_profile: MedicalProfile
    priorities: Priorities
```

##### `Plan`
Represents a healthcare insurance plan.

```python
@dataclass
class Plan:
    plan_id: str
    issuer: str
    marketing_name: str
    metal_level: MetalLevel
    monthly_premium: float
    deductible_individual: float
    oop_max_individual: float
    # ... additional fields
```

##### `ScoringMetrics`
Contains all scoring metrics for a plan (0-10 scale).

```python
@dataclass
class ScoringMetrics:
    provider_network_score: float = 0.0  # 0-10
    medication_coverage_score: float = 0.0  # 0-10
    total_cost_score: float = 0.0  # 0-10
    financial_protection_score: float = 0.0  # 0-10
    administrative_simplicity_score: float = 0.0  # 0-10
    plan_quality_score: float = 0.0  # 0-10
    weighted_total_score: float = 0.0  # 0-10
```

### `healthplan_navigator.core.score`

Scoring algorithm implementation.

#### Classes

##### `HealthPlanScorer`
Implements the 6-metric scoring algorithm.

```python
class HealthPlanScorer:
    def score_plan(self, client: Client, plan: Plan, all_plans: List[Plan]) -> PlanAnalysis:
        """Score a single plan against client requirements."""
        pass
```

**Scoring Methods:**
- `_score_provider_network()`: 0-10 based on in-network provider coverage
- `_score_medication_coverage()`: 0-10 based on formulary and assistance programs
- `_score_total_cost()`: 0-10 normalized against all plans
- `_score_financial_protection()`: 0-10 based on deductible and OOPM
- `_score_administrative_simplicity()`: 0-10 with penalties for complexity
- `_score_plan_quality()`: 0-10 based on star rating

### `healthplan_navigator.core.ingest`

Document parsing functionality.

#### Classes

##### `DocumentParser`
Handles parsing of various document formats.

```python
class DocumentParser:
    def parse_document(self, file_path: str) -> Optional[Plan]:
        """Parse a document and extract plan information."""
        pass
    
    def parse_batch(self, directory_path: str) -> List[Plan]:
        """Parse all supported documents in a directory."""
        pass
```

**Supported Formats:**
- PDF (with OCR fallback)
- DOCX
- JSON
- CSV

### `healthplan_navigator.analysis.engine`

Main analysis orchestration.

#### Classes

##### `AnalysisEngine`
Coordinates the analysis process.

```python
class AnalysisEngine:
    def analyze_plans(self, client: Client, plans: List[Plan]) -> AnalysisReport:
        """Analyze all plans for a client and generate comprehensive report."""
        pass
    
    def generate_scoring_matrix(self, report: AnalysisReport) -> List[Dict]:
        """Generate a scoring matrix showing all metrics for all plans."""
        pass
```

### `healthplan_navigator.output.report`

Report generation functionality.

#### Classes

##### `ReportGenerator`
Generates various output formats.

```python
class ReportGenerator:
    def generate_executive_summary(self, report: AnalysisReport) -> str:
        """Generate executive summary in markdown format."""
        pass
    
    def generate_scoring_matrix_csv(self, report: AnalysisReport) -> str:
        """Generate detailed scoring matrix as CSV."""
        pass
    
    def generate_html_dashboard(self, report: AnalysisReport) -> str:
        """Generate interactive HTML dashboard."""
        pass
    
    def generate_json_export(self, report: AnalysisReport) -> str:
        """Generate complete analysis data as JSON."""
        pass
```

## Usage Examples

### Basic Analysis

```python
from healthplan_navigator.core.ingest import DocumentParser
from healthplan_navigator.core.models import Client
from healthplan_navigator.analysis.engine import AnalysisEngine
from healthplan_navigator.output.report import ReportGenerator

# Parse plans
parser = DocumentParser()
plans = parser.parse_batch("./plan_documents")

# Create client profile
client = create_client_profile()  # Your implementation

# Analyze
engine = AnalysisEngine()
report = engine.analyze_plans(client, plans)

# Generate reports
report_gen = ReportGenerator()
summary = report_gen.generate_executive_summary(report)
```

### Custom Scoring Weights

```python
from healthplan_navigator.core.score import HealthPlanScorer

# Create custom scorer with different weights
scorer = HealthPlanScorer()
scorer.WEIGHTS = {
    'provider_network': 0.40,  # Increase provider importance
    'medication_coverage': 0.20,
    'total_cost': 0.20,
    'financial_protection': 0.10,
    'administrative_simplicity': 0.05,
    'plan_quality': 0.05
}
```

### Parsing Specific Document Types

```python
# Parse PDF
plan = parser._parse_pdf("plan.pdf")

# Parse JSON with custom structure
with open("custom_plan.json") as f:
    data = json.load(f)
    plan = parser._json_to_plan(data)

# Parse CSV batch
plans = parser._parse_csv("plans.csv")
```

## Error Handling

All methods include appropriate error handling:

```python
try:
    plans = parser.parse_batch(directory)
except ValueError as e:
    print(f"Invalid input: {e}")
except IOError as e:
    print(f"File access error: {e}")
```

## Extension Points

The system is designed for extensibility:

1. **Custom Metrics**: Add new scoring metrics by extending `ScoringMetrics`
2. **Document Formats**: Add parsers by extending `DocumentParser`
3. **Output Formats**: Add generators by extending `ReportGenerator`
4. **Analysis Rules**: Customize scoring logic in `HealthPlanScorer`