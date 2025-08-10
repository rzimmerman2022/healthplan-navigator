# Contributing to HealthPlan Navigator

Welcome to the HealthPlan Navigator community! We're excited that you're interested in contributing to this healthcare plan analysis system. This comprehensive guide will help you get started and ensure your contributions align with our project standards.

## 📋 Table of Contents

1. [Code of Conduct](#-code-of-conduct)
2. [Getting Started](#-getting-started)
3. [Development Environment Setup](#-development-environment-setup)
4. [Contribution Types](#-contribution-types)
5. [Coding Standards](#-coding-standards)
6. [Testing Requirements](#-testing-requirements)
7. [Documentation Guidelines](#-documentation-guidelines)
8. [Pull Request Process](#-pull-request-process)
9. [Issue Reporting](#-issue-reporting)
10. [Community and Support](#-community-and-support)

## 🤝 Code of Conduct

### Our Pledge
We are committed to providing a welcoming, inclusive, and harassment-free environment for everyone, regardless of:
- Age, body size, disability, ethnicity, gender identity and expression
- Level of experience, nationality, personal appearance, race, religion
- Sexual identity and orientation

### Expected Behavior
- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior
- Harassment, discriminatory language, or personal attacks
- Publishing others' private information without permission
- Trolling or insulting/derogatory comments
- Other conduct that could be considered inappropriate

### Enforcement
Violations should be reported to rzimmerman2022@example.com. All complaints will be reviewed and investigated promptly and fairly.

## 🚀 Getting Started

### Prerequisites
Before contributing, ensure you have:
- Python 3.7 or higher installed
- Git for version control
- A GitHub account
- Basic understanding of healthcare insurance concepts (helpful but not required)

### First Steps
1. **Fork the Repository**
   ```bash
   # Navigate to https://github.com/rzimmerman2022/healthplan-navigator
   # Click "Fork" button in the top right
   ```

2. **Clone Your Fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/healthplan-navigator.git
   cd "healthgov resaerch projec t"
   ```

3. **Add Upstream Remote**
   ```bash
   git remote add upstream https://github.com/rzimmerman2022/healthplan-navigator.git
   ```

4. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 🛠️ Development Environment Setup

### 1. Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

### 3. Pre-commit Hooks (Recommended)
```bash
# Install pre-commit
pip install pre-commit

# Install the git hook scripts
pre-commit install

# (Optional) Run against all files
pre-commit run --all-files
```

### 4. Verify Installation
```bash
# Run tests
pytest

# Check code style
flake8 healthplan_navigator/
black healthplan_navigator/ --check

# Run the demo
python demo.py
```

## 📝 Contribution Types

### 1. Bug Fixes
- Fix existing issues labeled with `bug`
- Include tests that demonstrate the fix
- Reference the issue number in your PR

### 2. New Features
- Discuss major features in an issue first
- Implement with tests and documentation
- Consider backward compatibility

### 3. Documentation
- Improve existing documentation
- Add examples and use cases
- Fix typos and clarify explanations

### 4. Performance Improvements
- Profile code to identify bottlenecks
- Benchmark improvements
- Maintain functionality while optimizing

### 5. Test Coverage
- Add missing tests
- Improve test quality
- Cover edge cases

### 6. Refactoring
- Improve code structure
- Enhance readability
- Maintain existing functionality

## 💻 Coding Standards

### Python Style Guide

We follow PEP 8 with these specific requirements:

#### Code Formatting
```python
# Maximum line length: 100 characters
# Use 4 spaces for indentation (no tabs)
# Use blank lines to separate logical sections

# Good
def calculate_provider_score(
    client: Client,
    plan: Plan,
    weight: float = 0.3
) -> float:
    """Calculate provider network score."""
    must_keep = client.get_must_keep_providers()
    in_network = sum(
        1 for provider in must_keep
        if plan.is_provider_in_network(provider.name)
    )
    return (in_network / len(must_keep)) * 10 if must_keep else 10.0
```

#### Type Hints
All functions must include type hints:
```python
from typing import List, Dict, Optional, Union

def parse_plans(
    file_paths: List[str],
    options: Optional[Dict[str, Any]] = None
) -> List[Plan]:
    """Parse multiple plan files."""
    pass
```

#### Docstrings
Use Google-style docstrings for all public functions and classes:
```python
def analyze_medication_coverage(
    medications: List[Medication],
    formulary: Dict[str, str],
    manufacturer_programs: Optional[Dict[str, ManufacturerProgram]] = None
) -> MedicationAnalysis:
    """Analyze medication coverage for a list of medications.
    
    Evaluates each medication against the plan's formulary and available
    manufacturer assistance programs to determine coverage and costs.
    
    Args:
        medications: List of medications to analyze
        formulary: Plan's drug formulary mapping drug names to tiers
        manufacturer_programs: Optional mapping of drug names to programs
        
    Returns:
        MedicationAnalysis object containing:
            - coverage_scores: Individual medication scores
            - total_cost: Estimated annual medication cost
            - warnings: List of coverage concerns
            
    Raises:
        ValueError: If medications list is empty
        KeyError: If formulary tier is unrecognized
        
    Example:
        >>> meds = [Medication(name="Metformin", dosage="500mg")]
        >>> formulary = {"Metformin": "generic"}
        >>> analysis = analyze_medication_coverage(meds, formulary)
        >>> print(f"Score: {analysis.overall_score}")
    """
    if not medications:
        raise ValueError("Medications list cannot be empty")
    
    # Implementation here
    pass
```

#### Naming Conventions
```python
# Classes: PascalCase
class HealthPlanAnalyzer:
    pass

# Functions/Variables: snake_case
def calculate_annual_cost():
    total_cost = 0
    return total_cost

# Constants: UPPER_SNAKE_CASE
MAX_RETRY_ATTEMPTS = 3
DEFAULT_TIMEOUT = 30

# Private methods: leading underscore
def _internal_helper():
    pass
```

#### Import Organization
```python
# Standard library imports
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional

# Third-party imports
import pandas as pd
import numpy as np
from pdfplumber import PDF

# Local imports
from healthplan_navigator.core.models import Plan, Client
from healthplan_navigator.core.score import HealthPlanScorer
```

### Error Handling
```python
# Be specific with exceptions
try:
    plan = parse_pdf(file_path)
except FileNotFoundError:
    logger.error(f"Plan file not found: {file_path}")
    raise
except PDFParsingError as e:
    logger.warning(f"Failed to parse PDF: {e}")
    return None

# Always clean up resources
with open(file_path, 'r') as f:
    data = json.load(f)  # File automatically closed
```

### Logging
```python
import logging

logger = logging.getLogger(__name__)

# Use appropriate log levels
logger.debug("Detailed information for debugging")
logger.info("General informational messages")
logger.warning("Warning messages for potential issues")
logger.error("Error messages for failures")
logger.critical("Critical errors that may cause system failure")
```

## 🧪 Testing Requirements

### Test Structure
```
tests/
├── unit/                    # Unit tests for individual components
│   ├── test_models.py      # Test data models
│   ├── test_scoring.py     # Test scoring algorithms
│   ├── test_parsing.py     # Test document parsers
│   └── test_utils.py       # Test utility functions
├── integration/            # Integration tests
│   ├── test_analysis.py    # Test complete analysis workflow
│   ├── test_cli.py         # Test command-line interface
│   └── test_reports.py     # Test report generation
├── fixtures/               # Test data and fixtures
│   ├── sample_plans/       # Sample plan documents
│   ├── client_profiles/    # Test client profiles
│   └── expected_outputs/   # Expected test outputs
└── conftest.py            # Pytest configuration
```

### Writing Tests
```python
import pytest
from healthplan_navigator.core.models import Plan, Client
from healthplan_navigator.core.score import HealthPlanScorer

class TestHealthPlanScorer:
    """Test cases for HealthPlanScorer class."""
    
    @pytest.fixture
    def sample_client(self):
        """Fixture providing a sample client."""
        return Client(
            personal=PersonalInfo(
                full_name="Test User",
                dob="1980-01-01",
                zipcode="85001",
                household_size=2,
                annual_income=50000,
                csr_eligible=False
            ),
            medical_profile=MedicalProfile(
                providers=[],
                medications=[]
            ),
            priorities=Priorities(
                keep_providers=5,
                minimize_total_cost=4,
                predictable_costs=3,
                avoid_prior_auth=3,
                simple_admin=3
            )
        )
    
    @pytest.fixture
    def sample_plan(self):
        """Fixture providing a sample plan."""
        return Plan(
            plan_id="TEST001",
            issuer="Test Insurance",
            marketing_name="Test Gold HMO",
            plan_type="HMO",
            metal_level="Gold",
            monthly_premium=400.0,
            deductible_individual=1000.0,
            oop_max_individual=5000.0,
            copay_primary=20.0,
            copay_specialist=40.0,
            copay_emergency=250.0,
            coinsurance=0.2,
            network_providers=[],
            formulary={},
            requires_referral=True,
            star_rating=4.0
        )
    
    def test_provider_network_score_perfect(self, sample_client, sample_plan):
        """Test perfect provider network score when all providers in network."""
        # Arrange
        scorer = HealthPlanScorer()
        sample_client.medical_profile.providers = [
            Provider(name="Dr. Smith", specialty="Primary Care", 
                    priority="must-keep", visit_frequency=4)
        ]
        sample_plan.network_providers = ["Dr. Smith"]
        
        # Act
        score = scorer._score_provider_network(sample_client, sample_plan)
        
        # Assert
        assert score == 10.0
    
    def test_medication_coverage_with_formulary(self, sample_client, sample_plan):
        """Test medication scoring with formulary coverage."""
        # Arrange
        scorer = HealthPlanScorer()
        sample_client.medical_profile.medications = [
            Medication(name="Metformin", dosage="500mg", 
                      frequency="Daily", annual_doses=365)
        ]
        sample_plan.formulary = {"Metformin": "generic"}
        
        # Act
        score = scorer._score_medication_coverage(sample_client, sample_plan)
        
        # Assert
        assert score == 10.0
    
    @pytest.mark.parametrize("deductible,oop_max,expected_score", [
        (500, 3000, 10.0),   # Excellent protection
        (1000, 5000, 7.0),   # Good protection
        (2000, 7000, 4.0),   # Fair protection
        (5000, 10000, 0.0),  # Poor protection
    ])
    def test_financial_protection_scores(
        self, sample_plan, deductible, oop_max, expected_score
    ):
        """Test financial protection scoring with various thresholds."""
        # Arrange
        scorer = HealthPlanScorer()
        sample_plan.deductible_individual = deductible
        sample_plan.oop_max_individual = oop_max
        
        # Act
        score = scorer._score_financial_protection(sample_plan)
        
        # Assert
        assert score == expected_score
```

### Test Coverage Requirements
- Minimum 80% code coverage
- 100% coverage for critical paths (scoring, analysis)
- Cover edge cases and error conditions

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=healthplan_navigator --cov-report=html

# Run specific test file
pytest tests/unit/test_scoring.py

# Run tests matching pattern
pytest -k "test_medication"

# Run with verbose output
pytest -v

# Run in parallel
pytest -n auto
```

## 📚 Documentation Guidelines

### Code Documentation
1. **Module Level**: Describe the module's purpose
   ```python
   """Document parsing module for healthcare plans.
   
   This module provides parsers for various document formats including
   PDF, DOCX, JSON, and CSV. Each parser extracts plan information and
   normalizes it into the standard Plan model.
   """
   ```

2. **Class Level**: Explain the class's role
   ```python
   class DocumentParser:
       """Multi-format document parser for healthcare plans.
       
       Supports parsing of PDF, DOCX, JSON, and CSV files containing
       healthcare plan information. Automatically detects format and
       routes to appropriate parser.
       
       Attributes:
           pdf_parser: Parser instance for PDF files
           docx_parser: Parser instance for DOCX files
           json_parser: Parser instance for JSON files
           csv_parser: Parser instance for CSV files
           
       Example:
           >>> parser = DocumentParser()
           >>> plan = parser.parse_document("plan.pdf")
       """
   ```

3. **Function Level**: Use Google-style docstrings (as shown above)

### User Documentation
1. **README Updates**: Update for user-facing changes
2. **API Documentation**: Update docs/API.md for API changes
3. **Architecture Docs**: Update docs/ARCHITECTURE.md for structural changes
4. **Examples**: Add examples for new features

### Commit Messages
Follow the Conventional Commits specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only changes
- `style`: Code style changes (formatting, missing semi-colons, etc)
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `perf`: Performance improvement
- `test`: Adding missing tests or correcting existing tests
- `build`: Changes that affect the build system or external dependencies
- `ci`: Changes to CI configuration files and scripts
- `chore`: Other changes that don't modify src or test files

#### Examples
```bash
# Feature
feat(scoring): add telehealth coverage metric

- Added new metric for telehealth services
- Weighted at 5% in overall score
- Includes video visit coverage analysis

Closes #123

# Bug Fix
fix(parser): handle missing provider names in PDF

- Add null check for provider name extraction
- Default to "Unknown Provider" if name missing
- Log warning for missing provider information

Fixes #456

# Documentation
docs(api): add examples for custom scoring weights

- Added three examples showing weight customization
- Included validation requirements
- Updated return value documentation

# Performance
perf(analysis): optimize provider network scoring

- Cache provider lookups to reduce O(n²) to O(n)
- Add early return for empty provider lists
- Benchmark shows 3x speed improvement

Relates to #789
```

## 🔄 Pull Request Process

### 1. Before Creating a PR

#### Update Your Fork
```bash
# Fetch upstream changes
git fetch upstream

# Merge or rebase
git checkout main
git merge upstream/main

# Update your feature branch
git checkout feature/your-feature
git rebase main
```

#### Run Quality Checks
```bash
# Run tests
pytest

# Check code style
black healthplan_navigator/
flake8 healthplan_navigator/

# Check type hints
mypy healthplan_navigator/

# Build documentation
cd docs && make html
```

### 2. Creating the PR

#### PR Title Format
Use the same format as commit messages:
```
feat(scoring): add telehealth coverage metric
```

#### PR Description Template
```markdown
## Description
Brief description of what this PR does.

## Motivation and Context
Why is this change required? What problem does it solve?
If it fixes an open issue, link to the issue here.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## How Has This Been Tested?
Describe the tests that you ran to verify your changes.
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Screenshots (if appropriate)
Add screenshots to help explain your changes.

## Checklist
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published
```

### 3. PR Review Process

#### For Contributors
- Respond to feedback promptly
- Make requested changes in new commits (don't force-push during review)
- Mark conversations as resolved when addressed
- Be patient - reviews take time

#### For Reviewers
- Be constructive and specific
- Suggest improvements, don't just criticize
- Approve when ready, request changes when needed
- Consider functionality, performance, and maintainability

### 4. After PR Approval

#### Squash Commits (if requested)
```bash
# Interactive rebase
git rebase -i main

# Force push to your branch
git push --force-with-lease origin feature/your-feature
```

#### Celebrate!
Your contribution is now part of HealthPlan Navigator! 🎉

## 🐛 Issue Reporting

### Before Creating an Issue
1. **Search existing issues** to avoid duplicates
2. **Check the documentation** for answers
3. **Verify the problem** in the latest version

### Issue Templates

#### Bug Report
```markdown
**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
What you expected to happen.

**Actual behavior**
What actually happened.

**Environment:**
- OS: [e.g. Windows 10, macOS 12.1, Ubuntu 20.04]
- Python version: [e.g. 3.9.7]
- HealthPlan Navigator version: [e.g. 1.0.0]

**Additional context**
Add any other context, error messages, or screenshots.
```

#### Feature Request
```markdown
**Is your feature request related to a problem?**
A clear description of the problem.

**Describe the solution you'd like**
What you want to happen.

**Describe alternatives you've considered**
Other solutions you've thought about.

**Additional context**
Any other context or screenshots.
```

## 👥 Community and Support

### Getting Help
1. **Documentation**: Start with the docs
2. **Issues**: Search closed issues for solutions
3. **Discussions**: Ask questions in GitHub Discussions
4. **Stack Overflow**: Tag with `healthplan-navigator`

### Communication Channels
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Email**: rzimmerman2022@example.com (maintainer)

### Recognition
Contributors are recognized in:
- The CONTRIBUTORS.md file
- Release notes
- Annual contributor spotlight

## 🎯 Areas for Contribution

### High Priority
1. **Additional Document Parsers**
   - Excel file support
   - XML plan descriptions
   - API integrations

2. **Scoring Enhancements**
   - Dental/Vision plan support
   - Prescription drug pricing APIs
   - Multi-year cost projections

3. **User Interface**
   - Web-based analysis interface
   - Interactive plan comparison tool
   - Mobile-responsive reports

### Good First Issues
Look for issues labeled `good first issue` for:
- Documentation improvements
- Simple bug fixes
- Test additions
- Code style improvements

### Advanced Contributions
- Performance optimizations
- Machine learning features
- Cloud deployment support
- Internationalization

## 📅 Release Process

### Version Numbering
We follow Semantic Versioning (MAJOR.MINOR.PATCH):
- MAJOR: Breaking API changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

### Release Checklist
1. Update version in `healthplan_navigator/__init__.py`
2. Update CHANGELOG.md
3. Update documentation
4. Create release PR
5. Tag release after merge
6. Deploy to PyPI

## 🙏 Thank You!

Thank you for taking the time to contribute to HealthPlan Navigator. Your efforts help make healthcare decisions easier and more accessible for everyone. Together, we're building a tool that empowers people to make informed choices about their health insurance.

Happy coding! 🚀