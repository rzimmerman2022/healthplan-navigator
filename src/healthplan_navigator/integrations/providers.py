#!/usr/bin/env python3
"""
Provider Network Integration Module
Handles provider network data from various sources.
"""

import json
import logging
import os
from typing import List, Dict, Optional, Set, Any
from pathlib import Path
import requests
from fuzzywuzzy import fuzz

from ..core.models import Provider, ProviderNetwork, Priority

logger = logging.getLogger(__name__)


class ProviderNetworkIntegration:
    """
    Manages provider network data integration from multiple sources.
    
    Supports:
    - NPPES (National Provider Identifier) database
    - Insurance carrier provider directories
    - Healthcare.gov provider networks
    - Local provider database caching
    """
    
    # NPPES API endpoint (public, no auth required)
    NPPES_API_URL = "https://npiregistry.cms.hhs.gov/api/"
    NPPES_SEARCH_ENDPOINT = "?version=2.1"
    
    def __init__(self, cache_dir: str = "./cache/providers", nppes_api_key: Optional[str] = None):
        """
        Initialize provider network integration.
        
        Args:
            cache_dir: Directory for caching provider data
            nppes_api_key: Optional API key for enhanced NPPES access
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.provider_cache = {}
        self.nppes_api_key = nppes_api_key or os.getenv('NPPES_API_KEY')
        self.session = requests.Session()
        self._load_provider_cache()
    
    def check_provider_in_network(self, 
                                  provider: Provider, 
                                  network: ProviderNetwork,
                                  fuzzy_match: bool = True) -> bool:
        """
        Check if a provider is in a specific network.
        
        Args:
            provider: Provider to check
            network: Network to search in
            fuzzy_match: Whether to use fuzzy string matching
        
        Returns:
            True if provider is found in network
        """
        if not network or not network.providers:
            return False
        
        # Try exact match first
        for network_provider in network.providers:
            if self._exact_match(provider, network_provider):
                return True
        
        # Try fuzzy match if enabled
        if fuzzy_match:
            for network_provider in network.providers:
                if self._fuzzy_match(provider, network_provider):
                    return True
        
        return False
    
    def _exact_match(self, provider1: Provider, provider2: Dict) -> bool:
        """Check for exact provider match."""
        # Match by NPI if available
        if hasattr(provider1, 'npi') and provider2.get('npi'):
            return provider1.npi == provider2['npi']
        
        # Match by name and specialty
        name_match = provider1.name.lower() == provider2.get('name', '').lower()
        specialty_match = provider1.specialty.lower() == provider2.get('specialty', '').lower()
        
        return name_match and specialty_match
    
    def _fuzzy_match(self, provider1: Provider, provider2: Dict) -> bool:
        """Check for fuzzy provider match."""
        # Use fuzzy string matching for names
        name_ratio = fuzz.ratio(
            provider1.name.lower(),
            provider2.get('name', '').lower()
        )
        
        # Check if specialty matches (exact or partial)
        specialty_ratio = fuzz.partial_ratio(
            provider1.specialty.lower(),
            provider2.get('specialty', '').lower()
        )
        
        # Consider a match if name is >85% similar and specialty is >70% similar
        return name_ratio > 85 and specialty_ratio > 70
    
    def fetch_network_details(self, network_id: str) -> Optional[ProviderNetwork]:
        """
        Fetch detailed provider network information.
        
        Args:
            network_id: Network identifier
        
        Returns:
            ProviderNetwork object with provider details
        """
        # Check cache first
        cache_file = self.cache_dir / f"network_{network_id}.json"
        
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                data = json.load(f)
                return self._deserialize_network(data)
        
        # TODO: Implement API calls to fetch network data
        logger.warning(f"Network {network_id} not found in cache")
        return None
    
    def _deserialize_network(self, data: Dict) -> ProviderNetwork:
        """Convert JSON data to ProviderNetwork object."""
        return ProviderNetwork(
            network_id=data.get('network_id'),
            name=data.get('name'),
            providers=data.get('providers', []),
            hospitals=data.get('hospitals', []),
            urgent_care_centers=data.get('urgent_care_centers', [])
        )
    
    def search_providers(self, 
                        specialty: Optional[str] = None,
                        location: Optional[str] = None,
                        radius_miles: int = 25) -> List[Dict]:
        """
        Search for providers by specialty and location.
        
        Args:
            specialty: Medical specialty to search for
            location: ZIP code or city/state
            radius_miles: Search radius in miles
        
        Returns:
            List of provider dictionaries
        """
        results = []
        
        # Try NPPES API first
        try:
            nppes_results = self._search_nppes(specialty, location)
            if nppes_results:
                results.extend(nppes_results)
        except Exception as e:
            logger.debug(f"NPPES search error: {e}")
        
        # Search in cache as fallback
        for provider_id, provider_data in self.provider_cache.items():
            if specialty and specialty.lower() in provider_data.get('specialty', '').lower():
                results.append(provider_data)
        
        return results[:50]  # Limit results
    
    def _search_nppes(self, specialty: Optional[str], location: Optional[str]) -> List[Dict]:
        """
        Search NPPES registry for providers.
        
        Args:
            specialty: Medical specialty
            location: ZIP code or city/state
        
        Returns:
            List of provider data from NPPES
        """
        params = {
            'enumeration_type': '1',  # Individual providers
            'limit': 25
        }
        
        if specialty:
            params['taxonomy_description'] = specialty
        
        if location:
            if location.isdigit() and len(location) == 5:
                params['postal_code'] = location
            else:
                params['city'] = location
        
        try:
            response = self.session.get(
                self.NPPES_API_URL + self.NPPES_SEARCH_ENDPOINT,
                params=params,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                providers = []
                
                for result in data.get('results', []):
                    provider = {
                        'npi': result.get('number'),
                        'name': f"{result.get('basic', {}).get('first_name', '')} {result.get('basic', {}).get('last_name', '')}".strip(),
                        'specialty': result.get('taxonomies', [{}])[0].get('desc', '') if result.get('taxonomies') else '',
                        'address': result.get('addresses', [{}])[0] if result.get('addresses') else {},
                        'phone': result.get('addresses', [{}])[0].get('telephone_number', '') if result.get('addresses') else ''
                    }
                    providers.append(provider)
                    
                    # Cache the provider
                    self.provider_cache[provider['npi']] = provider
                
                self._save_provider_cache()
                return providers
                
        except Exception as e:
            logger.error(f"NPPES API error: {e}")
        
        return []
    
    def _load_provider_cache(self):
        """Load provider cache from disk."""
        cache_file = self.cache_dir / "provider_cache.json"
        
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                self.provider_cache = json.load(f)
    
    def _save_provider_cache(self):
        """Save provider cache to disk."""
        cache_file = self.cache_dir / "provider_cache.json"
        
        with open(cache_file, 'w') as f:
            json.dump(self.provider_cache, f, indent=2)
    
    def calculate_network_coverage(self, 
                                   client_providers: List[Provider],
                                   network: ProviderNetwork) -> Dict[str, Any]:
        """
        Calculate how well a network covers a client's providers.
        
        Args:
            client_providers: Client's current providers
            network: Network to evaluate
        
        Returns:
            Dictionary with coverage statistics
        """
        must_keep_providers = [p for p in client_providers if p.priority == Priority.MUST_KEEP]
        nice_to_keep_providers = [p for p in client_providers if p.priority == Priority.NICE_TO_KEEP]
        
        must_keep_covered = sum(
            1 for p in must_keep_providers 
            if self.check_provider_in_network(p, network)
        )
        
        nice_to_keep_covered = sum(
            1 for p in nice_to_keep_providers 
            if self.check_provider_in_network(p, network)
        )
        
        total_covered = must_keep_covered + nice_to_keep_covered
        total_providers = len(client_providers)
        
        return {
            'total_providers': total_providers,
            'total_covered': total_covered,
            'coverage_percentage': (total_covered / total_providers * 100) if total_providers > 0 else 0,
            'must_keep_total': len(must_keep_providers),
            'must_keep_covered': must_keep_covered,
            'must_keep_percentage': (must_keep_covered / len(must_keep_providers) * 100) if must_keep_providers else 100,
            'nice_to_keep_total': len(nice_to_keep_providers),
            'nice_to_keep_covered': nice_to_keep_covered,
            'nice_to_keep_percentage': (nice_to_keep_covered / len(nice_to_keep_providers) * 100) if nice_to_keep_providers else 100
        }
    
    def estimate_network_size(self, network: ProviderNetwork) -> str:
        """
        Estimate the size/breadth of a provider network.
        
        Args:
            network: Network to evaluate
        
        Returns:
            Size category: 'Large', 'Medium', 'Small', or 'Unknown'
        """
        if not network:
            return 'Unknown'
        
        provider_count = len(network.providers) if network.providers else 0
        hospital_count = len(network.hospitals) if network.hospitals else 0
        
        total_facilities = provider_count + hospital_count
        
        if total_facilities > 1000:
            return 'Large'
        elif total_facilities > 250:
            return 'Medium'
        elif total_facilities > 0:
            return 'Small'
        else:
            return 'Unknown'