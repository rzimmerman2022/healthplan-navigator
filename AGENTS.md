# HealthPlan Navigator - AI Agent Guide

## 🩺 Project Overview
HealthPlan Navigator is a healthcare plan analysis system that uses 6-metric scoring to help users choose optimal health insurance plans. The system can process local documents and integrate with live APIs for real-time data.

## 🏗️ Architecture & Navigation

### Core Components
- `healthplan_navigator/` - Main package
  - `core/` - Data models, parsing, scoring
  - `integrations/` - API connections (Healthcare.gov, NPPES, RxNorm)  
  - `analysis/` - Analysis engine orchestration
  - `output/` - Report generation
  - `analyzer.py` - Unified interface (NEW in v1.1.0)

### Key Entry Points
- `demo.py` - Quick demo with sample data
- `healthplan_navigator/analyzer.py` - Main analysis interface
- `healthplan_navigator/cli.py` - Command-line interface

## 🧪 Testing & Validation

### Running Tests
```bash
# Basic functionality test
python demo.py

# Full test suite  
python -m pytest tests/ -v

# API connectivity test
python -c "
from healthplan_navigator.analyzer import HealthPlanAnalyzer
analyzer = HealthPlanAnalyzer()
print('Healthcare.gov API:', analyzer.healthcare_gov_api.validate_api_access())
"
```

### Test Data Locations
- `personal_documents/` - Sample healthcare plan documents (PDFs/DOCX)
- `sample_client.json` - Example client profile
- `tests/test_end_to_end.py` - Comprehensive test suite

## 🔧 Development Standards

### Code Quality
- **Type Hints**: Use throughout for better IDE support
- **Error Handling**: Comprehensive try/catch with meaningful messages
- **Logging**: Use module-level loggers, not print statements
- **Documentation**: Docstrings for all public methods

### Testing Approach
- **End-to-End**: Test complete workflows from document to report
- **Unit Tests**: Individual component validation
- **API Mocking**: Mock external API calls in tests
- **Error Cases**: Test failure scenarios and edge cases

### Performance Considerations
- **Memory**: Process large document sets in batches
- **Caching**: Cache API responses to reduce calls
- **Async**: Consider async for multiple API calls
- **Optimization**: Profile scoring calculations for large plan sets

## 📊 Core Functionality

### Analysis Workflow
1. **Client Profile**: Personal info, providers, medications, priorities
2. **Plan Ingestion**: Local documents OR live API data
3. **6-Metric Scoring**: Provider network (30%), medications (25%), cost (20%), protection (10%), admin (10%), quality (5%)
4. **Ranking**: Sort by weighted scores
5. **Reporting**: Multiple formats (Markdown, CSV, JSON, HTML)

### API Integration Status
- ✅ **NPPES Provider Registry**: Working (public API)
- ✅ **RxNorm Drug Database**: Working (public API)  
- ✅ **CMS Public Data**: Working (fallback for Healthcare.gov)
- 🔑 **Healthcare.gov Marketplace**: Ready (needs API key)
- 🔑 **GoodRx Pricing**: Ready (needs API key)

## 🐛 Common Issues & Solutions

### Import Errors
```bash
# Ensure package is installed in development mode
pip install -e .

# Or run from project root
export PYTHONPATH=/workspace/healthplan-navigator:$PYTHONPATH
```

### API Connection Issues
- **No API Keys**: System uses public APIs and cached data
- **Rate Limiting**: Automatic retry with exponential backoff
- **Network Issues**: Graceful fallback to local analysis

### Memory Issues with Large Files
```python
# Process in smaller batches
analyzer = HealthPlanAnalyzer()
for batch in batched_files:
    results = analyzer.analyze(client, batch)
    analyzer.clear_plans()  # Free memory
```

## 🎯 Recommended Testing Flow

### 1. Basic Functionality
```bash
python demo.py  # Should complete without errors
```

### 2. API Integration
```python
from healthplan_navigator.analyzer import HealthPlanAnalyzer
analyzer = HealthPlanAnalyzer()
# Test API connectivity (should work even without keys)
```

### 3. Document Processing
```bash
# Place test PDFs in personal_documents/ and run
python demo.py
```

### 4. Comprehensive Testing
```bash
pytest tests/ -v --tb=short
```

## 💡 Enhancement Ideas

### Immediate Improvements
- Add more document format support (Excel, XML)
- Enhance error messages with actionable suggestions
- Improve PDF parsing for complex layouts
- Add progress bars for long operations

### Advanced Features
- Family plan analysis (multi-member optimization)
- Provider quality ratings integration
- Prescription drug interaction checking
- Cost trend analysis over multiple years

## 🔍 Code Patterns to Follow

### Error Handling
```python
try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    return fallback_result()
```

### API Integration
```python
def api_call_with_fallback():
    try:
        return live_api_call()
    except APIError:
        logger.warning("API unavailable, using fallback")
        return cached_or_estimated_data()
```

### Logging
```python
import logging
logger = logging.getLogger(__name__)

logger.info("Starting analysis...")
logger.debug(f"Processing {len(plans)} plans")
logger.warning("API key not provided, using fallback")
```

This guide should help you navigate the codebase effectively and maintain the high standards established in v1.1.0!