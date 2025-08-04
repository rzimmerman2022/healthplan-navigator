# HealthPlan Navigator API Reference

## Table of Contents
1. [Overview](#overview)
2. [Core Modules](#core-modules)
   - [models](#healthplan_navigatorcoremodels)
   - [ingest](#healthplan_navigatorcoreingest)
   - [score](#healthplan_navigatorcorescore)
   - [engine](#healthplan_navigatoranalysisengine)
   - [report](#healthplan_navigatoroutputreport)
3. [Data Types](#data-types)
4. [Usage Examples](#usage-examples)
5. [Error Handling](#error-handling)
6. [Extension Guide](#extension-guide)
7. [API Patterns](#api-patterns)
8. [Performance Considerations](#performance-considerations)

## Overview

The HealthPlan Navigator API provides a comprehensive programmatic interface for healthcare plan analysis. This document details every class, method, and data structure available for developers and AI coding assistants.

### Package Structure
```
healthplan_navigator/
├── __init__.py           # Package exports
├── core/                 # Core functionality
│   ├── __init__.py
│   ├── models.py         # Data models
│   ├── ingest.py         # Document parsing
│   └── score.py          # Scoring algorithms
├── analysis/             # Analysis engine
│   ├── __init__.py
│   └── engine.py         # Orchestration
├── output/               # Report generation
│   ├── __init__.py
│   └── report.py         # Multi-format output
└── cli.py               # Command-line interface
```

## Core Modules

### `healthplan_navigator.core.models`

This module contains all data models used throughout the system. All models use Python dataclasses for type safety and immutability.

#### Classes

##### `PersonalInfo`
Represents client demographic and eligibility information.

```python
from dataclasses import dataclass

@dataclass
class PersonalInfo:
    """Client demographic and eligibility data
    
    Attributes:
        full_name (str): Client's full legal name
        dob (str): Date of birth in YYYY-MM-DD format
        zipcode (str): 5-digit ZIP code for plan availability
        household_size (int): Number of people in tax household
        annual_income (float): Total household income in USD
        csr_eligible (bool): Cost-sharing reduction eligibility
    
    Example:
        >>> info = PersonalInfo(
        ...     full_name="John Smith",
        ...     dob="1985-06-15",
        ...     zipcode="85001",
        ...     household_size=2,
        ...     annual_income=75000.0,
        ...     csr_eligible=False
        ... )
    """
    full_name: str
    dob: str
    zipcode: str
    household_size: int
    annual_income: float
    csr_eligible: bool
    
    def get_age(self) -> int:
        """Calculate current age from date of birth"""
        from datetime import datetime
        birth_date = datetime.strptime(self.dob, "%Y-%m-%d")
        today = datetime.today()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    
    def get_fpl_percentage(self) -> float:
        """Calculate income as percentage of Federal Poverty Level"""
        # 2025 FPL guidelines (simplified)
        fpl_base = 15060
        fpl_increment = 5380
        fpl = fpl_base + (fpl_increment * (self.household_size - 1))
        return (self.annual_income / fpl) * 100
```

##### `Provider`
Represents a healthcare provider with visit frequency.

```python
@dataclass
class Provider:
    """Healthcare provider details
    
    Attributes:
        name (str): Provider's full name (as appears in network directories)
        specialty (str): Medical specialty (e.g., "Primary Care", "Cardiology")
        priority (str): "must-keep" or "nice-to-keep"
        visit_frequency (int): Expected annual visits
    
    Example:
        >>> provider = Provider(
        ...     name="Dr. Sarah Chen, MD",
        ...     specialty="Primary Care",
        ...     priority="must-keep",
        ...     visit_frequency=4
        ... )
    """
    name: str
    specialty: str
    priority: str  # Literal["must-keep", "nice-to-keep"]
    visit_frequency: int
    
    def validate(self):
        """Validate provider data"""
        if self.priority not in ["must-keep", "nice-to-keep"]:
            raise ValueError(f"Invalid priority: {self.priority}")
        if self.visit_frequency < 0:
            raise ValueError("Visit frequency cannot be negative")
```

##### `ManufacturerProgram`
Represents pharmaceutical manufacturer assistance programs.

```python
@dataclass
class ManufacturerProgram:
    """Manufacturer assistance program details
    
    Attributes:
        exists (bool): Whether a program exists for this medication
        type (str): Program type - "copay-card", "patient-assistance", "discount"
        max_benefit (float): Maximum annual benefit amount
        expected_copay (float): Expected copay with program
    
    Example:
        >>> program = ManufacturerProgram(
        ...     exists=True,
        ...     type="copay-card",
        ...     max_benefit=20000.0,
        ...     expected_copay=5.0
        ... )
    """
    exists: bool
    type: Optional[str] = None
    max_benefit: Optional[float] = None
    expected_copay: Optional[float] = None
```

##### `Medication`
Represents a prescription medication with details.

```python
@dataclass
class Medication:
    """Prescription medication details
    
    Attributes:
        name (str): Medication name (brand or generic)
        dosage (str): Dosage strength (e.g., "10mg", "100mcg")
        frequency (str): Dosing frequency (e.g., "Daily", "Twice daily")
        annual_doses (int): Total doses per year
        manufacturer_program (Optional[ManufacturerProgram]): Assistance program info
    
    Example:
        >>> medication = Medication(
        ...     name="Metformin",
        ...     dosage="500mg",
        ...     frequency="Daily",
        ...     annual_doses=365,
        ...     manufacturer_program=None
        ... )
    """
    name: str
    dosage: str
    frequency: str
    annual_doses: int
    manufacturer_program: Optional[ManufacturerProgram] = None
    
    def calculate_monthly_doses(self) -> float:
        """Calculate average monthly doses"""
        return self.annual_doses / 12
```

##### `MedicalProfile`
Contains all medical information for a client.

```python
@dataclass
class MedicalProfile:
    """Complete medical profile including providers and medications
    
    Attributes:
        providers (List[Provider]): List of healthcare providers
        medications (List[Medication]): List of current medications
        special_treatments (List[SpecialTreatment]): Special medical treatments
    
    Example:
        >>> profile = MedicalProfile(
        ...     providers=[provider1, provider2],
        ...     medications=[med1, med2],
        ...     special_treatments=[]
        ... )
    """
    providers: List[Provider]
    medications: List[Medication]
    special_treatments: List[SpecialTreatment] = field(default_factory=list)
    
    def get_must_keep_providers(self) -> List[Provider]:
        """Get only must-keep providers"""
        return [p for p in self.providers if p.priority == "must-keep"]
    
    def get_total_visits(self) -> int:
        """Calculate total expected annual visits"""
        return sum(p.visit_frequency for p in self.providers)
```

##### `Client`
Complete client profile combining all information.

```python
@dataclass
class Client:
    """Complete healthcare consumer profile
    
    Attributes:
        personal (PersonalInfo): Demographic information
        medical_profile (MedicalProfile): Medical needs
        priorities (Priorities): Decision-making priorities
    
    Example:
        >>> client = Client(
        ...     personal=personal_info,
        ...     medical_profile=medical_profile,
        ...     priorities=priorities
        ... )
    
    Class Methods:
        from_json(file_path): Load client from JSON file
        from_dict(data): Create client from dictionary
    """
    personal: PersonalInfo
    medical_profile: MedicalProfile
    priorities: Priorities
    
    @classmethod
    def from_json(cls, file_path: str) -> 'Client':
        """Load client profile from JSON file
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Client instance
            
        Example:
            >>> client = Client.from_json("sample_client.json")
        """
        import json
        with open(file_path, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data['client'])
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Client':
        """Create client from dictionary
        
        Args:
            data: Dictionary with client data
            
        Returns:
            Client instance
        """
        return cls(
            personal=PersonalInfo(**data['personal']),
            medical_profile=MedicalProfile(**data['medical_profile']),
            priorities=Priorities(**data['priorities'])
        )
```

##### `Plan`
Represents a healthcare insurance plan.

```python
@dataclass
class Plan:
    """Healthcare insurance plan details
    
    Attributes:
        plan_id (str): Unique plan identifier
        issuer (str): Insurance company name
        marketing_name (str): Plan marketing name
        plan_type (str): HMO, PPO, EPO, or POS
        metal_level (str): Bronze, Silver, Gold, or Platinum
        monthly_premium (float): Monthly premium cost
        deductible_individual (float): Individual deductible
        oop_max_individual (float): Individual out-of-pocket maximum
        copay_primary (float): Primary care visit copay
        copay_specialist (float): Specialist visit copay
        copay_emergency (float): Emergency room copay
        coinsurance (float): Coinsurance percentage (0-1)
        network_providers (List[str]): In-network provider names
        formulary (Dict[str, str]): Drug name to tier mapping
        requires_referral (bool): Whether referrals are required
        star_rating (Optional[float]): CMS star rating (0-5)
        
    Example:
        >>> plan = Plan(
        ...     plan_id="12345",
        ...     issuer="BlueCross",
        ...     marketing_name="Gold HMO",
        ...     plan_type="HMO",
        ...     metal_level="Gold",
        ...     monthly_premium=450.0,
        ...     deductible_individual=1000.0,
        ...     oop_max_individual=5000.0,
        ...     copay_primary=20.0,
        ...     copay_specialist=40.0,
        ...     copay_emergency=250.0,
        ...     coinsurance=0.2,
        ...     network_providers=["Dr. Chen", "Dr. Smith"],
        ...     formulary={"Metformin": "generic"},
        ...     requires_referral=True,
        ...     star_rating=4.5
        ... )
    """
    plan_id: str
    issuer: str
    marketing_name: str
    plan_type: str  # HMO, PPO, EPO, POS
    metal_level: str  # Bronze, Silver, Gold, Platinum
    monthly_premium: float
    deductible_individual: float
    oop_max_individual: float
    copay_primary: float
    copay_specialist: float
    copay_emergency: float
    coinsurance: float
    network_providers: List[str]
    formulary: Dict[str, str]  # drug_name -> tier
    requires_referral: bool
    star_rating: Optional[float] = None
    
    def get_annual_premium(self) -> float:
        """Calculate annual premium cost"""
        return self.monthly_premium * 12
    
    def is_provider_in_network(self, provider_name: str) -> bool:
        """Check if provider is in network
        
        Args:
            provider_name: Provider's name to check
            
        Returns:
            True if provider is in network
        """
        return any(provider_name in network_provider 
                  for network_provider in self.network_providers)
    
    def get_drug_tier(self, drug_name: str) -> Optional[str]:
        """Get formulary tier for a medication
        
        Args:
            drug_name: Medication name
            
        Returns:
            Tier name or None if not covered
        """
        return self.formulary.get(drug_name)
```

##### `ScoringMetrics`
Contains all scoring metrics for a plan.

```python
@dataclass
class ScoringMetrics:
    """Scoring results for all 6 metrics (0-10 scale)
    
    All scores are on a 0-10 scale where:
    - 10 = Excellent
    - 7-9 = Good
    - 4-6 = Fair
    - 0-3 = Poor
    
    Attributes:
        provider_network_score (float): Provider coverage score
        medication_coverage_score (float): Medication access score
        total_cost_score (float): Total cost efficiency score
        financial_protection_score (float): Catastrophic protection score
        administrative_simplicity_score (float): Ease of use score
        plan_quality_score (float): Quality rating score
        weighted_total_score (float): Overall weighted score
        
    Example:
        >>> metrics = ScoringMetrics(
        ...     provider_network_score=9.0,
        ...     medication_coverage_score=8.5,
        ...     total_cost_score=7.0,
        ...     financial_protection_score=8.0,
        ...     administrative_simplicity_score=7.5,
        ...     plan_quality_score=8.0,
        ...     weighted_total_score=8.1
        ... )
    """
    provider_network_score: float = 0.0
    medication_coverage_score: float = 0.0
    total_cost_score: float = 0.0
    financial_protection_score: float = 0.0
    administrative_simplicity_score: float = 0.0
    plan_quality_score: float = 0.0
    weighted_total_score: float = 0.0
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            'provider_network': self.provider_network_score,
            'medication_coverage': self.medication_coverage_score,
            'total_cost': self.total_cost_score,
            'financial_protection': self.financial_protection_score,
            'administrative_simplicity': self.administrative_simplicity_score,
            'plan_quality': self.plan_quality_score,
            'overall': self.weighted_total_score
        }
```

##### `PlanAnalysis`
Complete analysis results for a single plan.

```python
@dataclass
class PlanAnalysis:
    """Complete analysis results for a plan
    
    Attributes:
        plan (Plan): The analyzed plan
        metrics (ScoringMetrics): All scoring metrics
        cost_breakdown (CostBreakdown): Detailed cost analysis
        strengths (List[str]): Key strengths of the plan
        concerns (List[str]): Potential concerns
        
    Example:
        >>> analysis = PlanAnalysis(
        ...     plan=plan,
        ...     metrics=metrics,
        ...     cost_breakdown=costs,
        ...     strengths=["All providers in network"],
        ...     concerns=["High deductible"]
        ... )
    """
    plan: Plan
    metrics: ScoringMetrics
    cost_breakdown: CostBreakdown
    strengths: List[str] = field(default_factory=list)
    concerns: List[str] = field(default_factory=list)
    
    def get_summary(self) -> str:
        """Generate one-line summary of plan"""
        return f"{self.plan.marketing_name}: {self.metrics.weighted_total_score:.1f}/10"
```

### `healthplan_navigator.core.ingest`

Document parsing functionality supporting multiple formats.

#### Classes

##### `DocumentParser`
Main parser class handling all document formats.

```python
class DocumentParser:
    """Multi-format document parser for healthcare plans
    
    Supports parsing of PDF, DOCX, JSON, and CSV files containing
    healthcare plan information. Automatically detects format and
    routes to appropriate parser.
    
    Example:
        >>> parser = DocumentParser()
        >>> plan = parser.parse_document("plan.pdf")
        >>> plans = parser.parse_batch("./documents/")
    """
    
    def __init__(self):
        """Initialize parser with default configuration"""
        self.pdf_parser = PDFParser()
        self.docx_parser = DOCXParser()
        self.json_parser = JSONParser()
        self.csv_parser = CSVParser()
    
    def parse_document(self, file_path: str) -> Optional[Plan]:
        """Parse a single document file
        
        Args:
            file_path: Path to document file
            
        Returns:
            Plan object or None if parsing fails
            
        Raises:
            ValueError: If file format is not supported
            IOError: If file cannot be read
            
        Example:
            >>> plan = parser.parse_document("BlueCross_Gold.pdf")
            >>> if plan:
            ...     print(f"Parsed {plan.marketing_name}")
        """
        if not os.path.exists(file_path):
            raise IOError(f"File not found: {file_path}")
        
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.pdf':
            return self.pdf_parser.parse(file_path)
        elif ext == '.docx':
            return self.docx_parser.parse(file_path)
        elif ext == '.json':
            return self.json_parser.parse(file_path)
        elif ext == '.csv':
            plans = self.csv_parser.parse(file_path)
            return plans[0] if plans else None
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    
    def parse_batch(self, directory_path: str, 
                   recursive: bool = False) -> List[Plan]:
        """Parse all supported documents in a directory
        
        Args:
            directory_path: Path to directory containing documents
            recursive: Whether to search subdirectories
            
        Returns:
            List of successfully parsed plans
            
        Example:
            >>> plans = parser.parse_batch("./personal_documents/")
            >>> print(f"Parsed {len(plans)} plans")
        """
        plans = []
        patterns = ['*.pdf', '*.docx', '*.json', '*.csv']
        
        for pattern in patterns:
            if recursive:
                files = glob.glob(os.path.join(directory_path, '**', pattern), 
                                recursive=True)
            else:
                files = glob.glob(os.path.join(directory_path, pattern))
            
            for file_path in files:
                try:
                    if pattern == '*.csv':
                        plans.extend(self.csv_parser.parse(file_path))
                    else:
                        plan = self.parse_document(file_path)
                        if plan:
                            plans.append(plan)
                except Exception as e:
                    print(f"Error parsing {file_path}: {e}")
        
        return plans
```

##### `PDFParser`
Specialized parser for PDF documents.

```python
class PDFParser:
    """PDF document parser using pdfplumber
    
    Extracts plan information from PDF documents using text extraction
    and pattern matching. Includes OCR fallback for scanned documents.
    
    Example:
        >>> parser = PDFParser()
        >>> plan = parser.parse("plan.pdf")
    """
    
    def parse(self, file_path: str) -> Optional[Plan]:
        """Parse PDF document
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Plan object or None if parsing fails
        """
        import pdfplumber
        
        try:
            with pdfplumber.open(file_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
                
                # Extract plan data using patterns
                plan_data = self._extract_plan_data(text)
                
                if plan_data:
                    return Plan(**plan_data)
                    
        except Exception as e:
            print(f"PDF parsing error: {e}")
            
        return None
    
    def _extract_plan_data(self, text: str) -> dict:
        """Extract plan data from text using regex patterns
        
        Args:
            text: Extracted text from PDF
            
        Returns:
            Dictionary of plan attributes
        """
        patterns = {
            'marketing_name': r'Plan Name:\s*(.+)',
            'issuer': r'Insurance Company:\s*(.+)',
            'monthly_premium': r'Monthly Premium:\s*\$?([\d,]+\.?\d*)',
            'deductible_individual': r'Individual Deductible:\s*\$?([\d,]+)',
            'oop_max_individual': r'Out-of-Pocket Maximum:\s*\$?([\d,]+)',
            # Add more patterns as needed
        }
        
        data = {}
        for field, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                # Convert numeric fields
                if field in ['monthly_premium', 'deductible_individual', 
                           'oop_max_individual']:
                    value = float(value.replace(',', ''))
                data[field] = value
        
        return data
```

### `healthplan_navigator.core.score`

Scoring algorithm implementation with detailed metric calculations.

#### Classes

##### `HealthPlanScorer`
Implements the 6-metric scoring system.

```python
class HealthPlanScorer:
    """Healthcare plan scoring engine
    
    Implements a sophisticated 6-metric scoring system where each
    metric is scored 0-10 and weighted to produce an overall score.
    
    Default Weights:
        - Provider Network: 30%
        - Medication Coverage: 25%
        - Total Cost: 20%
        - Financial Protection: 10%
        - Administrative Simplicity: 10%
        - Plan Quality: 5%
    
    Example:
        >>> scorer = HealthPlanScorer()
        >>> analysis = scorer.score_plan(client, plan, all_plans)
        >>> print(f"Overall score: {analysis.metrics.weighted_total_score}")
    """
    
    # Default metric weights (must sum to 1.0)
    DEFAULT_WEIGHTS = {
        'provider_network': 0.30,
        'medication_coverage': 0.25,
        'total_cost': 0.20,
        'financial_protection': 0.10,
        'administrative_simplicity': 0.10,
        'plan_quality': 0.05
    }
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """Initialize scorer with optional custom weights
        
        Args:
            weights: Custom metric weights (must sum to 1.0)
            
        Raises:
            ValueError: If weights don't sum to 1.0
        """
        self.weights = weights or self.DEFAULT_WEIGHTS
        
        if abs(sum(self.weights.values()) - 1.0) > 0.001:
            raise ValueError("Weights must sum to 1.0")
    
    def score_plan(self, client: Client, plan: Plan, 
                   all_plans: List[Plan]) -> PlanAnalysis:
        """Score a single plan for a client
        
        Args:
            client: Client profile with requirements
            plan: Plan to score
            all_plans: All plans for cost normalization
            
        Returns:
            Complete analysis with scores and insights
            
        Example:
            >>> analysis = scorer.score_plan(client, plan, all_plans)
            >>> print(f"Provider score: {analysis.metrics.provider_network_score}")
        """
        metrics = ScoringMetrics()
        
        # Calculate individual metrics
        metrics.provider_network_score = self._score_provider_network(client, plan)
        metrics.medication_coverage_score = self._score_medication_coverage(client, plan)
        metrics.total_cost_score = self._score_total_cost(client, plan, all_plans)
        metrics.financial_protection_score = self._score_financial_protection(plan)
        metrics.administrative_simplicity_score = self._score_administrative_simplicity(plan)
        metrics.plan_quality_score = self._score_plan_quality(plan)
        
        # Calculate weighted total
        metrics.weighted_total_score = self._calculate_weighted_total(metrics)
        
        # Generate cost breakdown
        cost_breakdown = self._calculate_cost_breakdown(client, plan)
        
        # Identify strengths and concerns
        strengths, concerns = self._analyze_plan_characteristics(client, plan, metrics)
        
        return PlanAnalysis(
            plan=plan,
            metrics=metrics,
            cost_breakdown=cost_breakdown,
            strengths=strengths,
            concerns=concerns
        )
    
    def _score_provider_network(self, client: Client, plan: Plan) -> float:
        """Score provider network coverage (0-10)
        
        Scoring logic:
        - 10 points: 100% must-keep providers in network
        - 7 points: 80-99% must-keep providers in network
        - 4 points: 50-79% must-keep providers in network
        - 0 points: <50% must-keep providers in network
        - -2 penalty if referrals required
        
        Args:
            client: Client with provider list
            plan: Plan with network
            
        Returns:
            Score from 0-10
        """
        must_keep = client.medical_profile.get_must_keep_providers()
        if not must_keep:
            return 10.0  # No providers to keep = perfect score
        
        in_network = sum(1 for p in must_keep 
                        if plan.is_provider_in_network(p.name))
        coverage_ratio = in_network / len(must_keep)
        
        # Base score from coverage
        if coverage_ratio == 1.0:
            score = 10.0
        elif coverage_ratio >= 0.8:
            score = 7.0 + (coverage_ratio - 0.8) * 15  # Linear 7-10
        elif coverage_ratio >= 0.5:
            score = 4.0 + (coverage_ratio - 0.5) * 6   # Linear 4-7
        else:
            score = coverage_ratio * 8  # Linear 0-4
        
        # Apply penalties
        if plan.requires_referral:
            score = max(0, score - 2.0)
        
        return round(score, 1)
    
    def _score_medication_coverage(self, client: Client, plan: Plan) -> float:
        """Score medication coverage and access (0-10)
        
        Scoring per medication:
        - Covered on formulary: 10 points
        - Not covered but manufacturer program: 6 points
        - Not covered, no assistance: 0 points
        
        Modifiers:
        - -2 if prior authorization likely
        - -3 if maximizer program used
        - +2 if preferred tier with low copay
        
        Args:
            client: Client with medication list
            plan: Plan with formulary
            
        Returns:
            Score from 0-10
        """
        medications = client.medical_profile.medications
        if not medications:
            return 10.0  # No medications = perfect score
        
        total_score = 0
        
        for med in medications:
            med_score = 0
            tier = plan.get_drug_tier(med.name)
            
            if tier:
                # Medication is covered
                if tier in ['generic', 'preferred-generic']:
                    med_score = 10
                elif tier in ['preferred-brand', 'preferred']:
                    med_score = 9
                elif tier == 'non-preferred':
                    med_score = 7
                elif tier == 'specialty':
                    med_score = 5
                else:
                    med_score = 6  # Unknown tier
            elif med.manufacturer_program and med.manufacturer_program.exists:
                # Not covered but has assistance
                med_score = 6
            else:
                # Not covered, no assistance
                med_score = 0
            
            # Apply modifiers
            if tier == 'specialty':
                med_score -= 2  # Prior auth likely
            
            total_score += max(0, med_score)
        
        return round(total_score / len(medications), 1)
    
    def _score_total_cost(self, client: Client, plan: Plan, 
                         all_plans: List[Plan]) -> float:
        """Score total annual cost (0-10, normalized)
        
        Calculates estimated total annual cost including:
        - Premiums
        - Deductible (if likely to meet)
        - Copays/coinsurance
        - Medication costs
        
        Then normalizes against all plans where:
        - Lowest cost = 10 points
        - Highest cost = 0 points
        - Others scaled proportionally
        
        Args:
            client: Client profile
            plan: Plan to score
            all_plans: All plans for normalization
            
        Returns:
            Normalized score from 0-10
        """
        # Calculate costs for this plan
        annual_cost = self._estimate_annual_cost(client, plan)
        
        # Calculate costs for all plans
        all_costs = [self._estimate_annual_cost(client, p) for p in all_plans]
        min_cost = min(all_costs)
        max_cost = max(all_costs)
        
        # Normalize
        if max_cost == min_cost:
            return 5.0  # All plans cost the same
        
        # Invert scale (lower cost = higher score)
        normalized = 1 - (annual_cost - min_cost) / (max_cost - min_cost)
        return round(normalized * 10, 1)
    
    def _estimate_annual_cost(self, client: Client, plan: Plan) -> float:
        """Estimate total annual healthcare costs
        
        Args:
            client: Client profile
            plan: Plan to analyze
            
        Returns:
            Estimated annual cost in USD
        """
        # Base premium
        annual_cost = plan.get_annual_premium()
        
        # Estimate utilization
        total_visits = client.medical_profile.get_total_visits()
        pcp_visits = sum(p.visit_frequency for p in client.medical_profile.providers 
                        if p.specialty == "Primary Care")
        specialist_visits = total_visits - pcp_visits
        
        # Add expected copays
        annual_cost += pcp_visits * plan.copay_primary
        annual_cost += specialist_visits * plan.copay_specialist
        
        # Estimate medication costs
        for med in client.medical_profile.medications:
            tier = plan.get_drug_tier(med.name)
            if tier:
                # Estimate copay based on tier
                copay_map = {
                    'generic': 10,
                    'preferred': 35,
                    'non-preferred': 70,
                    'specialty': 200
                }
                copay = copay_map.get(tier, 50)
                annual_cost += copay * 12  # Monthly fills
            elif med.manufacturer_program and med.manufacturer_program.exists:
                annual_cost += med.manufacturer_program.expected_copay * 12
            else:
                # Cash price estimate
                annual_cost += 150 * 12  # Default estimate
        
        # Consider deductible if high utilization expected
        if total_visits > 10:
            annual_cost += plan.deductible_individual * 0.75  # Likely to meet
        
        return annual_cost
```

### `healthplan_navigator.analysis.engine`

Main analysis orchestration engine.

#### Classes

##### `HealthPlanAnalyzer`
Coordinates the complete analysis workflow.

```python
class HealthPlanAnalyzer:
    """Main healthcare plan analysis engine
    
    Orchestrates the complete analysis workflow from document parsing
    through scoring to report generation. This is the primary entry
    point for programmatic usage.
    
    Example:
        >>> analyzer = HealthPlanAnalyzer(client)
        >>> analyzer.add_plan_from_file("plan1.pdf")
        >>> analyzer.add_plan_from_file("plan2.pdf")
        >>> results = analyzer.analyze()
        >>> analyzer.generate_reports("./output/")
    """
    
    def __init__(self, client: Client, scorer: Optional[HealthPlanScorer] = None):
        """Initialize analyzer with client profile
        
        Args:
            client: Client profile with requirements
            scorer: Optional custom scorer (uses default if None)
        """
        self.client = client
        self.scorer = scorer or HealthPlanScorer()
        self.parser = DocumentParser()
        self.plans = []
        self.results = None
    
    @classmethod
    def from_file(cls, client_file: str, 
                  scorer: Optional[HealthPlanScorer] = None) -> 'HealthPlanAnalyzer':
        """Create analyzer from client JSON file
        
        Args:
            client_file: Path to client JSON file
            scorer: Optional custom scorer
            
        Returns:
            Configured analyzer instance
            
        Example:
            >>> analyzer = HealthPlanAnalyzer.from_file("client.json")
        """
        client = Client.from_json(client_file)
        return cls(client, scorer)
    
    def add_plan_from_file(self, file_path: str) -> bool:
        """Add a plan from document file
        
        Args:
            file_path: Path to plan document
            
        Returns:
            True if successfully added
            
        Example:
            >>> success = analyzer.add_plan_from_file("BlueCross_Gold.pdf")
        """
        try:
            plan = self.parser.parse_document(file_path)
            if plan:
                self.plans.append(plan)
                return True
        except Exception as e:
            print(f"Error adding plan from {file_path}: {e}")
        return False
    
    def add_plan(self, plan: Plan):
        """Add a plan directly
        
        Args:
            plan: Plan object to add
            
        Example:
            >>> analyzer.add_plan(my_plan)
        """
        self.plans.append(plan)
    
    def add_plans_from_directory(self, directory: str, recursive: bool = False):
        """Add all plans from a directory
        
        Args:
            directory: Directory containing plan documents
            recursive: Whether to search subdirectories
            
        Example:
            >>> analyzer.add_plans_from_directory("./plans/", recursive=True)
        """
        parsed_plans = self.parser.parse_batch(directory, recursive)
        self.plans.extend(parsed_plans)
        print(f"Added {len(parsed_plans)} plans from {directory}")
    
    def analyze(self) -> 'AnalysisResults':
        """Run complete analysis on all plans
        
        Performs scoring, ranking, and insight generation for all
        added plans. Results are cached for report generation.
        
        Returns:
            AnalysisResults object with complete findings
            
        Raises:
            ValueError: If no plans added
            
        Example:
            >>> results = analyzer.analyze()
            >>> print(f"Best plan: {results.get_top_plan().plan.marketing_name}")
        """
        if not self.plans:
            raise ValueError("No plans to analyze. Add plans first.")
        
        # Score all plans
        analyses = []
        for plan in self.plans:
            analysis = self.scorer.score_plan(self.client, plan, self.plans)
            analyses.append(analysis)
        
        # Sort by overall score
        analyses.sort(key=lambda a: a.metrics.weighted_total_score, reverse=True)
        
        # Generate insights
        insights = self._generate_insights(analyses)
        
        # Create results
        self.results = AnalysisResults(
            client=self.client,
            plan_analyses=analyses,
            insights=insights,
            analysis_date=datetime.now()
        )
        
        return self.results
    
    def _generate_insights(self, analyses: List[PlanAnalysis]) -> Dict[str, Any]:
        """Generate high-level insights from analyses
        
        Args:
            analyses: Sorted list of plan analyses
            
        Returns:
            Dictionary of insights
        """
        insights = {
            'total_plans_analyzed': len(analyses),
            'score_range': {
                'highest': analyses[0].metrics.weighted_total_score,
                'lowest': analyses[-1].metrics.weighted_total_score
            },
            'best_by_category': self._find_best_by_category(analyses),
            'key_findings': self._generate_key_findings(analyses),
            'warnings': self._generate_warnings(analyses)
        }
        
        return insights
    
    def _find_best_by_category(self, analyses: List[PlanAnalysis]) -> dict:
        """Find best plans by specific criteria
        
        Args:
            analyses: All plan analyses
            
        Returns:
            Dictionary of category winners
        """
        return {
            'overall': analyses[0],
            'lowest_cost': min(analyses, 
                             key=lambda a: a.cost_breakdown.total_annual_cost),
            'best_providers': max(analyses, 
                                key=lambda a: a.metrics.provider_network_score),
            'best_medications': max(analyses, 
                                  key=lambda a: a.metrics.medication_coverage_score),
            'best_protection': max(analyses, 
                                 key=lambda a: a.metrics.financial_protection_score)
        }
    
    def generate_reports(self, output_dir: str):
        """Generate all report formats
        
        Creates comprehensive reports in multiple formats:
        - Executive summary (Markdown)
        - Scoring matrix (CSV)
        - Interactive dashboard (HTML)
        - Raw data export (JSON)
        
        Args:
            output_dir: Directory for output files
            
        Raises:
            ValueError: If analysis not run yet
            
        Example:
            >>> analyzer.generate_reports("./output/2024-01-15/")
        """
        if not self.results:
            raise ValueError("No results to report. Run analyze() first.")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize report generator
        generator = ReportGenerator()
        
        # Generate all formats
        generator.generate_executive_summary(self.results, output_dir)
        generator.generate_scoring_matrix_csv(self.results, output_dir)
        generator.generate_html_dashboard(self.results, output_dir)
        generator.generate_json_export(self.results, output_dir)
        
        print(f"Reports generated in: {output_dir}")
```

### `healthplan_navigator.output.report`

Report generation in multiple formats.

#### Classes

##### `ReportGenerator`
Generates reports in various formats.

```python
class ReportGenerator:
    """Multi-format report generator
    
    Transforms analysis results into consumable reports in various
    formats suitable for different audiences and use cases.
    
    Supported formats:
    - Markdown: Human-readable executive summary
    - CSV: Detailed scoring matrix for spreadsheets
    - HTML: Interactive dashboard with visualizations
    - JSON: Complete data export for integration
    
    Example:
        >>> generator = ReportGenerator()
        >>> generator.generate_all_reports(results, "./output/")
    """
    
    def generate_all_reports(self, results: AnalysisResults, output_dir: str):
        """Generate all report formats
        
        Args:
            results: Analysis results to report
            output_dir: Directory for output files
        """
        self.generate_executive_summary(results, output_dir)
        self.generate_scoring_matrix_csv(results, output_dir)
        self.generate_html_dashboard(results, output_dir)
        self.generate_json_export(results, output_dir)
    
    def generate_executive_summary(self, results: AnalysisResults, 
                                 output_dir: str) -> str:
        """Generate executive summary in Markdown
        
        Creates a human-readable summary with:
        - Top recommendations
        - Key findings
        - Plan comparisons
        - Important warnings
        
        Args:
            results: Analysis results
            output_dir: Output directory
            
        Returns:
            Path to generated file
            
        Example:
            >>> path = generator.generate_executive_summary(results, "./output/")
            >>> print(f"Summary saved to: {path}")
        """
        output_path = os.path.join(output_dir, "executive_summary.md")
        
        with open(output_path, 'w') as f:
            # Write header
            f.write("# Healthcare Plan Analysis Report\n\n")
            f.write(f"Generated: {results.analysis_date.strftime('%Y-%m-%d %H:%M')}\n")
            f.write(f"Client: {results.client.personal.full_name}\n\n")
            
            # Top recommendation
            top_plan = results.get_top_plan()
            f.write("## 🏆 Top Recommendation\n\n")
            f.write(f"**{top_plan.plan.marketing_name}** ")
            f.write(f"(Score: {top_plan.metrics.weighted_total_score:.1f}/10)\n\n")
            
            # Why recommended
            f.write("### Why This Plan?\n")
            for strength in top_plan.strengths[:3]:
                f.write(f"- ✅ {strength}\n")
            f.write("\n")
            
            # Key metrics
            f.write("### Key Metrics\n")
            f.write(f"- **Monthly Premium**: ${top_plan.plan.monthly_premium:,.0f}\n")
            f.write(f"- **Annual Cost Estimate**: ${top_plan.cost_breakdown.total_annual_cost:,.0f}\n")
            f.write(f"- **Deductible**: ${top_plan.plan.deductible_individual:,.0f}\n")
            f.write(f"- **Out-of-Pocket Max**: ${top_plan.plan.oop_max_individual:,.0f}\n\n")
            
            # Alternatives
            f.write("## 🔄 Alternative Options\n\n")
            for i, analysis in enumerate(results.plan_analyses[1:3], 2):
                f.write(f"### {i}. {analysis.plan.marketing_name} ")
                f.write(f"(Score: {analysis.metrics.weighted_total_score:.1f}/10)\n")
                f.write(f"- **Best for**: {self._get_plan_strength(analysis)}\n")
                f.write(f"- **Monthly Premium**: ${analysis.plan.monthly_premium:,.0f}\n")
                f.write(f"- **Annual Cost**: ${analysis.cost_breakdown.total_annual_cost:,.0f}\n\n")
            
            # Category winners
            f.write("## 🏅 Best in Category\n\n")
            categories = results.insights['best_by_category']
            
            f.write(f"- **Lowest Cost**: {categories['lowest_cost'].plan.marketing_name} ")
            f.write(f"(${categories['lowest_cost'].cost_breakdown.total_annual_cost:,.0f}/year)\n")
            
            f.write(f"- **Best Provider Coverage**: {categories['best_providers'].plan.marketing_name} ")
            f.write(f"({categories['best_providers'].metrics.provider_network_score:.1f}/10)\n")
            
            f.write(f"- **Best Medication Coverage**: {categories['best_medications'].plan.marketing_name} ")
            f.write(f"({categories['best_medications'].metrics.medication_coverage_score:.1f}/10)\n\n")
            
            # Warnings
            if results.insights['warnings']:
                f.write("## ⚠️ Important Considerations\n\n")
                for warning in results.insights['warnings']:
                    f.write(f"- {warning}\n")
                f.write("\n")
            
            # Detailed comparison
            f.write("## 📊 Detailed Comparison\n\n")
            f.write("| Plan | Overall | Providers | Medications | Cost | Protection | Simplicity | Quality |\n")
            f.write("|------|---------|-----------|-------------|------|------------|------------|----------|\n")
            
            for analysis in results.plan_analyses[:5]:
                m = analysis.metrics
                f.write(f"| {analysis.plan.marketing_name[:20]} ")
                f.write(f"| **{m.weighted_total_score:.1f}** ")
                f.write(f"| {m.provider_network_score:.1f} ")
                f.write(f"| {m.medication_coverage_score:.1f} ")
                f.write(f"| {m.total_cost_score:.1f} ")
                f.write(f"| {m.financial_protection_score:.1f} ")
                f.write(f"| {m.administrative_simplicity_score:.1f} ")
                f.write(f"| {m.plan_quality_score:.1f} |\n")
        
        return output_path
```

## Data Types

### Enumerations

```python
from enum import Enum

class MetalLevel(Enum):
    """Health plan metal levels"""
    BRONZE = "Bronze"
    SILVER = "Silver"
    GOLD = "Gold"
    PLATINUM = "Platinum"

class PlanType(Enum):
    """Health plan types"""
    HMO = "HMO"
    PPO = "PPO"
    EPO = "EPO"
    POS = "POS"

class Priority(Enum):
    """Provider priority levels"""
    MUST_KEEP = "must-keep"
    NICE_TO_KEEP = "nice-to-keep"
```

### Type Aliases

```python
from typing import TypeAlias

# Common type aliases used throughout
PlanID: TypeAlias = str
ProviderName: TypeAlias = str
DrugName: TypeAlias = str
DrugTier: TypeAlias = str
Score: TypeAlias = float  # 0.0 to 10.0
Money: TypeAlias = float  # USD amount
Percentage: TypeAlias = float  # 0.0 to 1.0
```

## Usage Examples

### Example 1: Basic Analysis Flow

```python
from healthplan_navigator import HealthPlanAnalyzer, Client

# Load client profile
client = Client.from_json("sample_client.json")

# Create analyzer
analyzer = HealthPlanAnalyzer(client)

# Add plans from directory
analyzer.add_plans_from_directory("./personal_documents/")

# Run analysis
results = analyzer.analyze()

# Generate reports
analyzer.generate_reports("./output/analysis_2024-01-15/")

# Access results programmatically
top_plan = results.get_top_plan()
print(f"Recommended: {top_plan.plan.marketing_name}")
print(f"Score: {top_plan.metrics.weighted_total_score:.1f}/10")
print(f"Annual cost: ${top_plan.cost_breakdown.total_annual_cost:,.0f}")
```

### Example 2: Custom Scoring Weights

```python
from healthplan_navigator import HealthPlanAnalyzer, HealthPlanScorer, Client

# Create custom scorer emphasizing provider network
custom_weights = {
    'provider_network': 0.40,      # Increased from 0.30
    'medication_coverage': 0.20,   # Decreased from 0.25
    'total_cost': 0.20,           # Same
    'financial_protection': 0.10,  # Same
    'administrative_simplicity': 0.05,  # Decreased from 0.10
    'plan_quality': 0.05          # Same
}

scorer = HealthPlanScorer(weights=custom_weights)

# Use custom scorer in analysis
analyzer = HealthPlanAnalyzer(client, scorer=scorer)
```

### Example 3: Programmatic Plan Creation

```python
from healthplan_navigator.core.models import Plan

# Create plan manually (useful for testing or API integration)
plan = Plan(
    plan_id="CUSTOM-001",
    issuer="Custom Insurance Co",
    marketing_name="Custom Gold HMO",
    plan_type="HMO",
    metal_level="Gold",
    monthly_premium=475.00,
    deductible_individual=1500.00,
    oop_max_individual=6000.00,
    copay_primary=25.00,
    copay_specialist=50.00,
    copay_emergency=300.00,
    coinsurance=0.20,
    network_providers=["Dr. Smith", "Dr. Jones", "Medical Center"],
    formulary={
        "Metformin": "generic",
        "Lisinopril": "generic",
        "Insulin": "preferred"
    },
    requires_referral=True,
    star_rating=4.0
)

# Add to analyzer
analyzer.add_plan(plan)
```

### Example 4: Batch Processing Multiple Clients

```python
import os
from concurrent.futures import ProcessPoolExecutor

def analyze_client(client_file: str, plans_dir: str, output_base: str):
    """Analyze plans for a single client"""
    
    # Create output directory
    client_name = os.path.splitext(os.path.basename(client_file))[0]
    output_dir = os.path.join(output_base, client_name)
    
    # Run analysis
    analyzer = HealthPlanAnalyzer.from_file(client_file)
    analyzer.add_plans_from_directory(plans_dir)
    results = analyzer.analyze()
    analyzer.generate_reports(output_dir)
    
    return client_name, results.get_top_plan().plan.marketing_name

# Process multiple clients in parallel
client_files = ["client1.json", "client2.json", "client3.json"]
plans_dir = "./shared_plans/"
output_base = "./batch_output/"

with ProcessPoolExecutor(max_workers=3) as executor:
    futures = [
        executor.submit(analyze_client, cf, plans_dir, output_base)
        for cf in client_files
    ]
    
    for future in futures:
        client_name, best_plan = future.result()
        print(f"{client_name}: {best_plan}")
```

### Example 5: Integration with External APIs

```python
import requests
from healthplan_navigator.core.models import Plan

class APIPlansLoader:
    """Load plans from external API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.healthplans.com/v1"
    
    def load_plans_for_zip(self, zipcode: str) -> List[Plan]:
        """Load available plans for a ZIP code"""
        
        response = requests.get(
            f"{self.base_url}/plans",
            params={"zipcode": zipcode},
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        
        plans = []
        for plan_data in response.json()["plans"]:
            plan = Plan(
                plan_id=plan_data["id"],
                issuer=plan_data["issuer"],
                marketing_name=plan_data["name"],
                # Map remaining fields...
            )
            plans.append(plan)
        
        return plans

# Use with analyzer
loader = APIPlansLoader("your-api-key")
plans = loader.load_plans_for_zip("85001")

analyzer = HealthPlanAnalyzer(client)
for plan in plans:
    analyzer.add_plan(plan)
```

## Error Handling

### Common Exceptions

```python
# File not found
try:
    plan = parser.parse_document("missing.pdf")
except IOError as e:
    print(f"File error: {e}")

# Invalid file format
try:
    plan = parser.parse_document("file.xyz")
except ValueError as e:
    print(f"Format error: {e}")

# No plans to analyze
try:
    results = analyzer.analyze()
except ValueError as e:
    print(f"Analysis error: {e}")

# Invalid weights
try:
    scorer = HealthPlanScorer(weights={'invalid': 1.0})
except ValueError as e:
    print(f"Configuration error: {e}")
```

### Error Recovery Patterns

```python
def safe_parse_directory(directory: str) -> List[Plan]:
    """Parse directory with error recovery"""
    
    plans = []
    failed_files = []
    
    for file_path in glob.glob(os.path.join(directory, "*")):
        try:
            plan = parser.parse_document(file_path)
            if plan:
                plans.append(plan)
        except Exception as e:
            failed_files.append((file_path, str(e)))
            continue
    
    if failed_files:
        print(f"Failed to parse {len(failed_files)} files:")
        for path, error in failed_files:
            print(f"  - {path}: {error}")
    
    return plans
```

## Extension Guide

### Adding a New Scoring Metric

```python
# Step 1: Extend ScoringMetrics
@dataclass
class ExtendedScoringMetrics(ScoringMetrics):
    """Extended metrics including telehealth"""
    telehealth_score: float = 0.0

# Step 2: Extend Plan model if needed
@dataclass
class ExtendedPlan(Plan):
    """Plan with telehealth information"""
    offers_telehealth: bool = False
    telehealth_copay: float = 0.0

# Step 3: Create custom scorer
class ExtendedScorer(HealthPlanScorer):
    """Scorer with telehealth metric"""
    
    DEFAULT_WEIGHTS = {
        'provider_network': 0.25,
        'medication_coverage': 0.20,
        'total_cost': 0.20,
        'financial_protection': 0.10,
        'administrative_simplicity': 0.10,
        'plan_quality': 0.05,
        'telehealth': 0.10  # New metric
    }
    
    def _score_telehealth(self, plan: ExtendedPlan) -> float:
        """Score telehealth coverage (0-10)"""
        if not plan.offers_telehealth:
            return 0.0
        
        score = 5.0  # Base score for offering
        
        if plan.telehealth_copay == 0:
            score += 3.0  # Free telehealth
        elif plan.telehealth_copay <= 25:
            score += 2.0  # Low cost
        
        return min(score + 2.0, 10.0)  # Bonus points
```

### Creating a Custom Parser

```python
from healthplan_navigator.core.ingest import DocumentParser

class ExcelParser:
    """Parser for Excel files"""
    
    def parse(self, file_path: str) -> List[Plan]:
        """Parse Excel file with multiple plans"""
        import pandas as pd
        
        df = pd.read_excel(file_path)
        plans = []
        
        for _, row in df.iterrows():
            plan = Plan(
                plan_id=row['Plan ID'],
                issuer=row['Issuer'],
                marketing_name=row['Plan Name'],
                # Map remaining columns...
            )
            plans.append(plan)
        
        return plans

# Register with DocumentParser
class ExtendedDocumentParser(DocumentParser):
    """Parser with Excel support"""
    
    def __init__(self):
        super().__init__()
        self.excel_parser = ExcelParser()
    
    def parse_document(self, file_path: str) -> Optional[Plan]:
        if file_path.endswith('.xlsx'):
            plans = self.excel_parser.parse(file_path)
            return plans[0] if plans else None
        return super().parse_document(file_path)
```

### Custom Report Format

```python
class LatexReportGenerator:
    """Generate LaTeX reports for professional printing"""
    
    def generate_latex_report(self, results: AnalysisResults, 
                            output_dir: str) -> str:
        """Generate professional LaTeX report"""
        
        output_path = os.path.join(output_dir, "report.tex")
        
        with open(output_path, 'w') as f:
            # LaTeX header
            f.write("\\documentclass{article}\n")
            f.write("\\usepackage{booktabs}\n")
            f.write("\\begin{document}\n")
            f.write("\\title{Healthcare Plan Analysis}\n")
            f.write(f"\\author{{{results.client.personal.full_name}}}\n")
            f.write("\\maketitle\n\n")
            
            # Content sections
            self._write_summary_section(f, results)
            self._write_comparison_table(f, results)
            self._write_recommendations(f, results)
            
            # Close document
            f.write("\\end{document}\n")
        
        return output_path
```

## API Patterns

### Builder Pattern for Complex Objects

```python
class ClientBuilder:
    """Fluent builder for Client objects"""
    
    def __init__(self):
        self._personal = None
        self._providers = []
        self._medications = []
        self._priorities = None
    
    def with_personal_info(self, **kwargs) -> 'ClientBuilder':
        self._personal = PersonalInfo(**kwargs)
        return self
    
    def add_provider(self, **kwargs) -> 'ClientBuilder':
        self._providers.append(Provider(**kwargs))
        return self
    
    def add_medication(self, **kwargs) -> 'ClientBuilder':
        self._medications.append(Medication(**kwargs))
        return self
    
    def with_priorities(self, **kwargs) -> 'ClientBuilder':
        self._priorities = Priorities(**kwargs)
        return self
    
    def build(self) -> Client:
        """Build the client object"""
        if not all([self._personal, self._priorities]):
            raise ValueError("Missing required components")
        
        medical_profile = MedicalProfile(
            providers=self._providers,
            medications=self._medications
        )
        
        return Client(
            personal=self._personal,
            medical_profile=medical_profile,
            priorities=self._priorities
        )

# Usage
client = (ClientBuilder()
    .with_personal_info(
        full_name="John Doe",
        dob="1980-01-01",
        zipcode="85001",
        household_size=2,
        annual_income=75000,
        csr_eligible=False
    )
    .add_provider(
        name="Dr. Smith",
        specialty="Primary Care",
        priority="must-keep",
        visit_frequency=4
    )
    .add_medication(
        name="Metformin",
        dosage="500mg",
        frequency="Daily",
        annual_doses=365
    )
    .with_priorities(
        keep_providers=5,
        minimize_total_cost=4,
        predictable_costs=3,
        avoid_prior_auth=4,
        simple_admin=3
    )
    .build()
)
```

### Strategy Pattern for Scoring

```python
from abc import ABC, abstractmethod

class ScoringStrategy(ABC):
    """Abstract base for scoring strategies"""
    
    @abstractmethod
    def score(self, client: Client, plan: Plan) -> float:
        """Calculate score for a specific metric"""
        pass

class ProviderNetworkStrategy(ScoringStrategy):
    """Strategy for provider network scoring"""
    
    def score(self, client: Client, plan: Plan) -> float:
        # Implementation here
        pass

class CostFocusedScorer(HealthPlanScorer):
    """Scorer using strategy pattern"""
    
    def __init__(self):
        self.strategies = {
            'provider_network': ProviderNetworkStrategy(),
            'total_cost': TotalCostStrategy(),
            # etc...
        }
```

## Performance Considerations

### Caching Expensive Operations

```python
from functools import lru_cache
import hashlib

class CachedHealthPlanScorer(HealthPlanScorer):
    """Scorer with caching for repeated calculations"""
    
    @lru_cache(maxsize=128)
    def _estimate_annual_cost(self, client_hash: str, plan_id: str) -> float:
        """Cached cost estimation"""
        # Reconstruct objects from cache keys
        client = self._get_client_from_hash(client_hash)
        plan = self._get_plan_from_id(plan_id)
        return super()._estimate_annual_cost(client, plan)
    
    def _get_client_hash(self, client: Client) -> str:
        """Generate stable hash for client"""
        data = f"{client.personal.full_name}:{len(client.medical_profile.medications)}"
        return hashlib.md5(data.encode()).hexdigest()
```

### Parallel Processing

```python
from concurrent.futures import ThreadPoolExecutor
import asyncio

class ParallelAnalyzer(HealthPlanAnalyzer):
    """Analyzer with parallel plan scoring"""
    
    def analyze(self) -> AnalysisResults:
        """Analyze plans in parallel"""
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Score plans in parallel
            futures = [
                executor.submit(self.scorer.score_plan, self.client, plan, self.plans)
                for plan in self.plans
            ]
            
            analyses = [future.result() for future in futures]
        
        # Rest of analysis...
        return self._complete_analysis(analyses)
```

### Memory-Efficient Processing

```python
class StreamingAnalyzer:
    """Process large plan sets without loading all into memory"""
    
    def analyze_streaming(self, plan_files: List[str]) -> Generator[PlanAnalysis, None, None]:
        """Yield analysis results one at a time"""
        
        for plan_file in plan_files:
            # Parse one plan
            plan = self.parser.parse_document(plan_file)
            if not plan:
                continue
            
            # Score it
            analysis = self.scorer.score_plan(self.client, plan, [plan])
            
            # Yield result
            yield analysis
            
            # Plan object will be garbage collected
```

---

This comprehensive API documentation provides complete details for all classes, methods, patterns, and usage examples in the HealthPlan Navigator system. It serves as the definitive reference for developers and AI coding assistants working with the codebase.