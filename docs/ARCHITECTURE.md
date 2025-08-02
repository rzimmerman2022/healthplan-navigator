# HealthPlan Navigator Architecture

## System Overview

HealthPlan Navigator is designed as a modular, extensible system for healthcare plan analysis. The architecture follows clean code principles with clear separation of concerns.

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   CLI/Input     │     │   Web Interface │     │     API         │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                         │
         └───────────────────────┴─────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │    Analysis Engine      │
                    └────────────┬────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
┌───────┴────────┐    ┌──────────┴──────────┐   ┌────────┴────────┐
│  Document      │    │   Scoring Engine    │   │  Output         │
│  Parser        │    │   (6 Metrics)       │   │  Generator      │
└────────────────┘    └─────────────────────┘   └─────────────────┘
```

## Core Components

### 1. Document Ingestion Layer (`core.ingest`)

**Purpose**: Parse and normalize healthcare plan documents from various sources.

**Key Features**:
- Multi-format support (PDF, DOCX, JSON, CSV)
- Intelligent text extraction with regex patterns
- OCR fallback for scanned PDFs
- Batch processing capabilities

**Design Decisions**:
- Factory pattern for document parsers
- Unified `Plan` output model regardless of input format
- Graceful degradation when data is incomplete

### 2. Data Models (`core.models`)

**Purpose**: Define the domain entities and data structures.

**Key Entities**:
- `Client`: Consumer profile with medical needs
- `Plan`: Insurance plan details
- `ScoringMetrics`: 0-10 scale metrics
- `PlanAnalysis`: Complete analysis results

**Design Principles**:
- Immutable dataclasses for data integrity
- Type hints throughout for clarity
- Enums for constrained values
- Optional fields with sensible defaults

### 3. Scoring Engine (`core.score`)

**Purpose**: Implement the 6-metric scoring algorithm.

**Metrics and Weights**:
1. Provider Network (30%): In-network coverage
2. Medication Coverage (25%): Formulary and assistance
3. Total Cost (20%): Projected annual expenses
4. Financial Protection (10%): Deductible/OOPM limits
5. Administrative (10%): Ease of use
6. Plan Quality (5%): Star ratings

**Algorithm Design**:
- Each metric independently scored 0-10
- Weighted sum for final score
- Normalization against peer plans for cost
- Configurable weights for customization

### 4. Analysis Engine (`analysis.engine`)

**Purpose**: Orchestrate the analysis workflow.

**Responsibilities**:
- Coordinate scoring across all plans
- Generate comparative rankings
- Identify strengths and concerns
- Produce comprehensive reports

**Design Pattern**: 
- Facade pattern to simplify complex operations
- Separation of analysis from presentation

### 5. Output Generation (`output.report`)

**Purpose**: Create multiple report formats for different audiences.

**Output Types**:
- Executive Summary (Markdown): High-level recommendations
- Scoring Matrix (CSV): Detailed metrics table
- Interactive Dashboard (HTML): Visual comparisons
- Data Export (JSON): Complete analysis data

**Design Choices**:
- Template-based generation for consistency
- Embedded visualizations (Plotly offline)
- Self-contained outputs (no external dependencies)

## Data Flow

```
1. User Input
   ├── Client Profile (JSON)
   └── Plan Documents (PDF/DOCX/CSV)
           ↓
2. Document Parsing
   ├── Text Extraction
   ├── Pattern Matching
   └── Data Normalization
           ↓
3. Analysis Engine
   ├── Score Each Plan (6 metrics)
   ├── Calculate Weighted Totals
   └── Rank Plans
           ↓
4. Report Generation
   ├── Executive Summary
   ├── Detailed Matrix
   ├── Interactive Dashboard
   └── JSON Export
```

## Extension Points

### Adding New Metrics

1. Extend `ScoringMetrics` class
2. Add scoring method to `HealthPlanScorer`
3. Update weights dictionary
4. Modify report templates

Example:
```python
# Add telehealth metric
def _score_telehealth_coverage(self, plan: Plan) -> float:
    if plan.has_telehealth:
        return 10.0
    return 0.0
```

### Supporting New Document Formats

1. Add parser method to `DocumentParser`
2. Map to unified `Plan` model
3. Register file extension

Example:
```python
def _parse_xml(self, file_path: str) -> Optional[Plan]:
    # XML parsing logic
    pass
```

### Custom Analysis Rules

1. Subclass `AnalysisEngine`
2. Override analysis methods
3. Add domain-specific logic

## Performance Considerations

- **Batch Processing**: Parse multiple documents concurrently
- **Caching**: Store parsed plans to avoid re-parsing
- **Lazy Loading**: Load document content on-demand
- **Memory Efficiency**: Stream large files rather than loading entirely

## Security Considerations

- **Input Validation**: Sanitize all user inputs
- **File Access**: Restrict to specified directories
- **PII Protection**: No storage of personal health information
- **Secure Defaults**: Conservative scoring for missing data

## Testing Strategy

### Unit Tests
- Individual metric calculations
- Document parsing accuracy
- Model validation

### Integration Tests
- End-to-end analysis workflow
- Multi-format document handling
- Report generation

### Performance Tests
- Large document sets
- Concurrent processing
- Memory usage

## Future Architecture Enhancements

1. **Microservices**: Split into parsing, scoring, and reporting services
2. **API Gateway**: RESTful API for web integration
3. **Message Queue**: Async processing for large batches
4. **Database**: Persist analyses for historical comparison
5. **ML Pipeline**: Learn user preferences over time
6. **Cloud Native**: Containerization and orchestration