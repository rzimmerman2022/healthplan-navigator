import json
import csv
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
import pdfplumber
from docx import Document
from .models import Plan, MetalLevel, PlanType, CoverageStatus, NetworkStatus, CostSharing, Administrative


class DocumentParser:
    """Handles parsing of healthcare plan documents in various formats."""
    
    def __init__(self):
        self.metal_level_mapping = {
            'bronze': MetalLevel.BRONZE,
            'silver': MetalLevel.SILVER,
            'gold': MetalLevel.GOLD,
            'platinum': MetalLevel.PLATINUM
        }
    
    def parse_document(self, file_path: str) -> Optional[Plan]:
        """Parse a document and extract plan information."""
        path = Path(file_path)
        
        if path.suffix.lower() == '.pdf':
            return self._parse_pdf(file_path)
        elif path.suffix.lower() == '.docx':
            return self._parse_docx(file_path)
        elif path.suffix.lower() == '.json':
            return self.parse_json(file_path)
        elif path.suffix.lower() == '.csv':
            plans = self.parse_csv(file_path)
            return plans[0] if plans else None
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")
    
    def parse_batch(self, directory_path: str) -> List[Plan]:
        """Parse all supported documents in a directory."""
        plans = []
        directory = Path(directory_path)
        
        for file_path in directory.glob("*"):
            if file_path.suffix.lower() in ['.pdf', '.docx', '.json', '.csv']:
                try:
                    plan = self.parse_document(str(file_path))
                    if plan:
                        plans.append(plan)
                except Exception as e:
                    print(f"Error parsing {file_path}: {e}")
        
        return plans
    
    def _parse_pdf(self, file_path: str) -> Optional[Plan]:
        """Extract plan information from PDF documents."""
        try:
            with pdfplumber.open(file_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
                
                return self._extract_plan_from_text(text, file_path)
        except Exception as e:
            print(f"Error reading PDF {file_path}: {e}")
            return None
    
    def _parse_docx(self, file_path: str) -> Optional[Plan]:
        """Extract plan information from DOCX documents."""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return self._extract_plan_from_text(text, file_path)
        except Exception as e:
            print(f"Error reading DOCX {file_path}: {e}")
            return None
    
    def parse_json(self, file_path: str) -> Optional[Plan]:
        """Parse JSON format plan data."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Convert JSON data to Plan object
            return self._json_to_plan(data)
        except Exception as e:
            print(f"Error reading JSON {file_path}: {e}")
            return None
    
    def parse_csv(self, file_path: str) -> List[Plan]:
        """Parse CSV format plan data."""
        plans = []
        try:
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    plan = self._csv_row_to_plan(row)
                    if plan:
                        plans.append(plan)
            return plans
        except Exception as e:
            print(f"Error reading CSV {file_path}: {e}")
            return []
    
    def _extract_plan_from_text(self, text: str, source_file: str) -> Optional[Plan]:
        """Extract plan information using text parsing and regex patterns."""
        
        # Extract plan ID from filename
        filename = Path(source_file).stem
        plan_id = self._extract_plan_id(filename, text)
        
        # Extract issuer/company name
        issuer = self._extract_issuer(filename, text)
        
        # Extract metal level
        metal_level = self._extract_metal_level(filename, text)
        
        # Extract marketing name
        marketing_name = self._extract_marketing_name(filename, text)
        
        # Extract costs
        monthly_premium = self._extract_premium(text)
        deductible = self._extract_deductible(text)
        oop_max = self._extract_oop_max(text)
        
        # Extract cost sharing
        cost_sharing = self._extract_cost_sharing(text)
        
        # Extract administrative details
        administrative = self._extract_administrative_details(text)
        
        if not plan_id or not issuer or not metal_level:
            print(f"Could not extract required plan details from {source_file}")
            return None
        
        return Plan(
            plan_id=plan_id,
            issuer=issuer,
            marketing_name=marketing_name,
            metal_level=metal_level,
            monthly_premium=monthly_premium or 0.0,
            deductible_individual=deductible or 0.0,
            oop_max_individual=oop_max or 0.0,
            cost_sharing=cost_sharing,
            administrative=administrative
        )
    
    def _extract_plan_id(self, filename: str, text: str) -> Optional[str]:
        """Extract plan ID from filename or text."""
        # Try to extract from filename first
        id_match = re.search(r'(\d{6,})', filename)
        if id_match:
            return id_match.group(1)
        
        # Try to extract from text
        patterns = [
            r'Plan\s*ID[:\s]+([A-Z0-9]+)',
            r'ID[:\s]+([A-Z0-9]{6,})',
            r'([A-Z0-9]{10,})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return filename  # Fallback to filename
    
    def _extract_issuer(self, filename: str, text: str) -> Optional[str]:
        """Extract insurance company/issuer name."""
        # Common issuer abbreviations in filenames
        issuer_mappings = {
            'AMB': 'Ambetter',
            'BCBS': 'Blue Cross Blue Shield',
            'UHC': 'UnitedHealthcare',
            'Banner': 'Banner Health',
            'Imperial': 'Imperial Health',
            'Oscar': 'Oscar Health'
        }
        
        for abbrev, full_name in issuer_mappings.items():
            if abbrev.lower() in filename.lower():
                return full_name
        
        # Try to extract from text
        patterns = [
            r'(Ambetter|Blue Cross|UnitedHealth|Banner|Imperial|Oscar|Aetna|Cigna|Humana)',
            r'Issuer[:\s]+([A-Za-z\s]+)',
            r'Insurance Company[:\s]+([A-Za-z\s]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "Unknown Issuer"
    
    def _extract_metal_level(self, filename: str, text: str) -> Optional[MetalLevel]:
        """Extract metal level (Bronze, Silver, Gold, Platinum)."""
        filename_lower = filename.lower()
        text_lower = text.lower()
        
        for metal in ['platinum', 'gold', 'silver', 'bronze']:
            if metal in filename_lower or metal in text_lower:
                return self.metal_level_mapping[metal]
        
        return MetalLevel.SILVER  # Default fallback
    
    def _extract_marketing_name(self, filename: str, text: str) -> str:
        """Extract marketing name of the plan."""
        # Try to extract from filename
        parts = filename.split('_')
        if len(parts) >= 4:
            # Format: HealthGov_2025_Metal_Issuer_Type_...
            metal = parts[2] if len(parts) > 2 else ""
            issuer = parts[3] if len(parts) > 3 else ""
            plan_type = parts[4] if len(parts) > 4 else ""
            return f"{metal} {issuer} {plan_type}".strip()
        
        # Try to extract from text
        patterns = [
            r'Plan Name[:\s]+([A-Za-z0-9\s]+)',
            r'Marketing Name[:\s]+([A-Za-z0-9\s]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return filename  # Fallback to filename
    
    def _extract_premium(self, text: str) -> Optional[float]:
        """Extract monthly premium amount."""
        patterns = [
            r'Monthly Premium[:\s]+\$?([0-9,]+\.?\d*)',
            r'Premium[:\s]+\$?([0-9,]+\.?\d*)',
            r'\$([0-9,]+\.?\d*)\s*per month'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return float(match.group(1).replace(',', ''))
        
        return None
    
    def _extract_deductible(self, text: str) -> Optional[float]:
        """Extract individual deductible amount."""
        patterns = [
            r'Individual Deductible[:\s]+\$?([0-9,]+\.?\d*)',
            r'Deductible[:\s]+\$?([0-9,]+\.?\d*)',
            r'Annual Deductible[:\s]+\$?([0-9,]+\.?\d*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return float(match.group(1).replace(',', ''))
        
        return None
    
    def _extract_oop_max(self, text: str) -> Optional[float]:
        """Extract out-of-pocket maximum."""
        patterns = [
            r'Out.of.Pocket Maximum[:\s]+\$?([0-9,]+\.?\d*)',
            r'OOPM[:\s]+\$?([0-9,]+\.?\d*)',
            r'Maximum Out.of.Pocket[:\s]+\$?([0-9,]+\.?\d*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return float(match.group(1).replace(',', ''))
        
        return None
    
    def _extract_cost_sharing(self, text: str) -> CostSharing:
        """Extract cost sharing details."""
        cost_sharing = CostSharing()
        
        # Primary care copay
        pcp_patterns = [
            r'Primary Care[:\s]+\$?([0-9]+)',
            r'PCP[:\s]+\$?([0-9]+)',
            r'Family Doctor[:\s]+\$?([0-9]+)'
        ]
        
        for pattern in pcp_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                cost_sharing.primary_care_copay = float(match.group(1))
                break
        
        # Specialist copay
        spec_patterns = [
            r'Specialist[:\s]+\$?([0-9]+)',
            r'Specialty Care[:\s]+\$?([0-9]+)'
        ]
        
        for pattern in spec_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                cost_sharing.specialist_copay = float(match.group(1))
                break
        
        # Emergency room copay
        er_patterns = [
            r'Emergency Room[:\s]+\$?([0-9]+)',
            r'ER[:\s]+\$?([0-9]+)',
            r'Emergency[:\s]+\$?([0-9]+)'
        ]
        
        for pattern in er_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                cost_sharing.emergency_room_copay = float(match.group(1))
                break
        
        return cost_sharing
    
    def _extract_administrative_details(self, text: str) -> Administrative:
        """Extract administrative details."""
        administrative = Administrative()
        
        # Check for referral requirements
        if re.search(r'referral.*(required|needed)', text, re.IGNORECASE):
            administrative.prior_auth_common = True
        
        # Check for prior authorization
        if re.search(r'prior auth', text, re.IGNORECASE):
            administrative.prior_auth_common = True
        
        # Default rating (would need external data source for actual ratings)
        administrative.plan_rating = 3.5
        
        return administrative
    
    def _json_to_plan(self, data: Dict[str, Any]) -> Plan:
        """Convert JSON data to Plan object."""
        # Handle both new and old field names
        deductible = data.get('deductible', data.get('deductible_individual', 0))
        oop_max = data.get('oop_max', data.get('oop_max_individual', 0))
        
        return Plan(
            plan_id=data.get('plan_id', ''),
            issuer=data.get('issuer', ''),
            marketing_name=data.get('marketing_name', ''),
            metal_level=self.metal_level_mapping.get(data.get('metal_level', '').lower(), MetalLevel.SILVER),
            plan_type=PlanType[data.get('plan_type', 'PPO').upper()] if data.get('plan_type') else PlanType.PPO,
            monthly_premium=float(data.get('monthly_premium', 0)),
            deductible=float(deductible),
            oop_max=float(oop_max),
            copay_primary=float(data.get('copay_primary', 0)),
            copay_specialist=float(data.get('copay_specialist', 0)),
            copay_er=float(data.get('copay_er', 0)),
            coinsurance=float(data.get('coinsurance', 0.2)),
            requires_referrals=data.get('requires_referrals', False),
            cost_sharing=CostSharing(**data.get('cost_sharing', {})),
            administrative=Administrative(**data.get('administrative', {})),
            quality_rating=float(data.get('quality_rating', 0)),
            customer_rating=float(data.get('customer_rating', 0))
        )
    
    def _csv_row_to_plan(self, row: Dict[str, str]) -> Optional[Plan]:
        """Convert CSV row to Plan object."""
        try:
            # Handle both new and old field names
            deductible = row.get('deductible', row.get('deductible_individual', 0))
            oop_max = row.get('oop_max', row.get('oop_max_individual', 0))
            
            return Plan(
                plan_id=row.get('plan_id', ''),
                issuer=row.get('issuer', ''),
                marketing_name=row.get('marketing_name', ''),
                metal_level=self.metal_level_mapping.get(row.get('metal_level', '').lower(), MetalLevel.SILVER),
                plan_type=PlanType[row.get('plan_type', 'PPO').upper()] if row.get('plan_type') else PlanType.PPO,
                monthly_premium=float(row.get('monthly_premium', 0)),
                deductible=float(deductible),
                oop_max=float(oop_max),
                copay_primary=float(row.get('copay_primary', 0)),
                copay_specialist=float(row.get('copay_specialist', 0)),
                copay_er=float(row.get('copay_er', 0)),
                coinsurance=float(row.get('coinsurance', 0.2)),
                requires_referrals=row.get('requires_referrals', '').lower() == 'true',
                quality_rating=float(row.get('quality_rating', 0)),
                customer_rating=float(row.get('customer_rating', 0))
            )
        except Exception as e:
            print(f"Error converting CSV row to plan: {e}")
            return None