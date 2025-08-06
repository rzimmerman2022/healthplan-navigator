#!/usr/bin/env python3
"""
HealthPlanAnalyzer - Unified orchestrator for healthcare plan analysis.
Provides a single interface for the complete analysis pipeline.
"""

from pathlib import Path
from typing import List, Optional, Union, Dict, Any
import json
import logging

from .core.models import Client, Plan, AnalysisReport
from .core.ingest import DocumentParser
from .analysis.engine import AnalysisEngine
from .output.report import ReportGenerator
from .integrations.healthcare_gov import HealthcareGovAPI
from .integrations.providers import ProviderNetworkIntegration
from .integrations.medications import MedicationIntegration

logger = logging.getLogger(__name__)


class HealthPlanAnalyzer:
    """
    Unified orchestrator for healthcare plan analysis.
    
    This class provides a single interface for:
    - Plan document ingestion (PDF, DOCX, JSON, CSV)
    - Comprehensive scoring and ranking
    - Multi-format report generation
    - Healthcare.gov integration (future)
    """
    
    def __init__(self, output_dir: str = "./reports"):
        """
        Initialize the HealthPlanAnalyzer.
        
        Args:
            output_dir: Directory for generated reports
        """
        self.parser = DocumentParser()
        self.engine = AnalysisEngine()
        self.report_generator = ReportGenerator(output_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def analyze(self, 
                client: Client,
                plan_sources: Optional[Union[str, List[str]]] = None,
                healthcare_gov_fetch: bool = False,
                formats: List[str] = None) -> AnalysisReport:
        """
        Run complete analysis pipeline.
        
        Args:
            client: Client profile for analysis
            plan_sources: Path(s) to plan files or directory
            healthcare_gov_fetch: Whether to fetch plans from Healthcare.gov API
            formats: Report formats to generate ['summary', 'csv', 'json', 'html']
        
        Returns:
            AnalysisReport with all scored and ranked plans
        """
        # Store client reference for location-based fetching
        self._current_client = client
        
        # Load plans
        plans = self._load_plans(plan_sources, healthcare_gov_fetch)
        
        # Clean up client reference
        self._current_client = None
        
        if not plans:
            raise ValueError("No plans available for analysis")
        
        # Run analysis
        report = self.engine.analyze_plans(client, plans)
        
        # Generate requested reports
        if formats:
            self._generate_reports(report, formats)
        
        return report
    
    def _load_plans(self, 
                    plan_sources: Optional[Union[str, List[str]]] = None,
                    healthcare_gov_fetch: bool = False) -> List[Plan]:
        """
        Load plans from various sources.
        
        Args:
            plan_sources: File paths or directory to load
            healthcare_gov_fetch: Whether to fetch from Healthcare.gov
        
        Returns:
            List of parsed Plan objects
        """
        plans = []
        
        # Load from local files/directory
        if plan_sources:
            if isinstance(plan_sources, str):
                plan_sources = [plan_sources]
            
            for source in plan_sources:
                source_path = Path(source)
                
                if source_path.is_dir():
                    # Batch process directory
                    batch_plans = self.parser.parse_batch(str(source_path))
                    plans.extend(batch_plans)
                elif source_path.is_file():
                    # Single file
                    plan = self.parser.parse_document(str(source_path))
                    if plan:
                        plans.append(plan)
        
        # Fetch from Healthcare.gov (placeholder for future implementation)
        if healthcare_gov_fetch:
            hc_plans = self._fetch_healthcare_gov_plans()
            plans.extend(hc_plans)
        
        return plans
    
    def _fetch_healthcare_gov_plans(self) -> List[Plan]:
        """
        Fetch plans from Healthcare.gov API.
        
        NOTE: This is a placeholder for future implementation.
        Will integrate with Healthcare.gov API when available.
        
        Returns:
            List of plans from Healthcare.gov
        """
        # TODO: Implement Healthcare.gov API integration
        # This will require:
        # 1. API authentication/registration
        # 2. Rate limiting handling
        # 3. Data transformation from API format to Plan model
        # 4. Caching mechanism for API responses
        
        print("Healthcare.gov API integration not yet implemented")
        return []
    
    def _generate_reports(self, report: AnalysisReport, formats: List[str]) -> Dict[str, Path]:
        """
        Generate reports in requested formats.
        
        Args:
            report: Analysis report to generate from
            formats: List of format strings
        
        Returns:
            Dictionary mapping format to generated file path
        """
        generated = {}
        
        if 'summary' in formats or 'all' in formats:
            summary = self.report_generator.generate_executive_summary(report)
            summary_file = self.output_dir / f"executive_summary_{report.generated_at.strftime('%Y%m%d_%H%M%S')}.md"
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary)
            generated['summary'] = summary_file
        
        if 'csv' in formats or 'all' in formats:
            csv_file = self.report_generator.generate_scoring_matrix_csv(report)
            generated['csv'] = Path(csv_file)
        
        if 'json' in formats or 'all' in formats:
            json_file = self.report_generator.generate_json_export(report)
            generated['json'] = Path(json_file)
        
        if 'html' in formats or 'all' in formats:
            html_file = self.report_generator.generate_html_dashboard(report)
            generated['html'] = Path(html_file)
        
        return generated
    
    def analyze_single_plan(self, client: Client, plan: Plan) -> Dict[str, Any]:
        """
        Analyze a single plan for quick assessment.
        
        Args:
            client: Client profile
            plan: Single plan to analyze
        
        Returns:
            Dictionary with plan analysis results
        """
        analysis = self.engine.scorer.score_plan(client, plan, [plan])
        
        return {
            'plan_name': plan.marketing_name,
            'issuer': plan.issuer,
            'metal_level': plan.metal_level.value,
            'monthly_premium': plan.monthly_premium,
            'estimated_annual_cost': analysis.estimated_annual_cost,
            'overall_score': analysis.metrics.weighted_total_score,
            'metrics': {
                'provider_network': analysis.metrics.provider_network_score,
                'medication_coverage': analysis.metrics.medication_coverage_score,
                'total_cost': analysis.metrics.total_cost_score,
                'financial_protection': analysis.metrics.financial_protection_score,
                'administrative_simplicity': analysis.metrics.administrative_simplicity_score,
                'plan_quality': analysis.metrics.plan_quality_score
            },
            'strengths': self.engine._identify_plan_strengths(analysis),
            'concerns': self.engine._identify_plan_concerns(analysis)
        }
    
    def get_scoring_matrix(self, report: AnalysisReport) -> List[Dict]:
        """
        Get scoring matrix for all analyzed plans.
        
        Args:
            report: Analysis report
        
        Returns:
            List of dictionaries with plan scores
        """
        return self.engine.generate_scoring_matrix(report)
    
    def get_comparison_summary(self, report: AnalysisReport) -> Dict:
        """
        Get comparison summary of analyzed plans.
        
        Args:
            report: Analysis report
        
        Returns:
            Dictionary with comparison data
        """
        return self.engine.generate_comparison_summary(report)