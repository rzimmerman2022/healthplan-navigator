#!/usr/bin/env python3
"""
Healthcare.gov API Integration Module
Fetches and transforms plan data from the Healthcare.gov marketplace.
"""

import json
import time
import os
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..core.models import Plan, MetalLevel, PlanType, DrugFormulary, ProviderNetwork

logger = logging.getLogger(__name__)


class HealthcareGovAPI:
    """
    Interface for Healthcare.gov marketplace API.
    
    Handles authentication, rate limiting, and data transformation
    for fetching plan data from the federal marketplace.
    """
    
    # API endpoints - Using public Healthcare.gov endpoints
    # Note: These are example endpoints based on Healthcare.gov's structure
    # Actual production endpoints require API registration
    BASE_URL = "https://marketplace.api.healthcare.gov/api/v1"
    PLANS_ENDPOINT = "/plans/search"
    PROVIDERS_ENDPOINT = "/providers"
    FORMULARY_ENDPOINT = "/formularies"
    COUNTIES_ENDPOINT = "/counties/by/zip"
    
    # Alternative: CMS public data endpoints (no auth required)
    CMS_QHP_URL = "https://data.healthcare.gov/api/1/datastore/sql"
    CMS_DATASET_ID = "b8in-sz6k"  # 2025 QHP Individual Medical Landscape
    
    def __init__(self, api_key: Optional[str] = None, cache_dir: str = "./cache"):
        """
        Initialize Healthcare.gov API client.
        
        Args:
            api_key: API key for authentication (when available)
            cache_dir: Directory for caching API responses
        """
        self.api_key = api_key or os.getenv('HEALTHCARE_GOV_API_KEY')
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        self.rate_limit_delay = 0.5  # Delay between requests in seconds
        self.last_request_time = 0
    
    def fetch_plans(self, 
                   zipcode: str,
                   county_fips: Optional[str] = None,
                   metal_levels: Optional[List[str]] = None,
                   plan_types: Optional[List[str]] = None,
                   year: Optional[int] = None) -> List[Plan]:
        """
        Fetch available plans for a given location.
        
        Args:
            zipcode: 5-digit ZIP code
            county_fips: County FIPS code (for more accurate results)
            metal_levels: Filter by metal levels (Bronze, Silver, Gold, Platinum)
            plan_types: Filter by plan types (HMO, PPO, EPO, POS)
            year: Plan year (defaults to current year)
        
        Returns:
            List of Plan objects available in the specified area
        """
        # Check cache first
        cache_key = self._generate_cache_key(zipcode, county_fips, metal_levels, plan_types, year)
        cached_data = self._load_from_cache(cache_key)
        
        if cached_data:
            logger.info(f"Using cached data for {zipcode}")
            return self._transform_to_plans(cached_data)
        
        # Try CMS public data API first (no auth required)
        try:
            plans_data = self._fetch_cms_public_data(zipcode, county_fips, metal_levels, plan_types, year)
            if plans_data:
                self._save_to_cache(cache_key, plans_data)
                return self._transform_to_plans(plans_data)
        except Exception as e:
            logger.warning(f"CMS public data fetch failed: {e}")
        
        # If API key is available, try authenticated endpoint
        if self.api_key:
            try:
                # Rate limiting
                self._apply_rate_limit()
                
                # Build request parameters
                params = {
                    'zipcode': zipcode,
                    'year': year or datetime.now().year
                }
                
                if county_fips:
                    params['fips'] = county_fips
                if metal_levels:
                    params['metal_levels'] = ','.join(metal_levels)
                if plan_types:
                    params['plan_types'] = ','.join(plan_types)
                
                # Make API request
                response = self.session.get(
                    f"{self.BASE_URL}{self.PLANS_ENDPOINT}",
                    params=params,
                    headers={'Authorization': f'Bearer {self.api_key}'},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self._save_to_cache(cache_key, data)
                    return self._transform_to_plans(data)
                else:
                    logger.error(f"API request failed: {response.status_code}")
            except Exception as e:
                logger.error(f"Healthcare.gov API error: {e}")
        
        logger.warning("Healthcare.gov API not available. Use local files or provide API key.")
        return []
    
    def fetch_provider_network(self, plan_id: str) -> Optional[ProviderNetwork]:
        """
        Fetch provider network details for a specific plan.
        
        Args:
            plan_id: Healthcare.gov plan ID
        
        Returns:
            ProviderNetwork object or None if not available
        """
        # TODO: Implement when API access is available
        logger.info(f"Provider network fetch for {plan_id} - pending API implementation")
        
        # Return a placeholder network for now
        return ProviderNetwork(
            network_id=f"network_{plan_id}",
            name="Network Data Pending",
            providers=[],
            hospitals=[],
            urgent_care_centers=[]
        )
    
    def fetch_drug_formulary(self, plan_id: str) -> Optional[DrugFormulary]:
        """
        Fetch drug formulary for a specific plan.
        
        Args:
            plan_id: Healthcare.gov plan ID
        
        Returns:
            DrugFormulary object or None if not available
        """
        # TODO: Implement when API access is available
        logger.info(f"Drug formulary fetch for {plan_id} - pending API implementation")
        
        # Return a placeholder formulary for now
        return DrugFormulary(
            formulary_id=f"formulary_{plan_id}",
            name="Formulary Data Pending",
            tiers={},
            covered_drugs=[]
        )
    
    def _transform_to_plans(self, api_data: Dict[str, Any]) -> List[Plan]:
        """
        Transform Healthcare.gov API response to Plan objects.
        
        Args:
            api_data: Raw API response data
        
        Returns:
            List of Plan objects
        """
        plans = []
        
        for plan_data in api_data.get('plans', []):
            try:
                # Map API fields to Plan model
                plan = Plan(
                    plan_id=plan_data.get('id', ''),
                    marketing_name=plan_data.get('name', ''),
                    issuer=plan_data.get('issuer', {}).get('name', ''),
                    metal_level=self._map_metal_level(plan_data.get('metal_level', '')),
                    plan_type=self._map_plan_type(plan_data.get('type', '')),
                    monthly_premium=float(plan_data.get('premium', 0)),
                    deductible=float(plan_data.get('deductible', {}).get('individual', 0)),
                    oop_max=float(plan_data.get('moop', {}).get('individual', 0)),
                    copay_primary=float(plan_data.get('copays', {}).get('primary', 0)),
                    copay_specialist=float(plan_data.get('copays', {}).get('specialist', 0)),
                    copay_er=float(plan_data.get('copays', {}).get('emergency', 0)),
                    coinsurance=float(plan_data.get('coinsurance', 0)) / 100,
                    provider_network=None,  # Will be fetched separately
                    drug_formulary=None,    # Will be fetched separately
                    quality_rating=float(plan_data.get('quality_rating', {}).get('global', 0)),
                    customer_rating=float(plan_data.get('quality_rating', {}).get('customer', 0))
                )
                plans.append(plan)
            except Exception as e:
                logger.error(f"Error transforming plan data: {e}")
                continue
        
        return plans
    
    def _map_metal_level(self, api_value: str) -> MetalLevel:
        """Map API metal level to enum."""
        mapping = {
            'bronze': MetalLevel.BRONZE,
            'silver': MetalLevel.SILVER,
            'gold': MetalLevel.GOLD,
            'platinum': MetalLevel.PLATINUM,
            'catastrophic': MetalLevel.CATASTROPHIC
        }
        return mapping.get(api_value.lower(), MetalLevel.BRONZE)
    
    def _map_plan_type(self, api_value: str) -> PlanType:
        """Map API plan type to enum."""
        mapping = {
            'hmo': PlanType.HMO,
            'ppo': PlanType.PPO,
            'epo': PlanType.EPO,
            'pos': PlanType.POS,
            'hdhp': PlanType.HDHP
        }
        return mapping.get(api_value.lower(), PlanType.PPO)
    
    def _apply_rate_limit(self):
        """Apply rate limiting between API requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        
        self.last_request_time = time.time()
    
    def _generate_cache_key(self, *args) -> str:
        """Generate cache key from request parameters."""
        key_parts = [str(arg) for arg in args if arg is not None]
        return "_".join(key_parts).replace(" ", "_")
    
    def _load_from_cache(self, cache_key: str) -> Optional[Dict]:
        """Load data from cache if available and fresh."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            # Check if cache is fresh (less than 24 hours old)
            age = time.time() - cache_file.stat().st_mtime
            if age < 86400:  # 24 hours
                with open(cache_file, 'r') as f:
                    return json.load(f)
        
        return None
    
    def _save_to_cache(self, cache_key: str, data: Dict):
        """Save data to cache."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        with open(cache_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_available_counties(self, zipcode: str) -> List[Dict[str, str]]:
        """
        Get available counties for a ZIP code.
        
        Args:
            zipcode: 5-digit ZIP code
        
        Returns:
            List of counties with FIPS codes
        """
        # TODO: Implement when API access is available
        return []
    
    def _fetch_cms_public_data(self, zipcode: str, county_fips: Optional[str], 
                               metal_levels: Optional[List[str]], plan_types: Optional[List[str]], 
                               year: Optional[int]) -> Dict[str, Any]:
        """
        Fetch plan data from CMS public datasets.
        
        Args:
            zipcode: ZIP code to search
            county_fips: County FIPS code
            metal_levels: Filter by metal levels
            plan_types: Filter by plan types
            year: Plan year
        
        Returns:
            Dictionary with plan data
        """
        try:
            # Build SQL query for CMS data
            year_val = year or datetime.now().year
            query = f"""
            [SELECT 
                "PlanId" as id,
                "PlanMarketingName" as name,
                "IssuerId" as issuer_id,
                "IssuerName" as issuer_name,
                "MetalLevel" as metal_level,
                "PlanType" as plan_type,
                "Premium Adult Individual Age 27" as premium,
                "Medical Deductible - Individual - Standard" as deductible,
                "Medical Maximum Out Of Pocket - Individual - Standard" as moop,
                "Primary Care Physician - Standard" as copay_primary,
                "Specialist - Standard" as copay_specialist,
                "Emergency Room - Standard" as copay_er,
                "Generic Drugs - Standard" as drug_tier1,
                "Quality Rating - Global Rating" as quality_rating
            FROM "{self.CMS_DATASET_ID}"
            WHERE "ServiceAreaId" LIKE '%{zipcode[:3]}%'
            """
            
            if metal_levels:
                levels_str = "','".join(metal_levels)
                query += f' AND "MetalLevel" IN (\'{levels_str}\')'
            
            if plan_types:
                types_str = "','".join(plan_types)
                query += f' AND "PlanType" IN (\'{types_str}\')'
            
            query += " LIMIT 100]"
            
            # Make request to CMS API
            response = self.session.get(
                self.CMS_QHP_URL,
                params={'query': query},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                # Transform to expected format
                return {'plans': data}
            
        except Exception as e:
            logger.debug(f"CMS data fetch error: {e}")
        
        return {}
    
    def validate_api_access(self) -> bool:
        """
        Validate API access and credentials.
        
        Returns:
            True if API is accessible, False otherwise
        """
        if self.api_key:
            try:
                response = self.session.get(
                    f"{self.BASE_URL}/status",
                    headers={'Authorization': f'Bearer {self.api_key}'},
                    timeout=10
                )
                return response.status_code == 200
            except:
                pass
        
        # Try CMS public endpoint
        try:
            response = self.session.get(
                self.CMS_QHP_URL,
                params={'query': f'[SELECT COUNT(*) FROM "{self.CMS_DATASET_ID}" LIMIT 1]'},
                timeout=10
            )
            return response.status_code == 200
        except:
            return False