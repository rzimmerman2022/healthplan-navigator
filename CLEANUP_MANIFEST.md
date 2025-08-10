# Repository Cleanup Manifest
**Generated**: 2025-08-10  
**Purpose**: Document current repository structure and guide systematic reorganization

## Repository Analysis Summary

**Total Files Analyzed**: 100+  
**Main Entry Point**: `main.py` - Interactive healthcare plan analysis launcher  
**Core Source**: `src/healthplan_navigator/` - Main application package  
**Architecture**: Gold standard healthcare analytics pipeline with statistical validation  

## File Classification

### CORE (Essential for Operation)
**Primary Entry Points:**
- `main.py` - Interactive launcher with demo, analysis, and validation modes
- `src/healthplan_navigator/analyzer.py` - Main analysis orchestrator

**Core Library Files:**
- `src/healthplan_navigator/core/models.py` - Data models (Client, Plan, AnalysisReport)
- `src/healthplan_navigator/core/ingest.py` - Document parsing engine
- `src/healthplan_navigator/core/score.py` - Scoring algorithms
- `src/healthplan_navigator/analysis/engine.py` - 6-metric analysis engine
- `src/healthplan_navigator/output/report.py` - Multi-format reporting
- `src/healthplan_navigator/integrations/` - Healthcare.gov, NPPES, RxNorm APIs
- `src/healthplan_navigator/analytics/statistical_validator.py` - Gold standard validation
- `src/healthplan_navigator/__init__.py` - Package initialization
- `src/healthplan_navigator/cli.py` - Command line interface

**Configuration & Setup:**
- `setup.py` - Package installation and metadata
- `requirements.txt` - Production dependencies
- `requirements-dev.txt` - Development dependencies
- `LICENSE` - MIT license
- `.gitignore` (if exists)

**Working Example:**
- `examples/demo.py` - Complete demonstration script
- `examples/sample_client.json` - Sample client profile
- `examples/sample_form.html` - Sample healthcare form

**Test Infrastructure:**
- `tests/test_end_to_end.py` - End-to-end pipeline testing
- `tests/test_gold_standard.py` - Gold standard compliance validation
- `tests/__init__.py` - Test package initialization

### DOCUMENTATION (Keeps Important Knowledge)
**Primary Documentation:**
- `README.md` - Main project documentation (comprehensive)
- `CHANGELOG.md` - Version history
- `CONTRIBUTING.md` - Contribution guidelines
- `GOLD_STANDARD_ACHIEVEMENT.md` - Compliance certification

**Technical Documentation:**
- `docs/API.md` - API reference documentation
- `docs/ARCHITECTURE.md` - System architecture details
- `docs/healthcare_discovery_questionnaire.md` - Healthcare analysis questionnaire

**Report Templates:**
- `reports/templates/sample_analysis_export.json` - Analysis export template
- `reports/templates/sample_dashboard.html` - Dashboard template
- `reports/templates/sample_executive_summary.md` - Executive summary template
- `reports/templates/sample_scoring_matrix.csv` - Scoring matrix template
- `reports/README.md` - Reports directory documentation
- `examples/README.md` - Examples documentation
- `personal_documents/README.md` - Personal documents guide

### DEPRECATED (Old/Unused)
**Archive Directory Contents:**
- `archive/AGENTS.md` - Old agent documentation
- `archive/INTEGRATION_ROADMAP.md` - Historical roadmap
- `archive/PIPELINE_STATUS.md` - Old pipeline status
- `archive/mcp_analytics_implementation.md` - Old MCP documentation
- `archive/questionnaire_strategies.md` - Deprecated questionnaire approaches
- `archive/smart_questionnaire.md` - Old questionnaire design
- `archive/critical_15_questionnaire.md` - Deprecated critical questionnaire
- `archive/healthcare_pipeline_discovery_questionnaire.md` - Old pipeline questionnaire

**Generated Report Archives:**
- `archive/analysis_export_*.json` - Historical analysis exports (7 files)
- `archive/dashboard_*.html` - Historical dashboards (7 files)
- `archive/executive_summary_*.md` - Historical summaries (7 files)
- `archive/scoring_matrix_*.csv` - Historical scoring matrices (7 files)
- `archive/gold_standard_report.json` - Historical compliance report

**HTML Form Archives:**
- `archive/Healthcare_Form_Ehanced.html` - Typo in filename (Enhanced)
- `archive/healthcare-form-enhanced (1).html` - Duplicate enhanced forms (3 files)
- `archive/healthcare-form-fixed (1).html` - Fixed form versions (2 files)
- `archive/healthcare-form-visual (1).html` - Visual form versions (2 files)

**Image Archive:**
- `archive/IMG_1473.PNG` - Historical image file

### EXPERIMENTAL (Unfinished Features)
**Working Directories:**
- `cache/medications/` - Medication data cache (experimental caching)
- `cache/providers/` - Provider data cache (experimental caching)
- `claude_workspace/processed/` - Claude Code integration workspace
- `claude_workspace/queue/` - Processing queue
- `claude_workspace/results/` - Results storage

**Vector Storage:**
- `healthcare_vectors/chroma.sqlite3` - Vector database for RAG functionality

### REDUNDANT (Duplicate Functionality)
**Backup Files:**
- `src/healthplan_navigator/output/report_backup.py` - Backup of report.py
- `REPOSITORY_CLEANUP_SUMMARY.md` - Previous cleanup summary (will be replaced)

**Personal Documents (User Data - Keep but Organize):**
- `personal_documents/*.pdf` - User's healthcare plan documents (28 files)
- `personal_documents/*.docx` - User's healthcare plan documents (28 files)

## Dependencies Analysis

**Critical Dependencies:**
- pdfplumber>=0.9.0 - PDF processing
- python-docx>=0.8.11 - DOCX processing  
- pandas>=2.0.0 - Data analysis
- numpy>=1.24.0 - Numerical computations
- plotly>=5.15.0 - Visualization
- requests>=2.31.0 - API integration

**Import Chain Analysis:**
```
main.py → examples/demo.py → src/healthplan_navigator/*
main.py → src/healthplan_navigator/analyzer.py → core modules
main.py → tests/test_gold_standard.py → statistical validation
```

## Proposed Directory Structure

Based on analysis, the new structure will be:
```
/src/               - Main entry points and core source code
/docs/              - All documentation (consolidated)  
/tests/             - Test files and test data
/config/            - Configuration files and environment settings
/scripts/           - Utility and deployment scripts
/archive/           - Files pending review for deletion
  /archive/deprecated/     - Old/unused files
  /archive/experimental/   - Unfinished features  
  /archive/historical/     - Generated reports and logs
```

## Migration Notes

1. **main.py stays at root** - It's the primary entry point
2. **src/ reorganization minimal** - Current structure is logical
3. **Archive directory already exists** - Will reorganize contents
4. **Personal documents** - Move to /data or document in place
5. **Import statements** - Most will remain unchanged due to good current structure
6. **Test files** - Already in correct location

## Risks & Mitigation

**Low Risk Files** (safe to move):
- Documentation files
- Archive contents  
- Template files
- Cache directories

**Medium Risk Files** (test after moving):
- Example scripts
- Personal documents
- Workspace directories

**High Risk Files** (DO NOT MOVE):
- main.py (entry point)
- src/ package structure
- setup.py and requirements files
- Core test files

## Recommendations

1. **Preserve current src/ structure** - It follows Python best practices
2. **Consolidate documentation** - Move all .md files to /docs except README.md
3. **Clean archive systematically** - Many files can be safely removed
4. **Maintain backward compatibility** - Keep import paths working
5. **Document personal_documents** - Create clear usage instructions