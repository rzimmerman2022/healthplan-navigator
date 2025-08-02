from typing import List, Dict
from ..core.models import Client, Plan, PlanAnalysis, AnalysisReport
from ..core.score import HealthPlanScorer


class AnalysisEngine:
    """Main analysis engine that orchestrates plan scoring and ranking."""
    
    def __init__(self):
        self.scorer = HealthPlanScorer()
    
    def analyze_plans(self, client: Client, plans: List[Plan]) -> AnalysisReport:
        """
        Analyze all plans for a client and generate comprehensive report.
        Returns plans ranked by weighted score (0-10 scale).
        """
        if not plans:
            raise ValueError("No plans provided for analysis")
        
        # Score all plans
        plan_analyses = []
        for plan in plans:
            analysis = self.scorer.score_plan(client, plan, plans)
            plan_analyses.append(analysis)
        
        # Sort by weighted total score (descending)
        plan_analyses.sort(key=lambda x: x.metrics.weighted_total_score, reverse=True)
        
        # Get top 3 recommendations
        top_recommendations = plan_analyses[:3]
        
        # Create comprehensive report
        report = AnalysisReport(
            client=client,
            plan_analyses=plan_analyses,
            top_recommendations=top_recommendations
        )
        
        return report
    
    def generate_scoring_matrix(self, report: AnalysisReport) -> List[Dict]:
        """
        Generate a scoring matrix showing all metrics for all plans.
        Returns a list of dictionaries suitable for CSV export or table display.
        """
        matrix = []
        
        for analysis in report.plan_analyses:
            row = {
                'Plan Name': analysis.plan.marketing_name,
                'Plan ID': analysis.plan.plan_id,
                'Issuer': analysis.plan.issuer,
                'Metal Level': analysis.plan.metal_level.value,
                'Monthly Premium': f"${analysis.plan.monthly_premium:.2f}",
                'Estimated Annual Cost': f"${analysis.estimated_annual_cost:.2f}",
                'Provider Network Score': f"{analysis.metrics.provider_network_score:.1f}/10",
                'Medication Coverage Score': f"{analysis.metrics.medication_coverage_score:.1f}/10",
                'Total Cost Score': f"{analysis.metrics.total_cost_score:.1f}/10",
                'Financial Protection Score': f"{analysis.metrics.financial_protection_score:.1f}/10",
                'Administrative Score': f"{analysis.metrics.administrative_simplicity_score:.1f}/10",
                'Plan Quality Score': f"{analysis.metrics.plan_quality_score:.1f}/10",
                'OVERALL SCORE': f"{analysis.metrics.weighted_total_score:.1f}/10",
                'Rank': report.plan_analyses.index(analysis) + 1
            }
            matrix.append(row)
        
        return matrix
    
    def generate_comparison_summary(self, report: AnalysisReport) -> Dict:
        """Generate a summary comparison of top plans."""
        if not report.top_recommendations:
            return {}
        
        top_plan = report.top_recommendations[0]
        
        summary = {
            'total_plans_analyzed': len(report.plan_analyses),
            'recommended_plan': {
                'name': top_plan.plan.marketing_name,
                'issuer': top_plan.plan.issuer,
                'score': top_plan.metrics.weighted_total_score,
                'monthly_premium': top_plan.plan.monthly_premium,
                'estimated_annual_cost': top_plan.estimated_annual_cost
            },
            'key_strengths': self._identify_plan_strengths(top_plan),
            'potential_concerns': self._identify_plan_concerns(top_plan),
            'cost_comparison': {
                'lowest_cost_plan': min(report.plan_analyses, key=lambda x: x.estimated_annual_cost),
                'highest_cost_plan': max(report.plan_analyses, key=lambda x: x.estimated_annual_cost),
                'cost_savings_vs_highest': max(report.plan_analyses, key=lambda x: x.estimated_annual_cost).estimated_annual_cost - top_plan.estimated_annual_cost
            }
        }
        
        return summary
    
    def _identify_plan_strengths(self, analysis: PlanAnalysis) -> List[str]:
        """Identify the key strengths of a plan based on its scores."""
        strengths = []
        
        if analysis.metrics.provider_network_score >= 8:
            strengths.append("Excellent provider network coverage")
        
        if analysis.metrics.medication_coverage_score >= 8:
            strengths.append("Strong medication formulary coverage")
        
        if analysis.metrics.total_cost_score >= 8:
            strengths.append("Very competitive total cost")
        
        if analysis.metrics.financial_protection_score >= 8:
            strengths.append("Strong financial protection with low deductible/OOPM")
        
        if analysis.metrics.administrative_simplicity_score >= 8:
            strengths.append("Simple administration with minimal barriers")
        
        if analysis.metrics.plan_quality_score >= 8:
            strengths.append("High plan quality rating")
        
        return strengths
    
    def _identify_plan_concerns(self, analysis: PlanAnalysis) -> List[str]:
        """Identify potential concerns with a plan based on its scores."""
        concerns = []
        
        if analysis.metrics.provider_network_score <= 4:
            concerns.append("Limited provider network coverage")
        
        if analysis.metrics.medication_coverage_score <= 4:
            concerns.append("Poor medication formulary coverage")
        
        if analysis.metrics.total_cost_score <= 4:
            concerns.append("Higher than average total cost")
        
        if analysis.metrics.financial_protection_score <= 4:
            concerns.append("High deductible or out-of-pocket maximum")
        
        if analysis.metrics.administrative_simplicity_score <= 4:
            concerns.append("Complex administration with potential barriers")
        
        if analysis.metrics.plan_quality_score <= 4:
            concerns.append("Below average plan quality rating")
        
        return concerns