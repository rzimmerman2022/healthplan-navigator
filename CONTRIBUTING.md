# Contributing to HealthPlan Navigator

Thank you for your interest in contributing to HealthPlan Navigator! This document provides guidelines and instructions for contributing to the project.

## 🤝 Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please be respectful and constructive in all interactions.

## 🐛 Reporting Issues

Before creating an issue:
1. Check existing issues to avoid duplicates
2. Use the issue templates provided
3. Include relevant information:
   - Python version
   - Operating system
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages/stack traces

## 🚀 Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following our coding standards
4. Write/update tests as needed
5. Update documentation
6. Commit with descriptive messages
7. Push to your fork
8. Open a Pull Request

### Commit Message Format

Use conventional commits format:
```
type(scope): subject

body

footer
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc)
- `refactor`: Code refactoring
- `test`: Test additions or changes
- `chore`: Build process or auxiliary tool changes

Example:
```
feat(scoring): add telehealth coverage metric

- Added new metric for telehealth services
- Weighted at 5% in overall score
- Includes video visit coverage analysis

Closes #123
```

## 📝 Coding Standards

### Python Style Guide

We follow PEP 8 with these additions:
- Maximum line length: 100 characters
- Use type hints for function parameters and returns
- Docstrings required for all public functions/classes (Google style)

Example:
```python
def calculate_score(plan: Plan, client: Client) -> float:
    """Calculate the overall score for a healthcare plan.
    
    Args:
        plan: The healthcare plan to score
        client: The client profile with requirements
        
    Returns:
        Float score between 0 and 10
        
    Raises:
        ValueError: If plan or client data is invalid
    """
    pass
```

### Testing

- Write tests for all new functionality
- Maintain test coverage above 80%
- Use pytest for testing
- Include both unit and integration tests

Test file structure:
```
tests/
├── unit/
│   ├── test_models.py
│   ├── test_scoring.py
│   └── test_parsing.py
└── integration/
    ├── test_analysis_engine.py
    └── test_cli.py
```

## 🏗️ Development Setup

1. Clone the repository:
```bash
git clone https://github.com/rzimmerman2022/healthplan-navigator.git
cd healthplan-navigator
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

4. Run tests:
```bash
pytest
```

5. Run linting:
```bash
flake8 healthplan_navigator/
black healthplan_navigator/ --check
```

## 📚 Documentation

- Update README.md for user-facing changes
- Update inline documentation for code changes
- Add examples for new features
- Update API documentation if applicable

## 🔄 Release Process

1. Update version in `healthplan_navigator/__init__.py`
2. Update CHANGELOG.md
3. Create release PR
4. Tag release after merge
5. Deploy to PyPI (maintainers only)

## 💡 Feature Requests

We welcome feature requests! Please:
1. Check if already requested
2. Provide clear use case
3. Explain expected behavior
4. Consider implementation approach

## 📧 Questions?

- Create a discussion issue
- Tag maintainers for urgent items
- Be patient - we're volunteers!

Thank you for contributing to making healthcare decisions easier! 🏥