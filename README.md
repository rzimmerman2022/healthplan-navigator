```
 _   _            _ _   _     ____  _               _   _             _             _             
| | | | ___  __ _| | |_| |__ |  _ \| | __ _ _ __   | \ | | __ ___   _(_) __ _  __ _| |_ ___  _ __ 
| |_| |/ _ \/ _` | | __| '_ \| |_) | |/ _` | '_ \  |  \| |/ _` \ \ / / |/ _` |/ _` | __/ _ \| '__|
|  _  |  __/ (_| | | |_| | | |  __/| | (_| | | | | | |\  | (_| |\ V /| | (_| | (_| | || (_) | |   
|_| |_|\___|\__,_|_|\__|_| |_|_|   |_|\__,_|_| |_| |_| \_|\__,_| \_/ |_|\__, |\__,_|\__\___/|_|   
                                                                         |___/                      
```

# HealthPlan Navigator v1.0.0

> **AI-Powered Healthcare Plan Analysis System**  
> Transform complex insurance decisions into clear, actionable recommendations with sophisticated 6-metric scoring

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Quick Start](#-quick-start)
- [System Architecture](#-system-architecture)
- [Scoring Methodology](#-scoring-methodology)
- [Installation Guide](#-installation-guide)
- [Usage Examples](#-usage-examples)
- [API Documentation](#-api-documentation)
- [Configuration](#-configuration)
- [Output Formats](#-output-formats)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [Changelog](#-changelog)

## 🎯 Overview

**HealthPlan Navigator** is an advanced healthcare plan analysis system designed to simplify the complex process of choosing health insurance. It ingests plan documents (PDFs, DOCX, JSON, CSV) from Healthcare.gov or private insurers and produces comprehensive analysis reports with 0-10 scores across six critical metrics.

### Core Purpose
- **Analyze** healthcare plan documents automatically
- **Score** plans using a weighted 6-metric system
- **Rank** options based on individual healthcare needs
- **Generate** actionable reports in multiple formats
- **Protect** privacy with local-only processing

### Target Users
- Individuals choosing healthcare plans during open enrollment
- Benefits administrators comparing plan options
- Healthcare consultants analyzing client options
- Developers building healthcare decision support tools

## ✨ Key Features

### 1. Multi-Format Document Ingestion
- **PDF Parser**: Extracts data from plan summaries and benefits documents
- **DOCX Parser**: Processes Word documents with plan details
- **JSON Parser**: Handles structured plan data exports
- **CSV Parser**: Batch processes multiple plans efficiently

### 2. Six-Metric Scoring System
Each metric is scored 0-10 and weighted for overall ranking:

| Metric | Weight | Description |
|--------|--------|-------------|
| Provider Network | 30% | In-network coverage for your doctors |
| Medication Coverage | 25% | Formulary inclusion and cost management |
| Total Annual Cost | 20% | Premium + out-of-pocket estimates |
| Financial Protection | 10% | Deductible and max out-of-pocket limits |
| Administrative Simplicity | 10% | Ease of use, prior auth requirements |
| Plan Quality | 5% | Star ratings and member satisfaction |

### 3. Comprehensive Output Formats
- **Executive Summary** (Markdown): Key findings and recommendations
- **Scoring Matrix** (CSV): Detailed metric breakdowns
- **Interactive Dashboard** (HTML): Visual comparisons with charts
- **Raw Data Export** (JSON): Complete analysis for integration

### 4. Privacy-First Design
- All processing happens locally on your machine
- No data sent to external servers
- Personal documents folder is gitignored
- Secure handling of sensitive health information

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- pip package manager
- 100MB free disk space
- Healthcare plan documents (PDF/DOCX format)

### 30-Second Setup

```bash
# Clone the repository
git clone https://github.com/rzimmerman2022/healthplan-navigator.git
cd "healthgov resaerch projec t"

# Install dependencies
pip install -r requirements.txt

# Run the demo with sample data
python demo.py

# Analyze your own plans
# 1. Place your documents in personal_documents/
# 2. Run analysis
python demo.py
```

### First Analysis
1. Download your plan documents from Healthcare.gov
2. Place PDFs/DOCX files in `personal_documents/`
3. Run `python demo.py`
4. Find reports in `output/YYYY-MM-DD_HHMMSS/`

## 🏗️ System Architecture

### Directory Structure
```
healthgov resaerch projec t/
├── healthplan_navigator/         # Main package
│   ├── __init__.py              # Package initialization
│   ├── core/                    # Core functionality
│   │   ├── __init__.py
│   │   ├── models.py            # Data models (Client, Plan, Scores)
│   │   ├── ingest.py            # Document parsing logic
│   │   └── score.py             # Scoring algorithms
│   ├── analysis/                # Analysis engine
│   │   ├── __init__.py
│   │   └── engine.py            # Orchestrates analysis workflow
│   ├── output/                  # Report generation
│   │   ├── __init__.py
│   │   └── report.py            # Multi-format report creation
│   └── cli.py                   # Command-line interface
├── personal_documents/          # Your healthcare documents (gitignored)
├── docs/                        # Documentation
│   ├── API.md                   # API reference
│   └── ARCHITECTURE.md          # Detailed architecture
├── demo.py                      # Quick start demo
├── sample_client.json           # Example client profile
├── requirements.txt             # Production dependencies
├── requirements-dev.txt         # Development dependencies
├── setup.py                     # Package installation
├── LICENSE                      # MIT License
├── CONTRIBUTING.md              # Contribution guidelines
└── CHANGELOG.md                 # Version history
```

### Core Components

#### 1. Document Ingestion (`core/ingest.py`)
```python
# Handles multiple document formats
- PDFParser: Extracts text and tables from PDFs
- DOCXParser: Processes Word documents
- JSONParser: Loads structured data
- CSVParser: Batch plan processing
```

#### 2. Data Models (`core/models.py`)
```python
# Type-safe data structures
- Client: Personal info, providers, medications
- Plan: Benefits, costs, network details
- Scores: Metric scores and calculations
```

#### 3. Scoring Engine (`core/score.py`)
```python
# Implements 6-metric scoring
- calculate_provider_score()
- calculate_medication_score()
- calculate_cost_score()
- calculate_protection_score()
- calculate_simplicity_score()
- calculate_quality_score()
```

#### 4. Analysis Engine (`analysis/engine.py`)
```python
# Orchestrates the workflow
1. Load client profile
2. Parse plan documents
3. Calculate all scores
4. Rank plans
5. Generate insights
```

#### 5. Report Generator (`output/report.py`)
```python
# Creates multiple output formats
- generate_executive_summary()
- create_scoring_matrix()
- build_interactive_dashboard()
- export_raw_data()
```

## 📊 Scoring Methodology

### Metric 1: Provider Network Adequacy (30%)
Evaluates how well the plan covers your healthcare providers.

**Scoring Logic:**
```
Base Score:
- 10 points: 100% of must-keep providers in-network
- 7 points: 80-99% of must-keep providers in-network
- 4 points: 50-79% of must-keep providers in-network
- 0 points: <50% of must-keep providers in-network

Adjustments:
- -2 points if referrals required for specialists
- +1 point if all nice-to-keep providers also covered
```

**Example:**
- 3 must-keep providers, all in-network = 10 points
- Referrals required = -2 points
- Final score = 8/10

### Metric 2: Medication Coverage & Access (25%)
Analyzes formulary coverage and total medication costs.

**Scoring Logic:**
```
Per Medication:
- Covered on formulary: 10 points
- Not covered but manufacturer program: 6 points
- Not covered, no assistance: 0 points

Modifiers:
- -2 if prior authorization required
- -3 if maximizer program used
- +2 if preferred tier with low copay
```

**Cost Calculation:**
```python
annual_cost = 0
for med in medications:
    if covered:
        annual_cost += copay * doses_per_year
    elif manufacturer_program:
        annual_cost += program_copay * doses_per_year
    else:
        annual_cost += cash_price * doses_per_year
```

### Metric 3: Total Annual Cost (20%)
Estimates your total yearly healthcare spending.

**Components:**
```
Total Cost = Premium × 12
           + Deductible (if likely to meet)
           + Estimated copays/coinsurance
           + Medication costs
           - HSA/FSA tax savings (if applicable)
```

**Normalization:**
- Lowest cost plan = 10 points
- Highest cost plan = 0 points
- Others scaled proportionally

### Metric 4: Financial Protection (10%)
Measures protection against catastrophic costs.

**Scoring Tiers:**
```
Excellent (10 points):
- Deductible ≤ $500 AND
- Out-of-pocket max ≤ $3,000

Good (7 points):
- Deductible ≤ $1,000 AND
- Out-of-pocket max ≤ $5,000

Fair (4 points):
- Deductible ≤ $2,000 AND
- Out-of-pocket max ≤ $7,000

Poor (0 points):
- Higher thresholds
```

### Metric 5: Administrative Simplicity (10%)
Evaluates ease of using the plan.

**Scoring:**
```
Start with 10 points, then subtract:
- -3 if referrals required
- -2 if frequent prior auth needed
- -2 if uses maximizer programs
- -1 if poor customer service ratings
- -1 if limited digital tools
```

### Metric 6: Plan Quality & Stability (5%)
Based on objective quality measures.

**Scoring:**
```
- CMS Star Rating × 2 (max 10 points)
- If no rating available: 5 points (neutral)
```

## 💻 Installation Guide

### System Requirements
- **OS**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)
- **Python**: 3.7, 3.8, 3.9, 3.10, or 3.11
- **Memory**: 2GB RAM minimum, 4GB recommended
- **Storage**: 100MB for installation + space for documents

### Detailed Installation

#### 1. Install Python
```bash
# Check if Python is installed
python --version

# If not installed, download from python.org
# Or use package manager:
# macOS: brew install python3
# Ubuntu: sudo apt-get install python3
# Windows: Download installer from python.org
```

#### 2. Clone Repository
```bash
# Using Git
git clone https://github.com/rzimmerman2022/healthplan-navigator.git
cd "healthgov resaerch projec t"

# Or download ZIP from GitHub and extract
```

#### 3. Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

#### 4. Install Dependencies
```bash
# Install production dependencies
pip install -r requirements.txt

# For development (includes testing tools)
pip install -r requirements-dev.txt
```

#### 5. Verify Installation
```bash
# Test the CLI
python -m healthplan_navigator.cli --help

# Run demo
python demo.py
```

### Docker Installation (Alternative)
```dockerfile
# Dockerfile included for containerized deployment
docker build -t healthplan-navigator .
docker run -v $(pwd)/personal_documents:/app/personal_documents healthplan-navigator
```

## 📖 Usage Examples

### Example 1: Basic Analysis with Demo
```bash
# Uses sample client profile and analyzes all documents in personal_documents/
python demo.py
```

### Example 2: CLI with Custom Client
```bash
# Create your client profile
cp sample_client.json my_profile.json
# Edit my_profile.json with your information

# Run analysis
python -m healthplan_navigator.cli --client my_profile.json --plans-dir ./personal_documents
```

### Example 3: Analyze Specific Plans
```bash
# Analyze only certain plan files
python -m healthplan_navigator.cli \
    --client my_profile.json \
    --plans ./personal_documents/BlueCross_Gold.pdf ./personal_documents/Aetna_Silver.pdf
```

### Example 4: Programmatic Usage
```python
from healthplan_navigator.analysis.engine import HealthPlanAnalyzer
from healthplan_navigator.core.models import Client

# Load client profile
with open('my_profile.json', 'r') as f:
    client_data = json.load(f)
client = Client(**client_data['client'])

# Initialize analyzer
analyzer = HealthPlanAnalyzer(client)

# Add plans
analyzer.add_plan_from_file('path/to/plan1.pdf')
analyzer.add_plan_from_file('path/to/plan2.docx')

# Run analysis
results = analyzer.analyze()

# Generate reports
analyzer.generate_reports('output/my_analysis/')
```

### Example 5: Batch Processing
```python
# Process multiple clients and plans
import glob
from pathlib import Path

# Get all client profiles
clients = glob.glob('clients/*.json')

# Get all plan documents
plans = glob.glob('plans/*.pdf') + glob.glob('plans/*.docx')

# Analyze each client against all plans
for client_file in clients:
    analyzer = HealthPlanAnalyzer.from_file(client_file)
    
    for plan_file in plans:
        analyzer.add_plan_from_file(plan_file)
    
    results = analyzer.analyze()
    output_dir = f'output/{Path(client_file).stem}/'
    analyzer.generate_reports(output_dir)
```

## 🔧 Configuration

### Client Profile Structure
```json
{
  "client": {
    "personal": {
      "full_name": "Your Name",
      "dob": "YYYY-MM-DD",
      "zipcode": "12345",
      "household_size": 2,
      "annual_income": 75000,
      "csr_eligible": false
    },
    "medical_profile": {
      "providers": [
        {
          "name": "Dr. Primary Care",
          "specialty": "Primary Care",
          "priority": "must-keep",
          "visit_frequency": 4
        }
      ],
      "medications": [
        {
          "name": "Medication Name",
          "dosage": "10mg",
          "frequency": "Daily",
          "annual_doses": 365,
          "manufacturer_program": {
            "exists": true,
            "type": "copay-card",
            "max_benefit": 10000,
            "expected_copay": 5
          }
        }
      ],
      "special_treatments": [
        {
          "name": "Physical Therapy",
          "frequency": 12,
          "allowed_cost": 150
        }
      ]
    },
    "priorities": {
      "keep_providers": 5,
      "minimize_total_cost": 4,
      "predictable_costs": 3,
      "avoid_prior_auth": 4,
      "simple_admin": 3
    }
  }
}
```

### Priority Weights (1-5 scale)
- **5**: Critical - Must have
- **4**: Very Important
- **3**: Important
- **2**: Nice to have
- **1**: Low priority

### Environment Variables
```bash
# Optional configuration
export HEALTHPLAN_OUTPUT_DIR=/custom/output/path
export HEALTHPLAN_LOG_LEVEL=DEBUG
export HEALTHPLAN_MAX_WORKERS=4
```

## 📄 Output Formats

### 1. Executive Summary (Markdown)
```markdown
# Healthcare Plan Analysis Report
Generated: 2025-01-15 10:30:00

## Top Recommendation
**BlueCross Gold HMO** - Overall Score: 8.7/10
- Best balance of provider coverage and cost
- All must-keep providers in-network
- Reasonable medication coverage

## Key Findings
1. Provider Coverage: 3 of 3 plans cover your PCP
2. Medication Costs: Vary from $1,200-$3,600/year
3. Total Annual Costs: Range from $8,400-$12,000
```

### 2. Scoring Matrix (CSV)
```csv
Plan Name,Provider Score,Medication Score,Cost Score,Protection Score,Simplicity Score,Quality Score,Overall Score
BlueCross Gold,10.0,8.5,7.2,8.0,7.5,8.0,8.7
Aetna Silver,8.0,9.0,8.5,6.0,8.0,7.0,8.1
United Bronze,6.0,7.0,9.5,4.0,9.0,7.5,7.3
```

### 3. Interactive Dashboard (HTML)
- Bar charts comparing metric scores
- Cost breakdown pie charts
- Provider network coverage maps
- Medication formulary tables
- Responsive design for mobile viewing

### 4. Raw Data Export (JSON)
```json
{
  "analysis_date": "2025-01-15T10:30:00",
  "client_id": "sample_client",
  "plans_analyzed": 3,
  "results": [
    {
      "plan_name": "BlueCross Gold HMO",
      "scores": {
        "provider_network": 10.0,
        "medication_coverage": 8.5,
        "total_cost": 7.2,
        "financial_protection": 8.0,
        "administrative_simplicity": 7.5,
        "plan_quality": 8.0,
        "overall": 8.7
      },
      "details": {
        "in_network_providers": ["Dr. Chen", "Dr. Anderson"],
        "covered_medications": ["Metformin", "Lisinopril"],
        "annual_cost_estimate": 9600
      }
    }
  ]
}
```

## 🔍 API Documentation

### Core Classes

#### Client Class
```python
class Client:
    """Represents a healthcare consumer profile"""
    
    def __init__(self, personal, medical_profile, priorities):
        self.personal = PersonalInfo(**personal)
        self.medical_profile = MedicalProfile(**medical_profile)
        self.priorities = Priorities(**priorities)
    
    def get_must_keep_providers(self):
        """Returns list of providers marked as must-keep"""
        
    def calculate_expected_utilization(self):
        """Estimates annual healthcare utilization"""
```

#### Plan Class
```python
class Plan:
    """Represents a healthcare plan"""
    
    def __init__(self, name, network, formulary, costs):
        self.name = name
        self.network = Network(**network)
        self.formulary = Formulary(**formulary)
        self.costs = CostStructure(**costs)
    
    def is_provider_in_network(self, provider_name):
        """Checks if provider is in-network"""
        
    def get_medication_tier(self, medication_name):
        """Returns formulary tier for medication"""
```

#### HealthPlanAnalyzer Class
```python
class HealthPlanAnalyzer:
    """Main analysis engine"""
    
    def __init__(self, client):
        self.client = client
        self.plans = []
        self.results = None
    
    def add_plan_from_file(self, filepath):
        """Parses and adds plan from document"""
        
    def analyze(self):
        """Runs full analysis on all plans"""
        
    def generate_reports(self, output_dir):
        """Creates all report formats"""
```

### Utility Functions

#### Document Parsing
```python
def parse_pdf(filepath):
    """Extracts plan data from PDF"""
    
def parse_docx(filepath):
    """Extracts plan data from DOCX"""
    
def parse_json(filepath):
    """Loads plan data from JSON"""
```

#### Score Calculations
```python
def calculate_weighted_score(scores, weights):
    """Calculates weighted average of scores"""
    
def normalize_cost_score(costs):
    """Normalizes costs to 0-10 scale"""
```

## 🐛 Troubleshooting

### Common Issues

#### 1. PDF Parsing Errors
**Problem**: "Unable to extract text from PDF"
```bash
# Solution 1: Update pdfplumber
pip install --upgrade pdfplumber

# Solution 2: Check if PDF is scanned image
# Use OCR tool to convert to searchable PDF first
```

#### 2. Missing Provider Information
**Problem**: "Provider not found in network"
```python
# Solution: Check name formatting in client profile
# Use exact name as appears in plan documents
{
  "name": "Dr. Sarah Chen, MD",  # Include full credentials
  "specialty": "Internal Medicine"
}
```

#### 3. Memory Errors with Large Files
**Problem**: "MemoryError when processing large PDF"
```bash
# Solution: Process files individually
python -m healthplan_navigator.cli --client profile.json --plans plan1.pdf
python -m healthplan_navigator.cli --client profile.json --plans plan2.pdf
```

#### 4. Import Errors
**Problem**: "ModuleNotFoundError"
```bash
# Solution: Ensure proper installation
pip install -e .  # Install in development mode
# Or
python setup.py install  # Standard installation
```

### Debug Mode
```bash
# Enable debug logging
export HEALTHPLAN_LOG_LEVEL=DEBUG
python demo.py

# Or in code
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Getting Help
1. Check existing issues: https://github.com/rzimmerman2022/healthplan-navigator/issues
2. Review documentation in `docs/` folder
3. Enable debug mode for detailed logs
4. Create minimal reproducible example

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Areas for Contribution
1. **Document Parsers**: Support for new formats (XML, Excel)
2. **Scoring Metrics**: Additional factors (telehealth, mental health)
3. **Visualizations**: Enhanced dashboard components
4. **API Integrations**: Provider databases, drug pricing APIs
5. **Internationalization**: Support for non-US healthcare systems

### Development Setup
```bash
# Fork and clone repository
git clone https://github.com/YOUR_USERNAME/healthplan-navigator.git
cd "healthgov resaerch projec t"

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Check code style
flake8 healthplan_navigator/
black healthplan_navigator/
```

## 📅 Changelog

### Version 1.0.0 (2024-01-15)
**Initial Release**
- ✅ Core 6-metric scoring system
- ✅ PDF and DOCX document parsing
- ✅ Multiple output formats (MD, CSV, HTML, JSON)
- ✅ Sample client profile system
- ✅ Command-line interface
- ✅ Privacy-focused local processing

### Version 0.9.0 (2024-01-01) - Beta
**Beta Testing Release**
- 🔧 Basic scoring implementation
- 🔧 PDF parsing functionality
- 🔧 Simple report generation

### Roadmap for v1.1.0
- 🔜 Excel file support
- 🔜 Provider network API integration
- 🔜 Prescription drug price lookups
- 🔜 Multi-year cost projections
- 🔜 Family plan analysis
- 🔜 Dental/Vision plan support

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Healthcare.gov for standardized plan data formats
- Open source community for document parsing libraries
- Beta testers for valuable feedback

---

**Disclaimer**: This tool provides analysis to help inform healthcare plan decisions. Always verify plan details directly with insurers and Healthcare.gov before making final enrollment decisions. This is not medical or insurance advice.