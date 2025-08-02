# HealthPlan Navigator

A comprehensive healthcare plan analysis and ranking system that transforms complex insurance decisions into clear, actionable recommendations with 0-10 metric scoring.

## 🎯 What It Does

HealthPlan Navigator analyzes healthcare plans using a sophisticated 6-metric scoring system:

1. **Provider Network Adequacy** (30% weight) - Are your doctors in-network?
2. **Medication Coverage & Access** (25% weight) - Are your medications covered?
3. **Total Annual Cost** (20% weight) - What will you actually pay?
4. **Financial Protection** (10% weight) - How much risk do you face?
5. **Administrative Simplicity** (10% weight) - How easy is it to use?
6. **Plan Quality & Stability** (5% weight) - How good is the plan overall?

Each metric is scored 0-10, then weighted to create an overall ranking that helps you choose the best plan for your specific needs.

## 🚀 Quick Start

### Option 1: Run the Demo (Recommended)

```bash
# Install dependencies
pip install -r requirements.txt

# Run the demo with your actual plan documents
python demo.py
```

This will analyze all PDF and DOCX files in your directory and generate comprehensive reports.

### Option 2: Use the CLI

```bash
# With sample client data
python -m healthplan_navigator.cli --sample-client --plans-dir .

# With your own client data
python -m healthplan_navigator.cli --client sample_client.json --plans-dir .

# Analyze specific plan files
python -m healthplan_navigator.cli --sample-client --plans plan1.pdf plan2.pdf
```

## 📊 Output Formats

The system generates multiple report formats:

1. **Executive Summary** (Markdown) - Key recommendations and analysis
2. **Scoring Matrix** (CSV) - Detailed 0-10 scores for all metrics
3. **Interactive Dashboard** (HTML) - Charts and visualizations
4. **Data Export** (JSON) - Complete analysis data for further processing

## 📁 Project Structure

```
healthplan_navigator/
├── core/
│   ├── models.py          # Data models (Client, Plan, Scores)
│   ├── ingest.py          # Document parsing (PDF, DOCX, JSON, CSV)
│   └── score.py           # 6-metric scoring algorithm
├── analysis/
│   └── engine.py          # Main analysis orchestration
└── output/
    └── report.py          # Report generation in multiple formats
```

## 🏥 Your Healthcare Documents

The system can analyze these document types from Healthcare.gov:

- **PDF Files**: Plan summaries, benefit details, formularies
- **DOCX Files**: Plan documents, cost breakdowns
- **JSON Files**: Structured plan data
- **CSV Files**: Batch plan information

Your current directory contains real Healthcare.gov plan documents that will be automatically analyzed.

## 🎯 Scoring System Details

### Metric 1: Provider Network (30% weight)
- 10 points: All must-keep providers in-network
- 7 points: 80%+ must-keep providers in-network  
- 4 points: 50-79% must-keep providers in-network
- 0 points: <50% must-keep providers in-network
- Penalty: -2 points if referrals required

### Metric 2: Medication Coverage (25% weight)
- Covered on formulary: 10 points
- Not covered but manufacturer program available: 6 points
- Not covered, no program: 0 points
- Bonuses/penalties for prior auth and maximizer programs

### Metric 3: Total Cost (20% weight)
- Calculates: Premiums + Deductible + Copays + Medication costs
- Normalized: Lowest cost plan = 10 points, highest = 0 points

### Metric 4: Financial Protection (10% weight)
- 10 points: Deductible ≤ $500 AND OOPM ≤ $3,000
- 7 points: Deductible ≤ $1,000 AND OOPM ≤ $5,000
- 4 points: Deductible ≤ $2,000 AND OOPM ≤ $7,000
- 0 points: Higher thresholds

### Metric 5: Administrative Simplicity (10% weight)
- Start with 10 points, apply penalties:
- -3 if referrals required
- -2 if frequent prior auth needed
- -2 if uses maximizer programs
- -1 if poor plan rating

### Metric 6: Plan Quality (5% weight)
- Plan star rating × 2 (max 10 points)

## 📋 Sample Client Profile

The `sample_client.json` file contains a realistic client profile with:
- Personal information (income, location, household size)
- Healthcare providers with priorities
- Current medications
- Decision-making priorities

Customize this file to match your specific situation for more accurate recommendations.

## 🔧 Customization

### Adding Your Providers
Edit `sample_client.json` to include your actual doctors:

```json
{
  "name": "Dr. Your Doctor",
  "specialty": "Primary Care",
  "priority": "must-keep",
  "visit_frequency": 2
}
```

### Adding Your Medications
Include your current medications with manufacturer programs:

```json
{
  "name": "Your Medication",
  "dosage": "10mg",
  "frequency": "Daily",
  "annual_doses": 365,
  "manufacturer_program": {
    "exists": true,
    "type": "copay-card",
    "expected_copay": 5
  }
}
```

## 📈 Understanding Your Results

### Overall Scores (0-10 scale):
- **9.0-10.0**: Excellent choice
- **7.0-8.9**: Very good option
- **5.0-6.9**: Acceptable with trade-offs
- **3.0-4.9**: Poor fit for your needs
- **0.0-2.9**: Avoid this plan

### Key Recommendations:
1. **Top Plan**: Highest overall score balancing all factors
2. **Cost Leader**: Lowest estimated annual cost
3. **Provider Champion**: Best provider network coverage
4. **Medication Master**: Best formulary coverage

## 🛠️ Dependencies

- Python 3.7+
- pdfplumber (PDF parsing)
- python-docx (DOCX parsing)
- pandas (data analysis)
- plotly (visualizations)

## 🤝 Contributing

This system is designed to be extensible. You can:
- Add new document parsers for other formats
- Customize scoring weights based on priorities
- Add new metrics (e.g., telehealth coverage)
- Integrate with external APIs (provider databases, drug prices)

## 📞 Support

For questions about the analysis methodology or customizing the system for your specific needs, refer to the detailed comments in the source code or create an issue.

---

**Disclaimer**: This tool provides analysis to help inform your healthcare plan decision. Always verify plan details directly with insurers and Healthcare.gov before making final decisions.