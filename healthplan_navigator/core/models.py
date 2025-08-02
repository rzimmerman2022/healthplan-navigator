from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union
from enum import Enum
from datetime import datetime


class MetalLevel(Enum):
    BRONZE = "Bronze"
    SILVER = "Silver"
    GOLD = "Gold"
    PLATINUM = "Platinum"


class CoverageStatus(Enum):
    COVERED = "COVERED"
    NOT_COVERED = "NOT"
    TIER1 = "TIER1"
    TIER2 = "TIER2"
    TIER3 = "TIER3"
    TIER4 = "TIER4"


class Priority(Enum):
    MUST_KEEP = "must-keep"
    NICE_TO_KEEP = "nice-to-keep"


class NetworkStatus(Enum):
    IN_NETWORK = "IN"
    OUT_OF_NETWORK = "OUT"


@dataclass
class ManufacturerProgram:
    exists: bool
    program_type: Optional[str] = None  # "copay-card" or "rebate"
    max_benefit: Optional[float] = None
    expected_copay: Optional[float] = None


@dataclass
class Provider:
    name: str
    specialty: str
    npi: Optional[str] = None
    priority: Priority = Priority.NICE_TO_KEEP
    visit_frequency: int = 1  # per year


@dataclass
class Medication:
    name: str
    rxnorm_code: Optional[str] = None
    dosage: str = ""
    frequency: str = ""
    annual_doses: int = 1
    manufacturer_program: Optional[ManufacturerProgram] = None


@dataclass
class SpecialTreatment:
    name: str
    frequency: int  # per year
    allowed_cost: float


@dataclass
class MedicalProfile:
    providers: List[Provider] = field(default_factory=list)
    medications: List[Medication] = field(default_factory=list)
    special_treatments: List[SpecialTreatment] = field(default_factory=list)


@dataclass
class PersonalInfo:
    full_name: str
    dob: str  # YYYY-MM-DD format
    zipcode: str
    household_size: int
    annual_income: float
    csr_eligible: bool = False


@dataclass
class Priorities:
    keep_providers: int = 3  # 1-5 scale
    minimize_total_cost: int = 3
    predictable_costs: int = 3
    avoid_prior_auth: int = 3
    simple_admin: int = 3


@dataclass
class Client:
    personal: PersonalInfo
    medical_profile: MedicalProfile
    priorities: Priorities


@dataclass
class CostSharing:
    primary_care_copay: float = 0
    specialist_copay: float = 0
    coinsurance_outpatient: float = 0  # 0-1 (e.g., 0.2 for 20%)
    emergency_room_copay: float = 0


@dataclass
class Administrative:
    prior_auth_common: bool = False
    uses_maximizer: bool = False
    plan_rating: float = 3.0  # 1-5 stars


@dataclass
class Plan:
    plan_id: str
    issuer: str
    marketing_name: str
    metal_level: MetalLevel
    monthly_premium: float
    deductible_individual: float
    oop_max_individual: float
    requires_referrals: bool = False
    network: Dict[str, NetworkStatus] = field(default_factory=dict)
    formulary: Dict[str, CoverageStatus] = field(default_factory=dict)
    cost_sharing: CostSharing = field(default_factory=CostSharing)
    administrative: Administrative = field(default_factory=Administrative)


@dataclass
class ScoringMetrics:
    provider_network_score: float = 0.0  # 0-10
    medication_coverage_score: float = 0.0  # 0-10
    total_cost_score: float = 0.0  # 0-10
    financial_protection_score: float = 0.0  # 0-10
    administrative_simplicity_score: float = 0.0  # 0-10
    plan_quality_score: float = 0.0  # 0-10
    weighted_total_score: float = 0.0  # 0-10


@dataclass
class PlanAnalysis:
    plan: Plan
    metrics: ScoringMetrics
    estimated_annual_cost: float
    provider_coverage_details: Dict[str, bool] = field(default_factory=dict)
    medication_coverage_details: Dict[str, str] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)


@dataclass
class AnalysisReport:
    client: Client
    plan_analyses: List[PlanAnalysis]
    generated_at: datetime = field(default_factory=datetime.now)
    top_recommendations: List[PlanAnalysis] = field(default_factory=list)