# Personal Healthcare Documents Directory

This directory is designated for storing your personal healthcare plan documents for analysis by the HealthPlan Navigator system. All files in this directory are automatically excluded from version control to protect your privacy.

## 🔒 Privacy & Security Notice

**IMPORTANT**: This directory and all its contents are:
- ✅ Excluded from Git via `.gitignore`
- ✅ Never uploaded to GitHub or any remote repository
- ✅ Processed locally on your machine only
- ✅ Not shared with any external services

Your personal health information remains completely private and secure.

## 📁 Supported Document Types

The HealthPlan Navigator can analyze the following document formats:

### PDF Files (`.pdf`)
- **Best for**: Official plan summaries from Healthcare.gov
- **Examples**: 
  - Summary of Benefits and Coverage (SBC)
  - Plan brochures
  - Formulary documents
  - Provider directories

### Word Documents (`.docx`)
- **Best for**: Plan details and benefit summaries
- **Examples**:
  - Benefit descriptions
  - Coverage details
  - Cost breakdowns

### JSON Files (`.json`)
- **Best for**: Structured plan data exports
- **Examples**:
  - Healthcare.gov data exports
  - API responses
  - Custom plan data

### CSV Files (`.csv`)
- **Best for**: Batch plan comparisons
- **Examples**:
  - Multiple plan summaries
  - Provider lists
  - Formulary tables

## 📥 How to Add Your Documents

### Option 1: Direct File Copy
1. Download your plan documents from Healthcare.gov
2. Copy or move them into this `personal_documents` folder
3. No renaming required - the system reads any supported file

### Option 2: Drag and Drop
1. Open this folder in your file explorer
2. Drag plan documents directly into the folder
3. The system will automatically detect new files

### Option 3: Command Line
```bash
# Copy a single file
cp ~/Downloads/YourPlan.pdf ./personal_documents/

# Copy multiple PDFs
cp ~/Downloads/*.pdf ./personal_documents/

# Move files instead of copying
mv ~/Downloads/HealthPlan*.pdf ./personal_documents/
```

## 🚀 Running Analysis

Once your documents are in this folder, you have several options:

### Quick Analysis with Demo Script
```bash
# From the project root directory
python demo.py
```
This will:
- Use the sample client profile
- Analyze all documents in this folder
- Generate comprehensive reports in the `output` directory

### Custom Client Profile
```bash
# Edit sample_client.json first with your information
python -m healthplan_navigator.cli --client sample_client.json --plans-dir ./personal_documents
```

### Analyze Specific Files
```bash
# Analyze only certain files
python -m healthplan_navigator.cli --sample-client --plans ./personal_documents/Plan1.pdf ./personal_documents/Plan2.pdf
```

## 📊 What Happens to Your Documents

1. **Parsing**: Documents are read and key information is extracted
2. **Analysis**: Plans are scored across 6 metrics based on your needs
3. **Reporting**: Results are saved to the `output` folder
4. **Privacy**: Original documents remain unchanged in this folder

## 🗂️ Organization Tips

### Recommended Naming Convention (Optional)
While not required, organizing files can help you track analyses:
```
2025_Gold_BlueCross_HMO.pdf
2025_Silver_Aetna_PPO.pdf
2025_Bronze_United_EPO.pdf
```

### Subfolder Organization (Optional)
You can create subfolders for better organization:
```
personal_documents/
├── 2025_plans/
│   ├── gold_plans/
│   ├── silver_plans/
│   └── bronze_plans/
├── formularies/
└── provider_directories/
```

The system will recursively search all subfolders if you use the `--recursive` flag.

## ⚠️ Important Notes

### File Size Limits
- Maximum recommended file size: 50MB per document
- For larger files, consider splitting or extracting relevant pages

### Document Quality
- **Best results**: Official Healthcare.gov documents
- **Good results**: Insurance company plan summaries
- **Variable results**: Scanned documents (OCR may be needed)

### Sensitive Information
- The system only extracts plan-related information
- Personal identifiers in documents are ignored
- No data is stored permanently outside the `output` folder

## 🔧 Troubleshooting

### Document Not Recognized
If a document isn't being parsed:
1. Verify it's a supported format (.pdf, .docx, .json, .csv)
2. Check the file isn't corrupted
3. Ensure the file contains plan information

### Parsing Errors
If you see parsing errors:
1. The document might be password-protected
2. The PDF might be a scanned image (not searchable)
3. The format might not match expected patterns

### No Documents Found
If the analysis reports no documents:
1. Verify files are in this `personal_documents` folder
2. Check file extensions are correct
3. Ensure files aren't hidden (starting with .)

## 📝 Document Checklist

For best analysis results, try to include:

- [ ] **Plan Summary**: Basic plan details and costs
- [ ] **Benefits Summary**: What's covered and copays
- [ ] **Provider Directory**: Or list of your doctors
- [ ] **Drug Formulary**: List of covered medications
- [ ] **Cost Details**: Deductibles, out-of-pocket maximums

## 📋 Document Quality Best Practices

### Optimal Document Types (in order of preference)
1. **Plan Summary Documents** (Most Important)
   - Summary of Benefits and Coverage (SBC)
   - Plan Overview/Highlights
   - Benefit Details sheet

2. **Cost Information**
   - Premium schedules
   - Deductible and copay information
   - Out-of-pocket maximum details

3. **Network Information**
   - Provider directory excerpts
   - List of covered doctors/hospitals
   - Network tier information

4. **Prescription Coverage**
   - Drug formulary (covered medications)
   - Pharmacy network information
   - Prescription copay schedules

### File Quality Guidelines

#### ✅ Best Results
- Native digital PDFs (not scanned)
- Official Healthcare.gov documents
- Insurance company benefit summaries
- Clear, searchable text

#### ⚠️ Acceptable with Preprocessing
- High-quality scanned PDFs with OCR text
- DOCX files from insurance companies
- Screenshots converted to PDF with OCR

#### ❌ Avoid These Formats
- Low-resolution scanned images
- Photos of documents taken with phone
- Password-protected PDSs
- Corrupted or damaged files

### Naming Convention

For best results, use this naming pattern:
```
[Year]_[Tier]_[Insurer]_[Type]_[Identifier].pdf

Examples:
2025_Gold_BlueCross_HMO_Summary_Plan123.pdf
2025_Silver_Aetna_PPO_Benefits_XYZ456.pdf
2025_Bronze_Kaiser_HMO_Formulary_ABC789.pdf
```

### Security and Privacy

#### Before Adding Documents
- Remove or redact personal information if sharing for testing
- Use sample/demo names instead of real names
- Consider using pseudonyms for provider names

#### File Permissions (Linux/macOS)
```bash
# Secure file permissions
chmod 600 personal_documents/*.pdf  # Owner read/write only
chmod 700 personal_documents/       # Owner access only
```

#### Windows Security
- Right-click folder → Properties → Security
- Remove access for unnecessary users
- Consider encrypting sensitive documents

### Troubleshooting Document Issues

#### "Document Not Recognized"
1. Verify file format (.pdf, .docx, .json, .csv)
2. Check file isn't corrupted (try opening manually)
3. Ensure file contains plan information (not just marketing)

#### "Poor Text Extraction"
1. Document may be scanned image - run through OCR
2. Try converting DOCX to PDF
3. Check if PDF has selectable text

#### "Missing Information"
1. Add multiple documents per plan for complete picture
2. Ensure plan summary document is included
3. Check document dates match analysis year

### Document Organization Tips

#### Single Plan Analysis
```
personal_documents/
├── BlueCross_Gold_2025/
│   ├── summary.pdf
│   ├── benefits.pdf
│   └── formulary.pdf
```

#### Multi-Plan Comparison
```
personal_documents/
├── 2025_Gold_Plans/
│   ├── BlueCross_Gold_HMO.pdf
│   ├── Aetna_Gold_PPO.pdf
│   └── Kaiser_Gold_HMO.pdf
├── 2025_Silver_Plans/
│   ├── BlueCross_Silver_HMO.pdf
│   └── Aetna_Silver_PPO.pdf
```

## 🆘 Getting Help

If you need assistance:
1. **Document Issues**: Check file format and quality above
2. **Analysis Problems**: Review main README.md troubleshooting section
3. **Technical Support**: See CONTRIBUTING.md for reporting issues
4. **Examples**: Review demo.py script for usage patterns

### Quick Validation Checklist
- [ ] Files are in supported formats (.pdf, .docx, .json, .csv)
- [ ] Documents contain searchable text (not just images)
- [ ] Plan information is clearly identifiable
- [ ] File names follow recommended convention
- [ ] Personal information is secured appropriately

Remember: Your documents stay private and local. The HealthPlan Navigator system is designed to help you make informed healthcare decisions while protecting your personal information.

---

**Note**: This folder is created automatically when you clone the repository. If it's missing, you can create it manually:
```bash
mkdir personal_documents
```