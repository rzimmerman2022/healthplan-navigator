# Changelog

All notable changes to HealthPlan Navigator will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-08-06

### Added
- **HealthPlanAnalyzer Orchestrator**: Unified orchestration class for complete analysis pipeline
  - Single interface for plan ingestion, analysis, and reporting
  - Support for multiple input sources and output formats
  - Batch processing capabilities
  
- **Healthcare.gov API Integration Module**: Complete structure for marketplace integration
  - `HealthcareGovAPI` class with plan fetching methods
  - Provider network and formulary data retrieval
  - Caching mechanism for API responses
  - Rate limiting support
  
- **Provider Network Integration**: Comprehensive provider verification system
  - `ProviderNetworkIntegration` class with fuzzy matching
  - Network coverage calculation
  - Provider search functionality
  - Support for NPPES database integration (pending API access)
  
- **Medication Integration**: Drug formulary and pricing analysis
  - `MedicationIntegration` class for medication coverage checking
  - Price estimation across multiple sources
  - Generic alternative suggestions
  - Annual medication cost calculations
  
- **Enhanced Data Models**: Expanded plan and analysis models
  - `PlanType` enum (HMO, PPO, EPO, POS, HDHP)
  - `ProviderNetwork` and `DrugFormulary` dataclasses
  - Additional plan fields (copays, quality ratings)
  - Backwards compatibility for legacy field names
  
- **Comprehensive Test Suite**: End-to-end testing framework
  - Complete pipeline testing
  - Document parsing validation
  - Scoring engine verification
  - Report generation tests

### Changed
- **Document Parser**: Enhanced parsing capabilities
  - Made `parse_json()` and `parse_csv()` methods public
  - Improved field mapping for multiple formats
  - Better error handling and validation
  
- **Plan Model**: Updated with new fields
  - Added `plan_type`, `copay_*`, and rating fields
  - Unified deductible and OOP max field names
  - Backwards compatibility through `__post_init__`

### Fixed
- Import errors in test modules
- Field compatibility issues between old and new plan structures
- Report generation with new plan fields
- Document parsing for CSV files returning single plan instead of list

## [1.0.0] - 2024-01-08

### Added
- Initial release of HealthPlan Navigator
- 6-metric scoring system (0-10 scale) for healthcare plan analysis
  - Provider Network Adequacy (30% weight)
  - Medication Coverage & Access (25% weight)
  - Total Annual Cost (20% weight)
  - Financial Protection (10% weight)
  - Administrative Simplicity (10% weight)
  - Plan Quality & Stability (5% weight)
- Document parsing support for multiple formats
  - PDF parsing with OCR fallback
  - DOCX document parsing
  - JSON structured data import
  - CSV batch import
- Comprehensive analysis engine
  - Weighted scoring algorithm
  - Provider network analysis
  - Medication formulary checking
  - Cost projection modeling
  - Manufacturer assistance program integration
- Multiple output formats
  - Executive summary (Markdown)
  - Scoring matrix (CSV)
  - Interactive dashboard (HTML)
  - Complete data export (JSON)
- Command-line interface
  - Sample client mode for testing
  - Custom client data support
  - Batch processing capabilities
  - Flexible output options
- Demo script for quick start
- Comprehensive documentation
  - README with quick start guide
  - API documentation
  - Sample client data file
  - Contributing guidelines

### Technical Features
- Modular architecture for extensibility
- Type hints throughout codebase
- Configurable scoring weights
- Extensible document parser framework
- Error handling and validation

### Known Limitations
- PDF parsing accuracy depends on document quality
- Provider matching currently uses exact name matching
- Medication matching does not yet use RxNorm codes
- Plan ratings are currently using default values

## [Unreleased]

### Planned Features
- Healthcare.gov API integration
- Fuzzy matching for provider names
- RxNorm code integration for medications
- Machine learning for preference detection
- Web interface version
- Docker containerization
- Medicare plan support
- Dental and vision plan analysis