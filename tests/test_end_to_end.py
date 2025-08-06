#!/usr/bin/env python3
"""
End-to-end tests for HealthPlan Navigator pipeline.
"""

import unittest
import tempfile
import json
from pathlib import Path
from datetime import datetime

from healthplan_navigator.core.models import (
    Client, PersonalInfo, MedicalProfile, Priorities,
    Provider, Medication, Priority, Plan, MetalLevel, PlanType
)
from healthplan_navigator.core.ingest import DocumentParser
from healthplan_navigator.analysis.engine import AnalysisEngine
from healthplan_navigator.output.report import ReportGenerator
from healthplan_navigator.analyzer import HealthPlanAnalyzer


class TestEndToEndPipeline(unittest.TestCase):
    """Test the complete analysis pipeline from ingestion to reporting."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_client = self._create_test_client()
        self.test_plans = self._create_test_plans()
    
    def _create_test_client(self) -> Client:
        """Create a test client profile."""
        personal = PersonalInfo(
            full_name="Test User",
            dob="1980-01-01",
            zipcode="12345",
            household_size=2,
            annual_income=60000,
            csr_eligible=False
        )
        
        medical = MedicalProfile(
            providers=[
                Provider(
                    name="Dr. Test",
                    specialty="Primary Care",
                    priority=Priority.MUST_KEEP,
                    visit_frequency=4
                )
            ],
            medications=[
                Medication(
                    name="Metformin",
                    dosage="500mg",
                    frequency="Daily",
                    annual_doses=365
                )
            ]
        )
        
        priorities = Priorities(
            keep_providers=5,
            minimize_total_cost=4,
            predictable_costs=3,
            avoid_prior_auth=3,
            simple_admin=3
        )
        
        return Client(personal=personal, medical_profile=medical, priorities=priorities)
    
    def _create_test_plans(self) -> list:
        """Create test plan objects."""
        plans = []
        
        # Bronze plan - low premium, high deductible
        plans.append(Plan(
            plan_id="TEST001",
            marketing_name="Test Bronze Plan",
            issuer="Test Insurance Co",
            metal_level=MetalLevel.BRONZE,
            plan_type=PlanType.PPO,
            monthly_premium=200,
            deductible=7000,
            oop_max=8700,
            copay_primary=40,
            copay_specialist=80,
            copay_er=500,
            coinsurance=0.4,
            provider_network=None,
            drug_formulary=None,
            quality_rating=3.5,
            customer_rating=3.0
        ))
        
        # Silver plan - moderate premium and deductible
        plans.append(Plan(
            plan_id="TEST002",
            marketing_name="Test Silver Plan",
            issuer="Test Insurance Co",
            metal_level=MetalLevel.SILVER,
            plan_type=PlanType.HMO,
            monthly_premium=350,
            deductible=3500,
            oop_max=7500,
            copay_primary=25,
            copay_specialist=50,
            copay_er=350,
            coinsurance=0.25,
            provider_network=None,
            drug_formulary=None,
            quality_rating=4.0,
            customer_rating=3.5
        ))
        
        # Gold plan - high premium, low deductible
        plans.append(Plan(
            plan_id="TEST003",
            marketing_name="Test Gold Plan",
            issuer="Premium Insurance Co",
            metal_level=MetalLevel.GOLD,
            plan_type=PlanType.PPO,
            monthly_premium=500,
            deductible=1500,
            oop_max=6000,
            copay_primary=15,
            copay_specialist=30,
            copay_er=250,
            coinsurance=0.2,
            provider_network=None,
            drug_formulary=None,
            quality_rating=4.5,
            customer_rating=4.0
        ))
        
        return plans
    
    def test_analysis_engine(self):
        """Test the analysis engine scoring and ranking."""
        engine = AnalysisEngine()
        report = engine.analyze_plans(self.test_client, self.test_plans)
        
        # Verify report structure
        self.assertIsNotNone(report)
        self.assertEqual(len(report.plan_analyses), 3)
        self.assertEqual(len(report.top_recommendations), 3)
        
        # Verify plans are ranked by score
        scores = [p.metrics.weighted_total_score for p in report.plan_analyses]
        self.assertEqual(scores, sorted(scores, reverse=True))
        
        # Verify each plan has all metrics
        for analysis in report.plan_analyses:
            self.assertIsNotNone(analysis.metrics.provider_network_score)
            self.assertIsNotNone(analysis.metrics.medication_coverage_score)
            self.assertIsNotNone(analysis.metrics.total_cost_score)
            self.assertIsNotNone(analysis.metrics.financial_protection_score)
            self.assertIsNotNone(analysis.metrics.administrative_simplicity_score)
            self.assertIsNotNone(analysis.metrics.plan_quality_score)
            self.assertIsNotNone(analysis.metrics.weighted_total_score)
    
    def test_scoring_matrix_generation(self):
        """Test scoring matrix generation."""
        engine = AnalysisEngine()
        report = engine.analyze_plans(self.test_client, self.test_plans)
        
        matrix = engine.generate_scoring_matrix(report)
        
        # Verify matrix structure
        self.assertEqual(len(matrix), 3)
        
        for row in matrix:
            self.assertIn('Plan Name', row)
            self.assertIn('OVERALL SCORE', row)
            self.assertIn('Rank', row)
            self.assertIn('Monthly Premium', row)
    
    def test_report_generation(self):
        """Test report generation in various formats."""
        engine = AnalysisEngine()
        report = engine.analyze_plans(self.test_client, self.test_plans)
        
        report_gen = ReportGenerator(self.temp_dir)
        
        # Test executive summary
        summary = report_gen.generate_executive_summary(report)
        self.assertIsNotNone(summary)
        self.assertIn('Executive Summary', summary)
        self.assertIn(report.top_recommendations[0].plan.marketing_name, summary)
        
        # Test CSV generation
        csv_file = report_gen.generate_scoring_matrix_csv(report)
        self.assertTrue(Path(csv_file).exists())
        
        # Test JSON export
        json_file = report_gen.generate_json_export(report)
        self.assertTrue(Path(json_file).exists())
        
        # Verify JSON content
        with open(json_file, 'r') as f:
            json_data = json.load(f)
            self.assertIn('client', json_data)
            self.assertIn('plan_analyses', json_data)
            self.assertEqual(len(json_data['plan_analyses']), 3)
    
    def test_healthplan_analyzer_orchestrator(self):
        """Test the unified HealthPlanAnalyzer orchestrator."""
        analyzer = HealthPlanAnalyzer(output_dir=self.temp_dir)
        
        # Create test plan files
        plan_dir = Path(self.temp_dir) / "plans"
        plan_dir.mkdir(exist_ok=True)
        
        for i, plan in enumerate(self.test_plans):
            plan_file = plan_dir / f"plan_{i}.json"
            with open(plan_file, 'w') as f:
                json.dump({
                    'plan_id': plan.plan_id,
                    'marketing_name': plan.marketing_name,
                    'issuer': plan.issuer,
                    'metal_level': plan.metal_level.value,
                    'monthly_premium': plan.monthly_premium,
                    'deductible': plan.deductible,
                    'oop_max': plan.oop_max
                }, f)
        
        # Run analysis through orchestrator
        report = analyzer.analyze(
            client=self.test_client,
            plan_sources=str(plan_dir),
            formats=['summary', 'csv']
        )
        
        # Verify results
        self.assertIsNotNone(report)
        self.assertTrue(len(report.plan_analyses) > 0)
        
        # Check if reports were generated
        output_files = list(Path(self.temp_dir).glob("*"))
        self.assertTrue(len(output_files) > 0)
    
    def test_single_plan_analysis(self):
        """Test analyzing a single plan."""
        analyzer = HealthPlanAnalyzer(output_dir=self.temp_dir)
        
        result = analyzer.analyze_single_plan(
            self.test_client,
            self.test_plans[0]
        )
        
        # Verify result structure
        self.assertIn('plan_name', result)
        self.assertIn('overall_score', result)
        self.assertIn('metrics', result)
        self.assertIn('strengths', result)
        self.assertIn('concerns', result)
        
        # Verify metrics
        metrics = result['metrics']
        self.assertIn('provider_network', metrics)
        self.assertIn('medication_coverage', metrics)
        self.assertIn('total_cost', metrics)
    
    def test_comparison_summary(self):
        """Test comparison summary generation."""
        engine = AnalysisEngine()
        report = engine.analyze_plans(self.test_client, self.test_plans)
        
        summary = engine.generate_comparison_summary(report)
        
        # Verify summary structure
        self.assertIn('total_plans_analyzed', summary)
        self.assertEqual(summary['total_plans_analyzed'], 3)
        
        self.assertIn('recommended_plan', summary)
        self.assertIn('key_strengths', summary)
        self.assertIn('potential_concerns', summary)
        self.assertIn('cost_comparison', summary)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)


class TestDocumentParsing(unittest.TestCase):
    """Test document parsing capabilities."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = DocumentParser()
        self.temp_dir = tempfile.mkdtemp()
    
    def test_json_parsing(self):
        """Test JSON plan parsing."""
        json_file = Path(self.temp_dir) / "test_plan.json"
        
        plan_data = {
            'plan_id': 'JSON001',
            'marketing_name': 'JSON Test Plan',
            'issuer': 'JSON Insurance',
            'metal_level': 'silver',
            'monthly_premium': 300,
            'deductible': 3000,
            'oop_max': 7000
        }
        
        with open(json_file, 'w') as f:
            json.dump(plan_data, f)
        
        plan = self.parser.parse_json(str(json_file))
        
        self.assertIsNotNone(plan)
        self.assertEqual(plan.plan_id, 'JSON001')
        self.assertEqual(plan.marketing_name, 'JSON Test Plan')
        self.assertEqual(plan.monthly_premium, 300)
    
    def test_csv_parsing(self):
        """Test CSV plan parsing."""
        csv_file = Path(self.temp_dir) / "test_plans.csv"
        
        csv_content = """plan_id,marketing_name,issuer,metal_level,monthly_premium,deductible,oop_max
CSV001,CSV Test Plan 1,CSV Insurance,bronze,250,5000,8700
CSV002,CSV Test Plan 2,CSV Insurance,silver,350,3500,7500"""
        
        with open(csv_file, 'w') as f:
            f.write(csv_content)
        
        plans = self.parser.parse_csv(str(csv_file))
        
        self.assertEqual(len(plans), 2)
        self.assertEqual(plans[0].plan_id, 'CSV001')
        self.assertEqual(plans[1].plan_id, 'CSV002')
    
    def test_batch_parsing(self):
        """Test batch parsing of multiple files."""
        # Create test files
        for i in range(3):
            json_file = Path(self.temp_dir) / f"plan_{i}.json"
            with open(json_file, 'w') as f:
                json.dump({
                    'plan_id': f'BATCH{i:03d}',
                    'marketing_name': f'Batch Plan {i}',
                    'issuer': 'Batch Insurance',
                    'metal_level': 'silver',
                    'monthly_premium': 300 + (i * 50)
                }, f)
        
        plans = self.parser.parse_batch(str(self.temp_dir))
        
        self.assertEqual(len(plans), 3)
        self.assertEqual(plans[0].plan_id, 'BATCH000')
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()