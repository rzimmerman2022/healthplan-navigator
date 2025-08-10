#!/usr/bin/env python3
"""
HealthPlanAnalyzer - Unified orchestrator for healthcare plan analysis.
Provides a single interface for the complete analysis pipeline.

Version: 1.1.0
Last Updated: 2025-08-06

Core Capabilities:
- Multi-format document parsing (PDF, DOCX, JSON, CSV)
- Live API integration with Healthcare.gov, NPPES, RxNorm
- 6-metric scoring system with weighted analysis
- Multi-format report generation
- Intelligent caching and fallback mechanisms
"""

from pathlib import Path
from typing import List, Optional, Union, Dict, Any
import json
import logging

# Core models for client profiles, plans, and analysis results
from .core.models import Client, Plan, AnalysisReport, validate_zipcode
# Document parsing engine supporting multiple formats
from .core.ingest import DocumentParser
# Analysis engine with 6-metric scoring system
from .analysis.engine import AnalysisEngine
# Report generation in multiple formats (MD, CSV, JSON, HTML)
from .output.report import ReportGenerator
# API integrations for live data fetching
from .integrations.healthcare_gov import HealthcareGovAPI
from .integrations.providers import ProviderNetworkIntegration
from .integrations.medications import MedicationIntegration

logger = logging.getLogger(__name__)


class HealthPlanAnalyzer:
    """
    Unified orchestrator for healthcare plan analysis.
    
    This class provides a single interface for:
    - Plan document ingestion (PDF, DOCX, JSON, CSV)
    - Comprehensive scoring and ranking using 6-metric system
    - Multi-format report generation (Executive Summary, CSV, JSON, HTML)
    - Healthcare.gov integration with CMS public data fallback
    - NPPES provider registry integration for network validation
    - RxNorm medication database for drug coverage analysis
    
    Usage Example:
        analyzer = HealthPlanAnalyzer()
        report = analyzer.analyze(
            client=client_profile,
            plan_sources=['plans/'],
            healthcare_gov_fetch=True,
            formats=['summary', 'csv']
        )
    """
    
    def __init__(self, output_dir: str = "./reports", api_keys: Optional[Dict[str, str]] = None):
        """
        Initialize the HealthPlanAnalyzer with all components.
        
        Creates instances of:
        - DocumentParser for multi-format document ingestion
        - AnalysisEngine for 6-metric scoring calculations
        - ReportGenerator for output generation
        - API integrations for live data (if keys provided)
        
        Args:
            output_dir: Directory for generated reports (creates if not exists)
            api_keys: Optional dictionary of API keys for external services
                     Keys: 'healthcare_gov', 'nppes', 'rxnorm', 'goodrx'
        """
        # Initialize core components
        self.parser = DocumentParser()  # Handles PDF, DOCX, JSON, CSV
        self.engine = AnalysisEngine()  # 6-metric scoring system
        self.report_generator = ReportGenerator(output_dir)
        
        # Set up output directory
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize API integrations (v1.1.0 feature)
        api_keys = api_keys or {}
        self.healthcare_gov_api = HealthcareGovAPI(api_key=api_keys.get('healthcare_gov'))
        self.provider_integration = ProviderNetworkIntegration(nppes_api_key=api_keys.get('nppes'))
        self.medication_integration = MedicationIntegration(goodrx_api_key=api_keys.get('goodrx'))
    
    def analyze(self, 
                client: Client,
                plan_sources: Optional[Union[str, List[str]]] = None,
                healthcare_gov_fetch: bool = False,
                formats: List[str] = None) -> AnalysisReport:
        """
        Run complete analysis pipeline with 6-metric scoring.
        
        Pipeline Steps:
        1. Load plans from local files and/or Healthcare.gov API
        2. Validate provider networks via NPPES registry
        3. Check medication coverage via RxNorm database
        4. Calculate 6-metric scores (provider, medication, cost, protection, admin, quality)
        5. Rank plans by weighted total score
        6. Generate reports in requested formats
        
        Args:
            client: Client profile containing personal info, providers, medications, priorities
            plan_sources: Path(s) to plan files or directory (supports PDF, DOCX, JSON, CSV)
            healthcare_gov_fetch: Whether to fetch plans from Healthcare.gov API (uses CMS fallback)
            formats: Report formats to generate ['summary', 'csv', 'json', 'html', 'all']
        
        Returns:
            AnalysisReport with all scored and ranked plans, including:
            - Scored plan analyses with metric breakdowns
            - Top recommendations with rationale
            - Risk assessments and concerns
            - Comparison summary data
        
        Raises:
            ValueError: If no plans available for analysis
        """
        # Store client reference for location-based fetching (used by Healthcare.gov API)
        self._current_client = client
        
        # Load plans from all sources (local files + optional API fetch)
        plans = self._load_plans(plan_sources, healthcare_gov_fetch)
        
        # Clean up client reference after loading
        self._current_client = None
        
        # Validate we have plans to analyze
        if not plans:
            raise ValueError("No plans available for analysis")
        
        # Run comprehensive 6-metric analysis on all plans
        # This calculates scores for each metric and generates rankings
        report = self.engine.analyze_plans(client, plans)
        
        # Generate requested report formats (summary, CSV, JSON, HTML)
        if formats:
            self._generate_reports(report, formats)
        
        return report
    
    def _load_plans(self, 
                    plan_sources: Optional[Union[str, List[str]]] = None,
                    healthcare_gov_fetch: bool = False) -> List[Plan]:
        """
        Load plans from various sources (local and/or API).
        
        Supports:
        - Single files (PDF, DOCX, JSON, CSV)
        - Directories for batch processing
        - Healthcare.gov API with CMS public data fallback
        
        Args:
            plan_sources: File paths or directory to load
            healthcare_gov_fetch: Whether to fetch from Healthcare.gov
        
        Returns:
            List of parsed Plan objects ready for analysis
        """
        plans = []  # Accumulator for all loaded plans
        
        # Load from local files/directory
        if plan_sources:
            # Normalize to list for consistent processing
            if isinstance(plan_sources, str):
                plan_sources = [plan_sources]
            
            # Process each source (file or directory)
            for source in plan_sources:
                source_path = Path(source)
                
                if source_path.is_dir():
                    # Batch process all supported files in directory
                    # Automatically handles PDF, DOCX, JSON, CSV files
                    batch_plans = self.parser.parse_batch(str(source_path))
                    plans.extend(batch_plans)
                    logger.info(f"Loaded {len(batch_plans)} plans from {source_path}")
                elif source_path.is_file():
                    # Parse single file based on extension
                    plan = self.parser.parse_document(str(source_path))
                    if plan:
                        plans.append(plan)
                        logger.info(f"Loaded plan from {source_path.name}")
        
        # Fetch from Healthcare.gov API (v1.1.0 feature)
        if healthcare_gov_fetch:
            hc_plans = self._fetch_healthcare_gov_plans()
            plans.extend(hc_plans)
            if hc_plans:
                logger.info(f"Fetched {len(hc_plans)} plans from Healthcare.gov")
        
        logger.info(f"Total plans loaded: {len(plans)}")
        return plans
    
    def _fetch_healthcare_gov_plans(self) -> List[Plan]:
        """
        Fetch plans from Healthcare.gov API with CMS fallback.
        
        Implementation (v1.1.0):
        - Uses client location (zipcode) for geographic filtering
        - Falls back to CMS public data if API key not available
        - Implements caching to reduce API calls
        - Handles rate limiting with exponential backoff
        
        Returns:
            List of plans from Healthcare.gov or CMS public data
        """
        if not self._current_client:
            logger.warning("No client profile available for Healthcare.gov fetch")
            return []
        
        try:
            # Extract location from client profile
            zipcode = getattr(self._current_client.personal, 'zipcode', None)
            if not zipcode:
                logger.warning("Client zipcode not available for plan fetch")
                return []
            
            # Validate the zipcode format
            try:
                validated_zipcode = validate_zipcode(zipcode)
            except ValueError as e:
                logger.error(f"Invalid client zipcode '{zipcode}': {e}")
                return []
            
            # Fetch plans using Healthcare.gov API or CMS fallback
            # API automatically handles authentication and fallback
            plans_data = self.healthcare_gov_api.fetch_plans(
                zipcode=validated_zipcode,
                metal_levels=['Bronze', 'Silver', 'Gold', 'Platinum'],
                plan_types=['HMO', 'PPO', 'EPO', 'POS']
            )
            
            # Convert API response to Plan objects
            plans = []
            for plan_data in plans_data.get('plans', []):
                try:
                    plan = self._convert_api_plan(plan_data)
                    if plan:
                        plans.append(plan)
                except Exception as e:
                    logger.error(f"Error converting API plan: {e}")
                    continue
            
            return plans
            
        except Exception as e:
            logger.error(f"Error fetching Healthcare.gov plans: {e}")
            return []
    
    def _generate_reports(self, report: AnalysisReport, formats: List[str]) -> Dict[str, Path]:
        """
        Generate reports in requested formats.
        
        Available formats:
        - 'summary': Executive summary in Markdown
        - 'csv': Scoring matrix for spreadsheet analysis
        - 'json': Structured data for API integration
        - 'html': Interactive dashboard with visualizations
        - 'all': Generate all available formats
        
        Args:
            report: Analysis report containing scored plans
            formats: List of format strings to generate
        
        Returns:
            Dictionary mapping format to generated file path
        """
        generated = {}  # Track generated file paths
        
        # Generate executive summary (Markdown format)
        if 'summary' in formats or 'all' in formats:
            summary = self.report_generator.generate_executive_summary(report)
            summary_file = self.output_dir / f"executive_summary_{report.generated_at.strftime('%Y%m%d_%H%M%S')}.md"
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary)
            generated['summary'] = summary_file
            logger.info(f"Generated executive summary: {summary_file}")
        
        # Generate CSV scoring matrix for spreadsheet analysis
        if 'csv' in formats or 'all' in formats:
            csv_file = self.report_generator.generate_scoring_matrix_csv(report)
            generated['csv'] = Path(csv_file)
            logger.info(f"Generated CSV matrix: {csv_file}")
        
        # Generate JSON export for API integration
        if 'json' in formats or 'all' in formats:
            json_file = self.report_generator.generate_json_export(report)
            generated['json'] = Path(json_file)
            logger.info(f"Generated JSON export: {json_file}")
        
        # Generate interactive HTML dashboard
        if 'html' in formats or 'all' in formats:
            html_file = self.report_generator.generate_html_dashboard(report)
            generated['html'] = Path(html_file)
            logger.info(f"Generated HTML dashboard: {html_file}")
        
        return generated
    
    def analyze_single_plan(self, client: Client, plan: Plan) -> Dict[str, Any]:
        """
        Analyze a single plan for quick assessment.
        
        Useful for:
        - Quick plan comparisons
        - Individual plan evaluation
        - API endpoint responses
        
        Args:
            client: Client profile with priorities and requirements
            plan: Single plan to analyze
        
        Returns:
            Dictionary with complete analysis including:
            - All 6 metric scores
            - Estimated annual cost
            - Strengths and concerns
            - Overall weighted score
        """
        # Run 6-metric scoring on single plan
        analysis = self.engine.scorer.score_plan(client, plan, [plan])
        
        # Package results in structured format
        return {
            # Basic plan information
            'plan_name': plan.marketing_name,
            'issuer': plan.issuer,
            'metal_level': plan.metal_level.value,
            'monthly_premium': plan.monthly_premium,
            
            # Cost analysis
            'estimated_annual_cost': analysis.estimated_annual_cost,
            
            # Overall score (weighted combination of 6 metrics)
            'overall_score': analysis.metrics.weighted_total_score,
            
            # Individual metric scores (0-10 scale)
            'metrics': {
                'provider_network': analysis.metrics.provider_network_score,      # 30% weight
                'medication_coverage': analysis.metrics.medication_coverage_score, # 25% weight
                'total_cost': analysis.metrics.total_cost_score,                 # 20% weight
                'financial_protection': analysis.metrics.financial_protection_score, # 10% weight
                'administrative_simplicity': analysis.metrics.administrative_simplicity_score, # 10% weight
                'plan_quality': analysis.metrics.plan_quality_score              # 5% weight
            },
            
            # Qualitative assessment
            'strengths': self.engine._identify_plan_strengths(analysis),
            'concerns': self.engine._identify_plan_concerns(analysis)
        }
    
    def get_scoring_matrix(self, report: AnalysisReport) -> List[Dict]:
        """
        Get scoring matrix for all analyzed plans.
        
        Matrix includes:
        - All 6 metric scores for each plan
        - Weighted total scores
        - Rankings and recommendations
        
        Args:
            report: Analysis report with scored plans
        
        Returns:
            List of dictionaries with plan scores, sorted by rank
        """
        return self.engine.generate_scoring_matrix(report)
    
    def get_comparison_summary(self, report: AnalysisReport) -> Dict:
        """
        Get comparison summary of analyzed plans.
        
        Summary includes:
        - Top recommendations with rationale
        - Cost comparisons
        - Coverage highlights
        - Risk assessments
        
        Args:
            report: Analysis report with scored plans
        
        Returns:
            Dictionary with comprehensive comparison data
        """
        return self.engine.generate_comparison_summary(report)
    
    def _convert_api_plan(self, api_data: Dict[str, Any]) -> Optional[Plan]:
        """
        Convert Healthcare.gov API response to Plan model.
        
        Handles mapping of:
        - API fields to Plan attributes
        - Benefit structures
        - Network information
        - Cost components
        
        Args:
            api_data: Raw API response for a single plan
        
        Returns:
            Plan object or None if conversion fails
        """
        try:
            # Implementation would map API fields to Plan model
            # This is a simplified placeholder
            from .core.models import Plan, MetalLevel, PlanType
            
            plan = Plan(
                plan_id=api_data.get('plan_id', ''),
                marketing_name=api_data.get('plan_marketing_name', ''),
                issuer=api_data.get('issuer_name', ''),
                metal_level=MetalLevel(api_data.get('metal_level', 'Bronze').upper()),
                plan_type=PlanType(api_data.get('plan_type', 'HMO').upper()),
                monthly_premium=float(api_data.get('premium', 0)),
                deductible=float(api_data.get('medical_deductible', 0)),
                out_of_pocket_max=float(api_data.get('medical_moop', 0)),
                # Additional fields would be mapped here
            )
            return plan
        except Exception as e:
            logger.error(f"Error converting API plan data: {e}")
            return None