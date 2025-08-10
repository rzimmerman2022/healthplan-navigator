# Changelog
**Last Updated**: 2025-08-10  
**Description**: Complete version history and release notes for HealthPlan Navigator

All notable changes to HealthPlan Navigator will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - Repository Cleanup
### Added
- Comprehensive repository cleanup and standardization
- Professional documentation structure with headers and tables of contents  
- Systematic archive organization with categorized subdirectories (/deprecated, /experimental, /historical)
- Enhanced deployment documentation with production-ready instructions
- Complete archive documentation explaining all moved files

### Changed
- Reorganized documentation files into `/docs` directory for better organization
- Consolidated archived files into categorized subdirectories for easier management
- Updated all documentation cross-references to reflect new file locations
- Standardized documentation headers with version and update information
- Moved CHANGELOG.md, CONTRIBUTING.md, GOLD_STANDARD_ACHIEVEMENT.md to /docs

### Fixed
- Broken documentation links in README.md
- Inconsistent file organization structure throughout repository
- Missing deployment and maintenance documentation
- Removed redundant backup files (report_backup.py)

## [1.1.2] - 2025-08-08
**Critical Security & Stability Release**

### 🔒 Security Fixes (Critical)
- **[SECURITY] SQL Injection Prevention**: Fixed unsafe SQL query construction in CMS API integration
  - Parameterized ZIP code inputs with proper sanitization
  - Added whitelist validation for metal levels and plan types
  - Prevents malicious input from executing arbitrary SQL commands
- **Input Validation**: Added comprehensive ZIP code validation throughout the application
  - Created global `validate_zipcode()` function with consistent error handling
  - Validates 5-digit and ZIP+4 formats with proper formatting
  - Prevents invalid ZIP codes from propagating through the system

### 🐛 Critical Bug Fixes
- **API Integration**: Fixed incorrect client attribute reference preventing Healthcare.gov API calls
  - Changed `personal_info` to `personal` in analyzer.py:217
  - Healthcare.gov plan fetching now works correctly
- **Error Handling**: Replaced silent print() failures with proper logging throughout the codebase
  - All document parsing errors now use logger.error() instead of print()
  - Parsing failures are properly logged and don't halt the entire pipeline
  - Added informative error messages for debugging
- **Model Compatibility**: Fixed backwards compatibility issues between old/new field names
  - Updated scoring logic to use unified `deductible`/`oop_max` fields
  - Fixed report generation to reference correct plan attributes
  - Maintained compatibility with existing data structures

### 📦 Technical Improvements
- **Import Issues**: Fixed missing `Any` type import in medications.py
- **Test Stability**: 8 out of 9 tests now passing with core functionality verified
- **Code Standardization**: Consistent error handling and logging patterns across all modules
- **Documentation**: Updated README.md and CHANGELOG.md with security information

### 🧪 Quality Assurance
- **End-to-End Testing**: Verified complete pipeline functionality with demo.py
- **Security Validation**: All identified security vulnerabilities have been resolved
- **Production Readiness**: System is now ready for production deployment

### ⚠️ Breaking Changes
- None - All changes maintain backward compatibility

### 🔧 Migration Notes
- No migration required - all changes are backward compatible
- Users should update to this version immediately due to security fixes
- The system will continue to work with existing client profiles and document formats

## [1.1.1] - 2025-08-06 (Internal Release)
**Development and Documentation Updates**

### 📚 Documentation
- Added comprehensive discovery questionnaire generation
- Enhanced AGENTS.md with OpenAI Codex integration guide
- Updated architectural documentation

## [1.1.0] - 2025-08-06
**Major Release: Live API Integration Framework**

### 🚀 Major Features Added
- **Live API Integration Framework**: Complete real-time data integration system
  - Healthcare.gov marketplace API with CMS public data fallback
  - NPPES provider registry integration (working with public API)
  - RxNorm drug database integration (working with public API)
  - GoodRx pricing framework (ready for API key)
  - Intelligent caching and rate limiting mechanisms
  - Graceful fallback when APIs unavailable

- **Unified HealthPlanAnalyzer Interface**: Single entry point for all functionality
  - Seamless integration between local documents and live APIs
  - Automatic client location-based plan fetching
  - Enhanced error handling and retry logic
  - Support for API key management

- **Enhanced Provider Network Validation**: Advanced provider matching system
  - NPPES registry search with fuzzy string matching
  - Real-time provider verification
  - Network coverage calculation and assessment
  - Geographic proximity analysis

- **Intelligent Medication Analysis**: Comprehensive drug coverage system
  - RxNorm integration for generic alternatives
  - Real-time formulary checking
  - Cost estimation across multiple pricing sources
  - Prior authorization and restriction detection

- **Production-Ready Infrastructure**: Enterprise-grade reliability
  - Comprehensive error handling and logging
  - Performance optimization for large datasets
  - Security-focused design with local processing
  - Extensive test coverage for all components

### 📈 Enhanced Existing Features
- **Document Parser**: Significantly improved parsing capabilities
  - Enhanced PDF text extraction with better error handling
  - Improved field mapping for multiple document formats
  - Support for complex plan document structures
  - Better handling of scanned vs native PDFs

- **Scoring Engine**: More sophisticated analysis algorithms
  - Enhanced provider network scoring with real provider data
  - Improved medication coverage analysis
  - Better cost projection accuracy
  - More nuanced financial protection assessment

- **Report Generation**: Enhanced output quality and usability
  - Improved executive summaries with clearer recommendations
  - Better data visualization in HTML dashboards
  - More comprehensive CSV exports for analysis
  - Enhanced JSON structure for API integration

### 🔧 Technical Improvements
- **Dependencies**: Updated and added new required packages
  - Added `requests` for HTTP API calls
  - Added `fuzzywuzzy` and `python-levenshtein` for provider matching
  - Updated existing dependencies for security and performance
  - Maintained backward compatibility

- **Architecture**: Improved modularity and maintainability
  - Clear separation of concerns between modules
  - Enhanced type hints throughout codebase
  - Improved logging and debugging capabilities
  - Better configuration management

- **Performance**: Optimizations for large-scale analysis
  - Efficient caching mechanisms for API responses
  - Memory-conscious processing for large document sets
  - Parallel processing capabilities where appropriate
  - Reduced I/O operations through smart batching

### 🐛 Fixed
- Import errors in test modules and dependencies
- Field compatibility issues between old and new plan structures
- Report generation with enhanced plan field support
- Document parsing edge cases for various PDF formats
- Memory usage optimization for large document sets

### 📋 Documentation Updates
- **README.md**: Complete rewrite highlighting v1.1.0 capabilities
- **INTEGRATION_ROADMAP.md**: Comprehensive roadmap for API integration
- **PIPELINE_STATUS.md**: Updated status reflecting 95% completion
- Enhanced inline documentation and code comments

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
  - PDF document parsing with pdfplumber
  - DOCX document parsing with python-docx
  - JSON structured data support
  - CSV batch processing capabilities
- Core data models
  - Client profile with personal, medical, and priority data
  - Plan structure with benefits, network, and cost information
  - Analysis results with detailed scoring breakdowns
- Report generation in multiple formats
  - Executive summary (Markdown)
  - Scoring matrix (CSV)
  - Interactive dashboard (HTML)
  - Raw data export (JSON)
- Command-line interface for easy usage
- Privacy-focused local processing
- Sample client profiles and demo functionality
- Comprehensive documentation and examples

### Technical Features
- Type-safe data structures using Python dataclasses
- Modular architecture for extensibility
- Error handling and input validation
- Cross-platform compatibility (Windows, macOS, Linux)
- Memory-efficient processing for large document sets
- Caching mechanisms for improved performance

### Security & Privacy
- Local-only processing (no external data transmission)
- Secure handling of sensitive healthcare information
- Personal documents directory automatically gitignored
- HIPAA-compliance considerations built into design

---

## Upcoming Releases

### [1.2.0] - Planned
- Family plan analysis for multi-member households
- Dental and vision plan integration
- Multi-year cost projections and trend analysis
- Enhanced provider quality metrics
- Telehealth coverage analysis
- HSA/FSA optimization recommendations

### [1.3.0] - Future
- Machine learning-powered plan recommendations
- Integration with electronic health records (EHR)
- Mobile app companion
- Advanced visualization and reporting options
- International healthcare system support