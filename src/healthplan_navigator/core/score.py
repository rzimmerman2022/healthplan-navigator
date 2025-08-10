from typing import List, Dict
from .models import Client, Plan, PlanAnalysis, ScoringMetrics, Priority, CoverageStatus, NetworkStatus


class HealthPlanScorer:
    """
    Implements the 6-metric scoring algorithm for healthcare plans.
    Each metric is scored 0-10 and then weighted to create final ranking.
    """
    
    # Metric weights (must sum to 1.0)
    WEIGHTS = {
        'provider_network': 0.30,
        'medication_coverage': 0.25,
        'total_cost': 0.20,
        'financial_protection': 0.10,
        'administrative_simplicity': 0.10,
        'plan_quality': 0.05
    }
    
    def __init__(self):
        pass
    
    def score_plan(self, client: Client, plan: Plan, all_plans: List[Plan]) -> PlanAnalysis:
        """Score a single plan against client requirements."""
        metrics = ScoringMetrics()
        
        # Calculate each metric
        metrics.provider_network_score = self._score_provider_network(client, plan)
        metrics.medication_coverage_score = self._score_medication_coverage(client, plan)
        metrics.financial_protection_score = self._score_financial_protection(plan)
        metrics.administrative_simplicity_score = self._score_administrative_simplicity(plan)
        metrics.plan_quality_score = self._score_plan_quality(plan)
        
        # Calculate cost score (requires all plans for normalization)
        estimated_cost = self._calculate_annual_cost(client, plan)
        metrics.total_cost_score = self._score_total_cost(estimated_cost, all_plans, client)
        
        # Calculate weighted total
        metrics.weighted_total_score = self._calculate_weighted_score(metrics)
        
        # Create analysis with details
        analysis = PlanAnalysis(
            plan=plan,
            metrics=metrics,
            estimated_annual_cost=estimated_cost,
            provider_coverage_details=self._get_provider_coverage_details(client, plan),
            medication_coverage_details=self._get_medication_coverage_details(client, plan)
        )
        
        return analysis
    
    def _score_provider_network(self, client: Client, plan: Plan) -> float:
        """
        Metric 1: Provider Network Adequacy (30% weight)
        - 10 points: All must-keep providers in-network
        - 7 points: 80%+ must-keep providers in-network
        - 4 points: 50-79% must-keep providers in-network
        - 0 points: <50% must-keep providers in-network
        - Penalty: -2 points if any specialist requires referral
        """
        must_keep_providers = [p for p in client.medical_profile.providers if p.priority == Priority.MUST_KEEP]
        
        if not must_keep_providers:
            score = 10.0  # No must-keep providers = perfect score
        else:
            in_network_count = sum(
                1 for provider in must_keep_providers
                if plan.network.get(provider.name, NetworkStatus.OUT_OF_NETWORK) == NetworkStatus.IN_NETWORK
            )
            coverage_ratio = in_network_count / len(must_keep_providers)
            
            if coverage_ratio == 1.0:
                score = 10.0
            elif coverage_ratio >= 0.8:
                score = 7.0
            elif coverage_ratio >= 0.5:
                score = 4.0
            else:
                score = 0.0
        
        # Apply referral penalty
        if plan.requires_referrals:
            score = max(0, score - 2)
        
        return score
    
    def _score_medication_coverage(self, client: Client, plan: Plan) -> float:
        """
        Metric 2: Medication Coverage & Access (25% weight)
        - Base score: Weighted average of drug coverage scores
        - Covered on formulary: 10 points
        - Not covered but manufacturer program available: 6 points
        - Not covered, no program: 0 points
        - Adjustments: +2 if no prior auth, -3 if uses maximizer
        """
        if not client.medical_profile.medications:
            return 10.0  # No medications = perfect score
        
        total_score = 0
        for medication in client.medical_profile.medications:
            med_score = 0
            coverage = plan.formulary.get(medication.name, CoverageStatus.NOT_COVERED)
            
            if coverage in [CoverageStatus.COVERED, CoverageStatus.TIER1, CoverageStatus.TIER2, CoverageStatus.TIER3, CoverageStatus.TIER4]:
                med_score = 10
            elif coverage == CoverageStatus.NOT_COVERED:
                if medication.manufacturer_program and medication.manufacturer_program.exists:
                    med_score = 6
                else:
                    med_score = 0
            
            total_score += med_score
        
        base_score = total_score / len(client.medical_profile.medications)
        
        # Apply adjustments
        if not plan.administrative.prior_auth_common:
            base_score += 2
        
        if plan.administrative.uses_maximizer:
            base_score -= 3
        
        return max(0, min(10, base_score))
    
    def _calculate_annual_cost(self, client: Client, plan: Plan) -> float:
        """Calculate estimated annual cost for this client and plan."""
        annual_premium = plan.monthly_premium * 12
        
        # Estimate visit costs
        visit_costs = 0
        for provider in client.medical_profile.providers:
            if provider.specialty.lower() in ['primary care', 'family medicine', 'internal medicine']:
                visit_costs += provider.visit_frequency * plan.cost_sharing.primary_care_copay
            else:
                visit_costs += provider.visit_frequency * plan.cost_sharing.specialist_copay
        
        # Estimate medication costs (simplified)
        medication_costs = 0
        for medication in client.medical_profile.medications:
            if medication.manufacturer_program and medication.manufacturer_program.exists:
                medication_costs += medication.annual_doses * (medication.manufacturer_program.expected_copay or 0)
            else:
                # Estimate based on formulary tier
                coverage = plan.formulary.get(medication.name, CoverageStatus.NOT_COVERED)
                if coverage == CoverageStatus.TIER1:
                    medication_costs += medication.annual_doses * 10
                elif coverage == CoverageStatus.TIER2:
                    medication_costs += medication.annual_doses * 50
                elif coverage == CoverageStatus.TIER3:
                    medication_costs += medication.annual_doses * 100
                elif coverage == CoverageStatus.TIER4:
                    medication_costs += medication.annual_doses * 300
                else:
                    medication_costs += medication.annual_doses * 500  # Full cost if not covered
        
        # Add deductible and estimate unexpected care
        estimated_unexpected = 1000  # Conservative estimate
        
        total_cost = annual_premium + plan.deductible + visit_costs + medication_costs + estimated_unexpected
        
        # Cap at out-of-pocket maximum + premiums
        true_cost = min(total_cost, plan.oop_max + annual_premium)
        
        return true_cost
    
    def _score_total_cost(self, estimated_cost: float, all_plans: List[Plan], client: Client) -> float:
        """
        Metric 3: Total Annual Cost (20% weight)
        Normalize scores: lowest cost = 10 points, highest = 0 points
        """
        all_costs = [self._calculate_annual_cost(client, plan) for plan in all_plans]
        min_cost = min(all_costs)
        max_cost = max(all_costs)
        
        if max_cost == min_cost:
            return 10.0  # All plans cost the same
        
        # Linear interpolation: lowest cost gets 10, highest gets 0
        score = 10 * (max_cost - estimated_cost) / (max_cost - min_cost)
        return max(0, min(10, score))
    
    def _score_financial_protection(self, plan: Plan) -> float:
        """
        Metric 4: Financial Protection (10% weight)
        - 10 points: Deductible ≤ $500 AND OOPM ≤ $3,000
        - 7 points: Deductible ≤ $1,000 AND OOPM ≤ $5,000
        - 4 points: Deductible ≤ $2,000 AND OOPM ≤ $7,000
        - 0 points: Higher than above thresholds
        """
        # Use the unified deductible and oop_max fields (backwards compatibility handled in Plan.__post_init__)
        deductible = plan.deductible
        oopm = plan.oop_max
        
        if deductible <= 500 and oopm <= 3000:
            return 10.0
        elif deductible <= 1000 and oopm <= 5000:
            return 7.0
        elif deductible <= 2000 and oopm <= 7000:
            return 4.0
        else:
            return 0.0
    
    def _score_administrative_simplicity(self, plan: Plan) -> float:
        """
        Metric 5: Administrative Simplicity (10% weight)
        Start with 10 points, apply penalties:
        - -3 if referrals required
        - -2 if frequent prior auth needed
        - -2 if uses maximizer programs
        - -1 if poor plan rating (<3 stars)
        """
        score = 10.0
        
        if plan.requires_referrals:
            score -= 3
        
        if plan.administrative.prior_auth_common:
            score -= 2
        
        if plan.administrative.uses_maximizer:
            score -= 2
        
        if plan.administrative.plan_rating < 3.0:
            score -= 1
        
        return max(0, score)
    
    def _score_plan_quality(self, plan: Plan) -> float:
        """
        Metric 6: Plan Stability & Quality (5% weight)
        Plan star rating × 2 (max 10 points)
        """
        return min(10.0, plan.administrative.plan_rating * 2)
    
    def _calculate_weighted_score(self, metrics: ScoringMetrics) -> float:
        """Calculate the final weighted score."""
        weighted_score = (
            metrics.provider_network_score * self.WEIGHTS['provider_network'] +
            metrics.medication_coverage_score * self.WEIGHTS['medication_coverage'] +
            metrics.total_cost_score * self.WEIGHTS['total_cost'] +
            metrics.financial_protection_score * self.WEIGHTS['financial_protection'] +
            metrics.administrative_simplicity_score * self.WEIGHTS['administrative_simplicity'] +
            metrics.plan_quality_score * self.WEIGHTS['plan_quality']
        )
        return round(weighted_score, 2)
    
    def _get_provider_coverage_details(self, client: Client, plan: Plan) -> Dict[str, bool]:
        """Get detailed provider coverage information."""
        details = {}
        for provider in client.medical_profile.providers:
            in_network = plan.network.get(provider.name, NetworkStatus.OUT_OF_NETWORK) == NetworkStatus.IN_NETWORK
            details[provider.name] = in_network
        return details
    
    def _get_medication_coverage_details(self, client: Client, plan: Plan) -> Dict[str, str]:
        """Get detailed medication coverage information."""
        details = {}
        for medication in client.medical_profile.medications:
            coverage = plan.formulary.get(medication.name, CoverageStatus.NOT_COVERED)
            details[medication.name] = coverage.value
        return details