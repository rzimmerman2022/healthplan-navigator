#!/usr/bin/env python3
"""
Medication and Drug Price Integration Module
Handles drug formulary data and pricing information.
"""

import json
import logging
import os
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path
from datetime import datetime
import requests

from ..core.models import Medication, DrugFormulary

logger = logging.getLogger(__name__)


class MedicationIntegration:
    """
    Manages medication formulary and pricing data integration.
    
    Supports:
    - RxNorm drug database integration
    - GoodRx price comparisons
    - Medicare Part D formulary data
    - Generic/brand name mapping
    """
    
    # RxNorm API (public, no auth required)
    RXNORM_API_URL = "https://rxnav.nlm.nih.gov/REST/"
    
    # OpenFDA API for drug information (public)
    OPENFDA_API_URL = "https://api.fda.gov/drug/"
    
    def __init__(self, cache_dir: str = "./cache/medications", goodrx_api_key: Optional[str] = None):
        """
        Initialize medication integration.
        
        Args:
            cache_dir: Directory for caching medication data
            goodrx_api_key: Optional GoodRx API key for pricing
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.drug_cache = {}
        self.price_cache = {}
        self.goodrx_api_key = goodrx_api_key or os.getenv('GOODRX_API_KEY')
        self.session = requests.Session()
        self._load_drug_cache()
    
    def check_medication_coverage(self, 
                                  medication: Medication,
                                  formulary: DrugFormulary) -> Dict[str, Any]:
        """
        Check if a medication is covered by a formulary.
        
        Args:
            medication: Medication to check
            formulary: Plan's drug formulary
        
        Returns:
            Dictionary with coverage details including tier and cost
        """
        if not formulary or not formulary.covered_drugs:
            return {
                'covered': False,
                'tier': None,
                'copay': None,
                'prior_auth_required': False,
                'quantity_limits': False,
                'step_therapy': False
            }
        
        # Try to find medication in formulary
        drug_info = self._find_drug_in_formulary(medication, formulary)
        
        if drug_info:
            return {
                'covered': True,
                'tier': drug_info.get('tier', 'Unknown'),
                'copay': drug_info.get('copay'),
                'coinsurance': drug_info.get('coinsurance'),
                'prior_auth_required': drug_info.get('prior_auth', False),
                'quantity_limits': drug_info.get('quantity_limits', False),
                'step_therapy': drug_info.get('step_therapy', False)
            }
        
        return {
            'covered': False,
            'tier': None,
            'copay': None,
            'prior_auth_required': False,
            'quantity_limits': False,
            'step_therapy': False
        }
    
    def _find_drug_in_formulary(self, 
                                medication: Medication,
                                formulary: DrugFormulary) -> Optional[Dict]:
        """
        Find a medication in the formulary.
        
        Args:
            medication: Medication to find
            formulary: Drug formulary to search
        
        Returns:
            Drug information if found, None otherwise
        """
        # Normalize medication name for matching
        med_name = medication.name.lower().strip()
        
        # Check covered drugs list
        for drug in formulary.covered_drugs:
            drug_name = drug.get('name', '').lower().strip()
            
            # Exact match
            if med_name == drug_name:
                return drug
            
            # Check generic name
            if drug.get('generic_name', '').lower() == med_name:
                return drug
            
            # Check brand names
            brand_names = drug.get('brand_names', [])
            if any(med_name == brand.lower() for brand in brand_names):
                return drug
        
        return None
    
    def get_medication_price(self, 
                            medication: Medication,
                            zipcode: str,
                            quantity: int = 30) -> Dict[str, float]:
        """
        Get estimated medication prices.
        
        Args:
            medication: Medication to price
            zipcode: Location for pricing
            quantity: Quantity (default 30-day supply)
        
        Returns:
            Dictionary with price estimates from various sources
        """
        cache_key = f"{medication.name}_{zipcode}_{quantity}"
        
        # Check cache first
        if cache_key in self.price_cache:
            cached = self.price_cache[cache_key]
            # Check if cache is fresh (less than 7 days old)
            if (datetime.now() - cached['timestamp']).days < 7:
                return cached['prices']
        
        # TODO: Implement actual price lookups
        # For now, return estimates based on medication type
        
        prices = self._estimate_prices(medication, quantity)
        
        # Cache the result
        self.price_cache[cache_key] = {
            'prices': prices,
            'timestamp': datetime.now()
        }
        
        return prices
    
    def _estimate_prices(self, medication: Medication, quantity: int) -> Dict[str, float]:
        """
        Estimate medication prices based on type and quantity.
        
        Args:
            medication: Medication to estimate
            quantity: Quantity to price
        
        Returns:
            Price estimates
        """
        # Simple estimation logic - would be replaced with actual API calls
        base_prices = {
            'generic': 10,
            'brand': 100,
            'specialty': 1000
        }
        
        # Determine medication type
        med_type = self._classify_medication(medication)
        base_price = base_prices.get(med_type, 50)
        
        # Adjust for quantity
        price_per_unit = base_price / 30  # Assume base is 30-day supply
        total_price = price_per_unit * quantity
        
        return {
            'cash_price': total_price,
            'goodrx_price': total_price * 0.7,  # GoodRx typically 30% discount
            'insurance_copay_tier1': 10,
            'insurance_copay_tier2': 40,
            'insurance_copay_tier3': 80,
            'insurance_copay_tier4': total_price * 0.25  # 25% coinsurance for specialty
        }
    
    def _classify_medication(self, medication: Medication) -> str:
        """
        Classify medication as generic, brand, or specialty.
        
        Args:
            medication: Medication to classify
        
        Returns:
            Classification: 'generic', 'brand', or 'specialty'
        """
        med_name = medication.name.lower()
        
        # Common generic medications (simplified list)
        common_generics = [
            'metformin', 'lisinopril', 'atorvastatin', 'metoprolol',
            'omeprazole', 'amlodipine', 'simvastatin', 'losartan',
            'levothyroxine', 'gabapentin', 'hydrochlorothiazide'
        ]
        
        # Common brand medications
        common_brands = [
            'lipitor', 'crestor', 'nexium', 'advair', 'januvia',
            'lyrica', 'synthroid', 'eliquis', 'xarelto', 'jardiance'
        ]
        
        # Specialty medications (very simplified)
        specialty_keywords = [
            'humira', 'enbrel', 'remicade', 'keytruda', 'opdivo',
            'insulin', 'biologic', 'injection', 'infusion'
        ]
        
        # Check classifications
        if any(generic in med_name for generic in common_generics):
            return 'generic'
        elif any(brand in med_name for brand in common_brands):
            return 'brand'
        elif any(keyword in med_name for keyword in specialty_keywords):
            return 'specialty'
        
        # Default to generic if unknown
        return 'generic'
    
    def calculate_annual_medication_cost(self, 
                                        medications: List[Medication],
                                        formulary: DrugFormulary,
                                        plan_copays: Dict[str, float]) -> float:
        """
        Calculate estimated annual medication costs for a plan.
        
        Args:
            medications: List of client medications
            formulary: Plan's drug formulary
            plan_copays: Plan's copay structure by tier
        
        Returns:
            Estimated annual medication cost
        """
        total_cost = 0
        
        for medication in medications:
            coverage = self.check_medication_coverage(medication, formulary)
            
            if coverage['covered']:
                # Use plan's copay/coinsurance
                tier = coverage.get('tier', 'tier3')
                
                if coverage.get('copay'):
                    # Fixed copay
                    monthly_cost = coverage['copay']
                elif coverage.get('coinsurance'):
                    # Percentage of drug cost
                    prices = self.get_medication_price(medication, '00000', 30)
                    monthly_cost = prices['cash_price'] * coverage['coinsurance']
                else:
                    # Use default tier copay
                    monthly_cost = plan_copays.get(tier, 50)
                
                # Calculate annual cost based on frequency
                annual_fills = medication.annual_doses / 30  # Assume 30-day fills
                total_cost += monthly_cost * annual_fills
            else:
                # Not covered - full cash price
                prices = self.get_medication_price(medication, '00000', 30)
                annual_fills = medication.annual_doses / 30
                total_cost += prices['cash_price'] * annual_fills
        
        return total_cost
    
    def find_generic_alternatives(self, medication: Medication) -> List[Dict[str, str]]:
        """
        Find generic alternatives for a brand medication.
        
        Args:
            medication: Brand medication
        
        Returns:
            List of generic alternatives
        """
        alternatives = []
        
        # Try RxNorm API first
        try:
            rxnorm_alternatives = self._find_rxnorm_alternatives(medication.name)
            if rxnorm_alternatives:
                return rxnorm_alternatives
        except Exception as e:
            logger.debug(f"RxNorm lookup error: {e}")
        
        # Fallback to simplified mapping for common brand -> generic
        brand_to_generic = {
            'lipitor': 'atorvastatin',
            'crestor': 'rosuvastatin',
            'nexium': 'esomeprazole',
            'prilosec': 'omeprazole',
            'zocor': 'simvastatin',
            'glucophage': 'metformin',
            'prinivil': 'lisinopril',
            'norvasc': 'amlodipine',
            'toprol': 'metoprolol',
            'synthroid': 'levothyroxine'
        }
        
        med_name = medication.name.lower()
        
        if med_name in brand_to_generic:
            return [{
                'generic_name': brand_to_generic[med_name],
                'brand_name': medication.name,
                'potential_savings': 'Up to 80% lower cost'
            }]
        
        return []
    
    def _find_rxnorm_alternatives(self, drug_name: str) -> List[Dict[str, str]]:
        """
        Find alternatives using RxNorm API.
        
        Args:
            drug_name: Name of medication
        
        Returns:
            List of alternative medications
        """
        try:
            # Get RxCUI for the drug
            response = self.session.get(
                f"{self.RXNORM_API_URL}rxcui.json",
                params={'name': drug_name},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                rxcui = data.get('idGroup', {}).get('rxnormId')
                
                if rxcui:
                    # Get related drugs (generics/brands)
                    related_response = self.session.get(
                        f"{self.RXNORM_API_URL}rxcui/{rxcui}/related.json",
                        params={'tty': 'SBD+SCD'},
                        timeout=10
                    )
                    
                    if related_response.status_code == 200:
                        related_data = related_response.json()
                        alternatives = []
                        
                        for group in related_data.get('relatedGroup', {}).get('conceptGroup', []):
                            for concept in group.get('conceptProperties', []):
                                if concept.get('name') and concept.get('name').lower() != drug_name.lower():
                                    alternatives.append({
                                        'generic_name': concept.get('name'),
                                        'brand_name': drug_name,
                                        'rxcui': concept.get('rxcui'),
                                        'potential_savings': 'Variable savings'
                                    })
                        
                        return alternatives[:5]  # Limit to 5 alternatives
        
        except Exception as e:
            logger.error(f"RxNorm API error: {e}")
        
        return []
    
    def _load_drug_cache(self):
        """Load drug cache from disk."""
        cache_file = self.cache_dir / "drug_cache.json"
        
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                self.drug_cache = json.load(f)
        
        price_cache_file = self.cache_dir / "price_cache.json"
        
        if price_cache_file.exists():
            with open(price_cache_file, 'r') as f:
                cached = json.load(f)
                # Convert timestamp strings back to datetime
                for key, value in cached.items():
                    value['timestamp'] = datetime.fromisoformat(value['timestamp'])
                self.price_cache = cached
    
    def _save_drug_cache(self):
        """Save drug cache to disk."""
        cache_file = self.cache_dir / "drug_cache.json"
        
        with open(cache_file, 'w') as f:
            json.dump(self.drug_cache, f, indent=2)
        
        # Save price cache with serialized timestamps
        price_cache_file = self.cache_dir / "price_cache.json"
        cache_copy = {}
        
        for key, value in self.price_cache.items():
            cache_copy[key] = {
                'prices': value['prices'],
                'timestamp': value['timestamp'].isoformat()
            }
        
        with open(price_cache_file, 'w') as f:
            json.dump(cache_copy, f, indent=2)