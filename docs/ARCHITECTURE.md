# HealthPlan Navigator Architecture - Technical Deep Dive

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Principles](#architecture-principles)
3. [Core Components](#core-components)
4. [Data Flow](#data-flow)
5. [Module Details](#module-details)
6. [Extension Points](#extension-points)
7. [Performance Optimization](#performance-optimization)
8. [Security Architecture](#security-architecture)
9. [Testing Strategy](#testing-strategy)
10. [Deployment Architecture](#deployment-architecture)
11. [Future Enhancements](#future-enhancements)

## System Overview

HealthPlan Navigator employs a **modular, layered architecture** designed for extensibility, maintainability, and performance. The system processes healthcare plan documents through a sophisticated pipeline that extracts data, applies scoring algorithms, and generates actionable insights.

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              User Interface Layer                            │
├─────────────────┬──────────────────┬──────────────────┬────────────────────┤
│   CLI Interface │  Web Interface   │   REST API       │  SDK/Library       │
│   (cli.py)      │  (Future)        │   (Future)       │  (Direct Import)   │
└─────────────────┴──────────────────┴──────────────────┴────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Orchestration Layer                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                      Analysis Engine (engine.py)                             │
│  • Workflow Coordination  • Plan Comparison  • Result Aggregation           │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    ▼                                   ▼
┌─────────────────────────────────┐ ┌─────────────────────────────────┐
│        Business Logic Layer      │ │      Data Processing Layer      │
├─────────────────────────────────┤ ├─────────────────────────────────┤
│   Scoring Engine (score.py)     │ │  Document Parser (ingest.py)    │
│   • 6-Metric Calculations       │ │  • PDF/DOCX/JSON/CSV Support    │
│   • Weighted Scoring            │ │  • Text Extraction              │
│   • Normalization               │ │  • Pattern Recognition          │
└─────────────────────────────────┘ └─────────────────────────────────┘
                    │                                   │
                    └─────────────────┬─────────────────┘
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Data Model Layer                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                          Core Models (models.py)                             │
│  • Client Profile  • Plan Details  • Scoring Results  • Analysis Output     │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Output Generation Layer                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                         Report Generator (report.py)                         │
│  • Markdown Reports  • CSV Matrices  • HTML Dashboards  • JSON Exports     │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Architecture Principles

### 1. **Separation of Concerns**
Each module has a single, well-defined responsibility:
- **models.py**: Data structures only
- **ingest.py**: Document parsing only
- **score.py**: Scoring logic only
- **engine.py**: Orchestration only
- **report.py**: Output generation only

### 2. **Dependency Inversion**
High-level modules don't depend on low-level modules. Both depend on abstractions:
```python
# Good: Engine depends on abstract interfaces
class AnalysisEngine:
    def __init__(self, parser: DocumentParser, scorer: PlanScorer):
        self.parser = parser
        self.scorer = scorer
```

### 3. **Open/Closed Principle**
System is open for extension but closed for modification:
```python
# Easy to add new document formats without changing existing code
class DocumentParser:
    def parse(self, file_path: str) -> Plan:
        if file_path.endswith('.pdf'):
            return self._parse_pdf(file_path)
        elif file_path.endswith('.xlsx'):  # New format
            return self._parse_excel(file_path)
```

### 4. **Single Source of Truth**
Each piece of information has exactly one authoritative source:
- Client data: `sample_client.json`
- Scoring weights: `METRIC_WEIGHTS` constant
- Plan data: Parsed documents

### 5. **Fail-Safe Defaults**
System continues operating with degraded functionality rather than failing:
```python
def get_plan_quality_score(self, plan: Plan) -> float:
    if plan.star_rating:
        return plan.star_rating * 2
    return 5.0  # Neutral score if data missing
```

## Core Components

### 1. Document Ingestion Layer (`healthplan_navigator/core/ingest.py`)

**Purpose**: Transform diverse document formats into standardized data structures.

**Key Classes**:
```python
class DocumentParser:
    """Factory for document parsing strategies"""
    
    def parse(self, file_path: str) -> Optional[Plan]:
        """Route to appropriate parser based on file type"""
        
    def _parse_pdf(self, file_path: str) -> Optional[Plan]:
        """Extract data from PDF documents using pdfplumber"""
        
    def _parse_docx(self, file_path: str) -> Optional[Plan]:
        """Extract data from Word documents using python-docx"""
        
    def _parse_json(self, file_path: str) -> Optional[Plan]:
        """Load structured data from JSON files"""
        
    def _parse_csv(self, file_path: str) -> List[Plan]:
        """Batch load plans from CSV files"""
```

**Data Extraction Strategy**:
1. **Text Extraction**: Raw text from documents
2. **Pattern Matching**: Regex for specific data points
3. **Table Parsing**: Structured data from tables
4. **Fallback Handling**: Defaults for missing data

**Example Pattern Matching**:
```python
# Extract premium from text
premium_pattern = r'Monthly Premium:\s*\$?([\d,]+\.?\d*)'
match = re.search(premium_pattern, text)
if match:
    premium = float(match.group(1).replace(',', ''))
```

### 2. Data Models (`healthplan_navigator/core/models.py`)

**Purpose**: Define type-safe, validated data structures.

**Core Models**:

```python
@dataclass
class PersonalInfo:
    """Client demographic and eligibility data"""
    full_name: str
    dob: str
    zipcode: str
    household_size: int
    annual_income: float
    csr_eligible: bool

@dataclass
class Provider:
    """Healthcare provider details"""
    name: str
    specialty: str
    priority: str  # "must-keep" or "nice-to-keep"
    visit_frequency: int

@dataclass
class Medication:
    """Prescription medication details"""
    name: str
    dosage: str
    frequency: str
    annual_doses: int
    manufacturer_program: Optional[ManufacturerProgram]

@dataclass
class Plan:
    """Complete healthcare plan information"""
    name: str
    issuer: str
    plan_type: str  # HMO, PPO, EPO, POS
    metal_tier: str  # Bronze, Silver, Gold, Platinum
    premium: float
    deductible: float
    oop_max: float
    network: List[str]
    formulary: Dict[str, str]
    requires_referral: bool
    star_rating: Optional[float]
```

**Design Patterns Used**:
- **Builder Pattern**: For complex object construction
- **Value Objects**: Immutable data containers
- **Type Safety**: Comprehensive type hints

### 3. Scoring Engine (`healthplan_navigator/core/score.py`)

**Purpose**: Implement sophisticated multi-metric scoring algorithms.

**Scoring Architecture**:

```python
class HealthPlanScorer:
    """Calculates 0-10 scores across 6 metrics"""
    
    METRIC_WEIGHTS = {
        'provider_network': 0.30,
        'medication_coverage': 0.25,
        'total_cost': 0.20,
        'financial_protection': 0.10,
        'administrative_simplicity': 0.10,
        'plan_quality': 0.05
    }
    
    def score_plan(self, plan: Plan, client: Client) -> ScoringResult:
        """Calculate all metric scores for a plan"""
        
    def _score_provider_network(self, plan: Plan, client: Client) -> float:
        """Score: 0-10 based on in-network provider coverage"""
        
    def _score_medication_coverage(self, plan: Plan, client: Client) -> float:
        """Score: 0-10 based on formulary and assistance programs"""
        
    def _score_total_cost(self, plan: Plan, client: Client) -> float:
        """Score: 0-10 normalized against other plans"""
        
    def _score_financial_protection(self, plan: Plan) -> float:
        """Score: 0-10 based on deductible and OOP max"""
        
    def _score_administrative_simplicity(self, plan: Plan) -> float:
        """Score: 0-10 based on ease of use factors"""
        
    def _score_plan_quality(self, plan: Plan) -> float:
        """Score: 0-10 based on star ratings"""
```

**Detailed Scoring Logic**:

#### Provider Network Score (30% weight)
```python
def _score_provider_network(self, plan: Plan, client: Client) -> float:
    must_keep = [p for p in client.providers if p.priority == "must-keep"]
    in_network = sum(1 for p in must_keep if p.name in plan.network)
    
    coverage_ratio = in_network / len(must_keep) if must_keep else 1.0
    
    if coverage_ratio == 1.0:
        score = 10.0
    elif coverage_ratio >= 0.8:
        score = 7.0
    elif coverage_ratio >= 0.5:
        score = 4.0
    else:
        score = 0.0
    
    # Penalty for referral requirements
    if plan.requires_referral:
        score = max(0, score - 2.0)
    
    return score
```

#### Medication Coverage Score (25% weight)
```python
def _score_medication_coverage(self, plan: Plan, client: Client) -> float:
    total_score = 0
    medication_count = len(client.medications)
    
    for medication in client.medications:
        med_score = 0
        
        if medication.name in plan.formulary:
            tier = plan.formulary[medication.name]
            if tier in ['generic', 'preferred']:
                med_score = 10
            elif tier == 'non-preferred':
                med_score = 7
            else:
                med_score = 5
        elif medication.manufacturer_program:
            med_score = 6
        else:
            med_score = 0
        
        total_score += med_score
    
    return total_score / medication_count if medication_count > 0 else 10.0
```

### 4. Analysis Engine (`healthplan_navigator/analysis/engine.py`)

**Purpose**: Orchestrate the complete analysis workflow.

**Key Responsibilities**:

```python
class HealthPlanAnalyzer:
    """Main orchestration engine"""
    
    def __init__(self, client: Client):
        self.client = client
        self.parser = DocumentParser()
        self.scorer = HealthPlanScorer()
        self.plans = []
        self.results = None
    
    def add_plan_from_file(self, file_path: str):
        """Parse and add a plan to analysis queue"""
        plan = self.parser.parse(file_path)
        if plan:
            self.plans.append(plan)
    
    def analyze(self) -> AnalysisResults:
        """Execute complete analysis workflow"""
        # 1. Score each plan
        scored_plans = []
        for plan in self.plans:
            scores = self.scorer.score_plan(plan, self.client)
            scored_plans.append(ScoredPlan(plan, scores))
        
        # 2. Normalize cost scores
        self._normalize_cost_scores(scored_plans)
        
        # 3. Calculate weighted totals
        for sp in scored_plans:
            sp.calculate_overall_score(self.scorer.METRIC_WEIGHTS)
        
        # 4. Rank plans
        scored_plans.sort(key=lambda x: x.overall_score, reverse=True)
        
        # 5. Generate insights
        insights = self._generate_insights(scored_plans)
        
        return AnalysisResults(scored_plans, insights)
```

### 5. Output Generation (`healthplan_navigator/output/report.py`)

**Purpose**: Transform analysis results into multiple consumable formats.

**Report Types**:

```python
class ReportGenerator:
    """Multi-format report generation"""
    
    def generate_all_reports(self, results: AnalysisResults, output_dir: str):
        """Create all report formats"""
        self._generate_executive_summary(results, output_dir)
        self._generate_scoring_matrix(results, output_dir)
        self._generate_interactive_dashboard(results, output_dir)
        self._generate_json_export(results, output_dir)
    
    def _generate_executive_summary(self, results: AnalysisResults, output_dir: str):
        """Markdown report with key findings"""
        
    def _generate_scoring_matrix(self, results: AnalysisResults, output_dir: str):
        """CSV file with detailed scores"""
        
    def _generate_interactive_dashboard(self, results: AnalysisResults, output_dir: str):
        """HTML dashboard with Plotly charts"""
        
    def _generate_json_export(self, results: AnalysisResults, output_dir: str):
        """Complete data export for integration"""
```

## Data Flow

### Complete Analysis Pipeline

```
1. INPUT STAGE
   ├── Client Profile Loading
   │   └── JSON → Client object with validation
   └── Plan Document Collection
       └── PDF/DOCX/CSV → File paths list

2. PARSING STAGE
   ├── Document Type Detection
   ├── Content Extraction
   │   ├── Text extraction (pdfplumber/python-docx)
   │   ├── Table parsing
   │   └── Pattern matching
   └── Data Normalization
       └── Raw data → Plan objects

3. SCORING STAGE
   ├── Individual Metric Calculation
   │   ├── Provider network analysis
   │   ├── Medication formulary lookup
   │   ├── Cost projections
   │   ├── Protection thresholds
   │   ├── Simplicity factors
   │   └── Quality ratings
   ├── Score Normalization
   │   └── Relative scoring for costs
   └── Weighted Aggregation
       └── 6 metrics → Overall score

4. ANALYSIS STAGE
   ├── Plan Ranking
   │   └── Sort by overall score
   ├── Insight Generation
   │   ├── Best plans by category
   │   ├── Key trade-offs
   │   └── Warnings/concerns
   └── Recommendation Logic
       └── Top 3 plans with rationale

5. OUTPUT STAGE
   ├── Report Generation
   │   ├── Executive summary (MD)
   │   ├── Scoring matrix (CSV)
   │   ├── Interactive dashboard (HTML)
   │   └── Raw data (JSON)
   └── File Organization
       └── Timestamped output directory
```

## Module Details

### healthplan_navigator/__init__.py
```python
"""Package initialization and version management"""
__version__ = "1.0.0"
__author__ = "Ryan Zimmerman"

# Public API exports
from .core.models import Client, Plan, ScoringResult
from .analysis.engine import HealthPlanAnalyzer
from .output.report import ReportGenerator
```

### healthplan_navigator/core/__init__.py
```python
"""Core functionality exports"""
from .models import *
from .ingest import DocumentParser
from .score import HealthPlanScorer
```

### healthplan_navigator/analysis/__init__.py
```python
"""Analysis engine exports"""
from .engine import HealthPlanAnalyzer, AnalysisResults
```

### healthplan_navigator/output/__init__.py
```python
"""Output generation exports"""
from .report import ReportGenerator
```

## Extension Points

### 1. Adding New Scoring Metrics

**Step 1**: Extend the scoring model
```python
# In models.py
@dataclass
class ScoringResult:
    provider_network: float
    medication_coverage: float
    total_cost: float
    financial_protection: float
    administrative_simplicity: float
    plan_quality: float
    telehealth_access: float  # NEW METRIC
```

**Step 2**: Implement scoring logic
```python
# In score.py
def _score_telehealth_access(self, plan: Plan) -> float:
    """Score 0-10 based on telehealth features"""
    score = 0.0
    
    if plan.offers_telehealth:
        score += 5.0
    if plan.telehealth_copay == 0:
        score += 3.0
    if plan.mental_health_telehealth:
        score += 2.0
    
    return min(score, 10.0)
```

**Step 3**: Update weights
```python
METRIC_WEIGHTS = {
    'provider_network': 0.25,
    'medication_coverage': 0.20,
    'total_cost': 0.20,
    'financial_protection': 0.10,
    'administrative_simplicity': 0.10,
    'plan_quality': 0.05,
    'telehealth_access': 0.10  # NEW WEIGHT
}
```

### 2. Supporting New Document Formats

**Step 1**: Add parser method
```python
# In ingest.py
def _parse_xml(self, file_path: str) -> Optional[Plan]:
    """Parse XML plan documents"""
    import xml.etree.ElementTree as ET
    
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # Extract plan data from XML structure
    plan_data = {
        'name': root.find('.//PlanName').text,
        'premium': float(root.find('.//Premium').text),
        # ... more fields
    }
    
    return Plan(**plan_data)
```

**Step 2**: Register file extension
```python
def parse(self, file_path: str) -> Optional[Plan]:
    if file_path.endswith('.xml'):
        return self._parse_xml(file_path)
    # ... existing parsers
```

### 3. Custom Analysis Rules

**Step 1**: Subclass the analyzer
```python
class SpecializedHealthPlanAnalyzer(HealthPlanAnalyzer):
    """Analyzer with custom rules for specific populations"""
    
    def _apply_senior_adjustments(self, scored_plans: List[ScoredPlan]):
        """Adjust scores for Medicare-eligible seniors"""
        for plan in scored_plans:
            if plan.plan.is_medicare_advantage:
                plan.scores.plan_quality *= 1.2  # Boost quality importance
```

### 4. API Integration Points

**Provider Network APIs**:
```python
class NetworkValidator:
    """Validate provider networks against external APIs"""
    
    def verify_provider(self, provider_name: str, plan_network_id: str) -> bool:
        """Check if provider is actually in network"""
        response = requests.get(
            f"https://api.provider-network.com/verify",
            params={'provider': provider_name, 'network': plan_network_id}
        )
        return response.json()['in_network']
```

**Drug Pricing APIs**:
```python
class DrugPricer:
    """Get real-time drug pricing information"""
    
    def get_drug_price(self, drug_name: str, dosage: str) -> float:
        """Fetch current cash price for medication"""
        response = requests.get(
            f"https://api.drugpricing.com/price",
            params={'drug': drug_name, 'dosage': dosage}
        )
        return response.json()['cash_price']
```

## Performance Optimization

### 1. Concurrent Document Processing
```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def parse_documents_parallel(file_paths: List[str]) -> List[Plan]:
    """Parse multiple documents concurrently"""
    plans = []
    parser = DocumentParser()
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_file = {
            executor.submit(parser.parse, fp): fp 
            for fp in file_paths
        }
        
        for future in as_completed(future_to_file):
            plan = future.result()
            if plan:
                plans.append(plan)
    
    return plans
```

### 2. Caching Strategy
```python
from functools import lru_cache

class CachedDocumentParser(DocumentParser):
    """Parser with caching for repeated analyses"""
    
    @lru_cache(maxsize=100)
    def parse(self, file_path: str) -> Optional[Plan]:
        """Cache parsed plans by file path"""
        return super().parse(file_path)
```

### 3. Lazy Loading
```python
class LazyPlan:
    """Load plan details only when accessed"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._data = None
    
    @property
    def data(self):
        if self._data is None:
            parser = DocumentParser()
            self._data = parser.parse(self.file_path)
        return self._data
```

### 4. Memory-Efficient Processing
```python
def process_large_csv(file_path: str, chunk_size: int = 1000):
    """Process large CSV files in chunks"""
    for chunk in pd.read_csv(file_path, chunksize=chunk_size):
        plans = [Plan(**row) for _, row in chunk.iterrows()]
        yield plans
```

## Security Architecture

### 1. Input Validation
```python
def validate_file_path(file_path: str) -> bool:
    """Ensure file path is safe and within allowed directories"""
    allowed_dirs = ['personal_documents', 'test_data']
    abs_path = os.path.abspath(file_path)
    
    return any(
        abs_path.startswith(os.path.abspath(dir)) 
        for dir in allowed_dirs
    )
```

### 2. Data Sanitization
```python
def sanitize_plan_data(data: dict) -> dict:
    """Remove or mask sensitive information"""
    sanitized = data.copy()
    
    # Remove SSN if present
    if 'ssn' in sanitized:
        del sanitized['ssn']
    
    # Mask account numbers
    if 'account_number' in sanitized:
        sanitized['account_number'] = 'XXX-' + sanitized['account_number'][-4:]
    
    return sanitized
```

### 3. Secure Configuration
```python
class SecureConfig:
    """Centralized security configuration"""
    
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.json', '.csv'}
    RATE_LIMIT = 100  # Max files per analysis
    
    @classmethod
    def validate_file(cls, file_path: str) -> bool:
        """Comprehensive file validation"""
        # Check extension
        if not any(file_path.endswith(ext) for ext in cls.ALLOWED_EXTENSIONS):
            return False
        
        # Check file size
        if os.path.getsize(file_path) > cls.MAX_FILE_SIZE:
            return False
        
        return True
```

## Testing Strategy

### 1. Unit Testing Structure
```python
# tests/test_models.py
class TestModels(unittest.TestCase):
    def test_client_validation(self):
        """Test client data validation"""
        
    def test_plan_initialization(self):
        """Test plan object creation"""

# tests/test_scoring.py  
class TestScoring(unittest.TestCase):
    def test_provider_network_scoring(self):
        """Test provider network score calculation"""
        
    def test_medication_scoring(self):
        """Test medication coverage scoring"""

# tests/test_parsing.py
class TestParsing(unittest.TestCase):
    def test_pdf_parsing(self):
        """Test PDF document parsing"""
        
    def test_missing_data_handling(self):
        """Test graceful handling of incomplete data"""
```

### 2. Integration Testing
```python
# tests/test_integration.py
class TestEndToEnd(unittest.TestCase):
    def test_complete_analysis_workflow(self):
        """Test full analysis from files to reports"""
        
        # Setup
        client = Client.from_file('test_data/test_client.json')
        analyzer = HealthPlanAnalyzer(client)
        
        # Add test plans
        test_plans = ['test_data/plan1.pdf', 'test_data/plan2.docx']
        for plan_file in test_plans:
            analyzer.add_plan_from_file(plan_file)
        
        # Run analysis
        results = analyzer.analyze()
        
        # Verify
        self.assertIsNotNone(results)
        self.assertTrue(len(results.scored_plans) > 0)
        self.assertTrue(all(0 <= p.overall_score <= 10 for p in results.scored_plans))
```

### 3. Performance Testing
```python
# tests/test_performance.py
class TestPerformance(unittest.TestCase):
    def test_large_document_processing(self):
        """Test processing of large PDF files"""
        
    def test_concurrent_parsing(self):
        """Test parallel document processing"""
        
    def test_memory_usage(self):
        """Monitor memory consumption during analysis"""
```

## Deployment Architecture

### 1. Local Installation
```bash
# Standard installation
pip install healthplan-navigator

# Development installation
git clone https://github.com/rzimmerman2022/healthplan-navigator.git
cd healthplan-navigator
pip install -e .
```

### 2. Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpoppler-cpp-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run application
CMD ["python", "-m", "healthplan_navigator.cli"]
```

### 3. Cloud Deployment (AWS Lambda)
```python
# lambda_handler.py
import json
from healthplan_navigator import HealthPlanAnalyzer

def lambda_handler(event, context):
    """AWS Lambda entry point"""
    
    # Parse input
    client_data = json.loads(event['body'])['client']
    plan_files = json.loads(event['body'])['plans']
    
    # Run analysis
    analyzer = HealthPlanAnalyzer.from_dict(client_data)
    for plan_file in plan_files:
        analyzer.add_plan_from_s3(plan_file)
    
    results = analyzer.analyze()
    
    return {
        'statusCode': 200,
        'body': json.dumps(results.to_dict())
    }
```

### 4. Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: healthplan-navigator
spec:
  replicas: 3
  selector:
    matchLabels:
      app: healthplan-navigator
  template:
    metadata:
      labels:
        app: healthplan-navigator
    spec:
      containers:
      - name: analyzer
        image: healthplan-navigator:latest
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
```

## Future Enhancements

### 1. Machine Learning Integration
```python
class MLPlanRecommender:
    """Use ML to personalize plan recommendations"""
    
    def train_model(self, historical_choices: List[Tuple[Client, Plan]]):
        """Train recommendation model on historical data"""
        
    def predict_preferences(self, client: Client, plans: List[Plan]) -> List[float]:
        """Predict client's plan preferences"""
```

### 2. Real-Time Updates
```python
class RealtimePlanMonitor:
    """Monitor plan changes and alert users"""
    
    def watch_formulary_changes(self, plan_id: str):
        """Alert when medications are added/removed from formulary"""
        
    def track_network_updates(self, plan_id: str):
        """Notify when providers join/leave network"""
```

### 3. Multi-Year Analysis
```python
class MultiYearAnalyzer:
    """Project costs and coverage over multiple years"""
    
    def project_costs(self, plan: Plan, years: int = 5) -> List[float]:
        """Estimate costs with medical inflation"""
        
    def simulate_health_events(self, client: Client) -> List[HealthEvent]:
        """Monte Carlo simulation of health scenarios"""
```

### 4. Family Plan Optimization
```python
class FamilyPlanOptimizer:
    """Optimize plan selection for entire families"""
    
    def analyze_family(self, members: List[Client]) -> FamilyAnalysis:
        """Find best plan considering all family members"""
        
    def split_coverage_analysis(self, members: List[Client]) -> SplitCoverageRecommendation:
        """Recommend if family should use different plans"""
```

### 5. API Gateway
```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/v1/analyze', methods=['POST'])
def analyze_plans():
    """REST API endpoint for plan analysis"""
    data = request.json
    
    # Validate input
    if not all(k in data for k in ['client', 'plans']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Run analysis
    analyzer = HealthPlanAnalyzer.from_dict(data['client'])
    for plan_url in data['plans']:
        analyzer.add_plan_from_url(plan_url)
    
    results = analyzer.analyze()
    
    return jsonify(results.to_dict())
```

---

This architecture document serves as the definitive technical reference for the HealthPlan Navigator system. It provides comprehensive details for developers, architects, and AI coding assistants to understand, extend, and maintain the system effectively.