import json
import csv
import re
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import pdfplumber
from docx import Document
from .models import Plan, MetalLevel, PlanType, CoverageStatus, NetworkStatus, CostSharing, Administrative

logger = logging.getLogger(__name__)


class DocumentParser:
    """Handles parsing of healthcare plan documents in various formats."""
    
    def __init__(self):
        self.metal_level_mapping = {
            'bronze': MetalLevel.BRONZE,
            'silver': MetalLevel.SILVER,
            'gold': MetalLevel.GOLD,
            'platinum': MetalLevel.PLATINUM,
            'catastrophic': MetalLevel.CATASTROPHIC
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
                        logger.info(f"Successfully parsed plan from {file_path.name}")
                    else:
                        logger.warning(f"No plan data extracted from {file_path.name}")
                except Exception as e:
                    logger.error(f"Error parsing {file_path}: {e}")
                    # Continue processing other files rather than failing completely
        
        return plans
    
    def _parse_pdf(self, file_path: str) -> Optional[Plan]:
        """Extract plan information from PDF documents."""
        try:
            with pdfplumber.open(file_path) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text
                
                return self._extract_plan_from_text(text, file_path)
        except Exception as e:
            logger.error(f"Error reading PDF {file_path}: {e}")
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
            logger.error(f"Error reading DOCX {file_path}: {e}")
            return None
    
    def parse_json(self, file_path: str) -> Optional[Plan]:
        """Parse JSON format plan data."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Convert JSON data to Plan object
            return self._json_to_plan(data)
        except Exception as e:
            logger.error(f"Error reading JSON {file_path}: {e}")
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
            logger.error(f"Error reading CSV {file_path}: {e}")
            return []
    
    def _extract_plan_from_text(self, text: str, source_file: str) -> Optional[Plan]:
        """Extract plan information using FIXED regex patterns for Healthcare.gov PDFs."""
        
        # Clean text for better matching
        text = text.replace('\n', ' ')  # Join lines for multi-line patterns
        
        # Extract plan ID - Healthcare.gov format
        plan_id = self._extract_plan_id_fixed(text, source_file)
        
        # Extract issuer/company name
        issuer = self._extract_issuer_fixed(text, source_file)
        
        # Extract metal level
        metal_level = self._extract_metal_level_fixed(text, source_file)
        
        # Extract marketing name
        marketing_name = self._extract_marketing_name_fixed(text, source_file)
        
        # Extract costs with FIXED patterns
        monthly_premium = self._extract_premium_fixed(text)
        deductible = self._extract_deductible_fixed(text)
        oop_max = self._extract_oop_max_fixed(text)
        
        # Extract cost sharing
        cost_sharing = self._extract_cost_sharing_fixed(text)
        
        # Extract administrative details
        administrative = self._extract_administrative_details(text)
        
        # Use defaults if extraction fails but we have a valid file
        if not plan_id:
            # Generate ID from filename
            filename = Path(source_file).stem
            plan_id = re.sub(r'[^A-Z0-9]', '', filename.upper())[:20]
        
        if not issuer:
            issuer = self._extract_issuer_from_filename(source_file)
        
        if not marketing_name:
            marketing_name = Path(source_file).stem.replace('_', ' ')
        
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
    
    def _extract_plan_id_fixed(self, text: str, source_file: str) -> str:
        """Extract plan ID with Healthcare.gov specific patterns."""
        # Healthcare.gov format: digits + AZ + digits
        patterns = [
            r'Plan ID[:\s]+([0-9]+AZ[0-9]+)',
            r'([0-9]{5,}AZ[0-9]{4,})',
            r'Plan ID[:\s]+([A-Z0-9]+)',
            r'ID#?\s*([0-9]{6,})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Fallback: extract from filename
        filename = Path(source_file).stem
        id_match = re.search(r'([0-9]{6,})', filename)
        if id_match:
            return id_match.group(1)
        
        return filename[:20]  # Use truncated filename as last resort
    
    def _extract_issuer_fixed(self, text: str, source_file: str) -> str:
        """Extract issuer with improved patterns."""
        # Look for known issuers in text
        issuer_patterns = [
            r'(Ambetter(?:\s+from\s+[^\.]+)?)',
            r'(Blue Cross Blue Shield(?:\s+of\s+[^\.]+)?)',
            r'(UnitedHealth(?:care)?)',
            r'(Banner Health)',
            r'(Oscar Health)',
            r'(Aetna)',
            r'(Cigna)',
            r'(Humana)',
        ]
        
        for pattern in issuer_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Fallback to filename
        return self._extract_issuer_from_filename(source_file)
    
    def _extract_issuer_from_filename(self, filename: str) -> str:
        """Extract issuer from filename."""
        filename_lower = Path(filename).stem.lower()
        
        issuer_mappings = {
            'amb': 'Ambetter',
            'bcbs': 'Blue Cross Blue Shield',
            'uhc': 'UnitedHealthcare',
            'banner': 'Banner Health',
            'imperial': 'Imperial Health',
            'oscar': 'Oscar Health'
        }
        
        for abbrev, full_name in issuer_mappings.items():
            if abbrev in filename_lower:
                return full_name
        
        # Special case for eligibility notices
        if 'eligibility' in filename_lower:
            return 'Healthcare.gov'
        
        return 'Unknown Issuer'
    
    def _extract_metal_level_fixed(self, text: str, source_file: str) -> MetalLevel:
        """Extract metal level with improved matching."""
        text_lower = text.lower()
        filename_lower = Path(source_file).stem.lower()
        
        # Check both text and filename
        combined = text_lower + ' ' + filename_lower
        
        # Order matters - check from highest to lowest tier
        for metal in ['platinum', 'gold', 'silver', 'bronze', 'catastrophic']:
            if metal in combined:
                return self.metal_level_mapping[metal]
        
        return MetalLevel.SILVER  # Default
    
    def _extract_marketing_name_fixed(self, text: str, source_file: str) -> str:
        """Extract marketing name with better patterns."""
        # Try to find actual plan name in text
        patterns = [
            r'((?:Standard\s+)?(?:Gold|Silver|Bronze|Platinum)[^|]*?)(?:\s*\|)',
            r'(Blue ACA[^|]+)',
            r'Plan Name[:\s]+([^\n]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Clean up the name
                name = re.sub(r'\s+', ' ', name)
                if len(name) > 5 and len(name) < 100:
                    return name
        
        # Fallback: build from filename
        filename = Path(source_file).stem
        parts = filename.split('_')
        
        # Try to construct a reasonable name
        if 'Gold' in filename:
            metal = 'Gold'
        elif 'Silver' in filename:
            metal = 'Silver'
        elif 'Bronze' in filename:
            metal = 'Bronze'
        else:
            metal = ''
        
        issuer = self._extract_issuer_from_filename(source_file)
        
        if metal and issuer != 'Unknown Issuer':
            return f"{metal} {issuer} Plan"
        
        return filename.replace('_', ' ')
    
    def _extract_premium_fixed(self, text: str) -> Optional[float]:
        """Extract monthly premium with FIXED patterns matching Healthcare.gov format."""
        patterns = [
            r'Monthly premium\s*\$([0-9]+(?:\.[0-9]{2})?)',
            r'premium\s*\$([0-9]+(?:\.[0-9]{2})?)\s*(?:/month|per month)?',
            r'\$([0-9]+(?:\.[0-9]{2})?)\s*/month',
            r'Was\s*\$([0-9]+(?:\.[0-9]{2})?)',  # Original premium before tax credit
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = float(match.group(1))
                # Return the value if it's reasonable (not zero unless explicitly stated)
                if value > 0 or 'premium $0' in text.lower():
                    return value
        
        return None
    
    def _extract_deductible_fixed(self, text: str) -> Optional[float]:
        """Extract deductible with FIXED patterns."""
        patterns = [
            r'Deductible\s*\$([0-9,]+(?:\.[0-9]{2})?)\s*Individual',
            r'Deductible\s*\$([0-9,]+(?:\.[0-9]{2})?)',
            r'Individual Deductible[:\s]*\$([0-9,]+(?:\.[0-9]{2})?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Remove commas and convert to float
                value = float(match.group(1).replace(',', ''))
                return value
        
        return None
    
    def _extract_oop_max_fixed(self, text: str) -> Optional[float]:
        """Extract out-of-pocket maximum with FIXED patterns."""
        patterns = [
            r'Out-of-pocket maximum\s*\$([0-9,]+(?:\.[0-9]{2})?)\s*Individual',
            r'Out-of-pocket maximum\s*\$([0-9,]+(?:\.[0-9]{2})?)',
            r'maximum\s*\$([0-9,]+(?:\.[0-9]{2})?)\s*Individual',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Remove commas and convert to float
                value = float(match.group(1).replace(',', ''))
                return value
        
        return None
    
    def _extract_cost_sharing_fixed(self, text: str) -> CostSharing:
        """Extract cost sharing details with improved patterns."""
        cost_sharing = CostSharing()
        
        # Primary care copay
        pcp_patterns = [
            r'Primary care visit[:\s]*\$([0-9]+)',
            r'PCP[:\s]*\$([0-9]+)',
            r'Doctor visit[:\s]*\$([0-9]+)',
        ]
        
        for pattern in pcp_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                cost_sharing.primary_care_copay = float(match.group(1))
                break
        
        # Specialist copay
        spec_patterns = [
            r'Specialist visit[:\s]*\$([0-9]+)',
            r'Specialist[:\s]*\$([0-9]+)',
        ]
        
        for pattern in spec_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                cost_sharing.specialist_copay = float(match.group(1))
                break
        
        # Emergency room copay
        er_patterns = [
            r'Emergency room[:\s]*\$([0-9]+)',
            r'ER visit[:\s]*\$([0-9]+)',
            r'Emergency[:\s]*\$([0-9]+)',
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
            logger.error(f"Error converting CSV row to plan: {e}")
            return None