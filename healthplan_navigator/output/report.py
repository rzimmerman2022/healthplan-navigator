import csv
import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime
from ..core.models import AnalysisReport, PlanAnalysis


class ReportGenerator:
    """Generates various output formats for healthcare plan analysis."""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_executive_summary(self, report: AnalysisReport) -> str:
        """Generate executive summary in markdown format."""
        client = report.client
        top_plan = report.top_recommendations[0] if report.top_recommendations else None
        
        if not top_plan:
            return "No plan recommendations available."
        
        summary = f"""# Health Insurance Plan Recommendation Report
Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M')}

## Executive Summary
Based on your medical profile and priorities, we recommend the **{top_plan.plan.marketing_name}** plan. 
This plan offers the best balance of provider access, medication coverage, and total cost for your specific needs.

### Client Profile
- **Name**: {client.personal.full_name}
- **Household Size**: {client.personal.household_size}
- **Annual Income**: ${client.personal.annual_income:,.2f}
- **ZIP Code**: {client.personal.zipcode}

### Key Findings
- **Overall Score**: {top_plan.metrics.weighted_total_score:.1f}/10
- **Estimated Annual Cost**: ${top_plan.estimated_annual_cost:,.2f}
- **Monthly Premium**: ${top_plan.plan.monthly_premium:.2f}
- **Deductible**: ${top_plan.plan.deductible_individual:,.2f}
- **Out-of-Pocket Maximum**: ${top_plan.plan.oop_max_individual:,.2f}

### Scoring Breakdown
| Metric | Score | Weight |
|--------|-------|---------|
| Provider Network | {top_plan.metrics.provider_network_score:.1f}/10 | 30% |
| Medication Coverage | {top_plan.metrics.medication_coverage_score:.1f}/10 | 25% |
| Total Cost | {top_plan.metrics.total_cost_score:.1f}/10 | 20% |
| Financial Protection | {top_plan.metrics.financial_protection_score:.1f}/10 | 10% |
| Administrative Simplicity | {top_plan.metrics.administrative_simplicity_score:.1f}/10 | 10% |
| Plan Quality | {top_plan.metrics.plan_quality_score:.1f}/10 | 5% |

### Top 3 Recommendations

"""
        
        for i, rec in enumerate(report.top_recommendations[:3], 1):
            medal = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else f"#{i}"
            summary += f"""
{medal} **{rec.plan.marketing_name}**
- Score: {rec.metrics.weighted_total_score:.1f}/10
- Monthly Premium: ${rec.plan.monthly_premium:.2f}
- Estimated Annual Cost: ${rec.estimated_annual_cost:,.2f}
- Issuer: {rec.plan.issuer}
- Metal Level: {rec.plan.metal_level.value}
"""
        
        # Provider coverage analysis
        if client.medical_profile.providers:
            summary += "\n### Provider Coverage Analysis\n"
            for provider in client.medical_profile.providers:
                in_network = top_plan.provider_coverage_details.get(provider.name, False)
                status = "✅ In-Network" if in_network else "❌ Out-of-Network"
                summary += f"- **{provider.name}** ({provider.specialty}): {status}\n"
        
        # Medication coverage analysis
        if client.medical_profile.medications:
            summary += "\n### Medication Coverage Analysis\n"
            for medication in client.medical_profile.medications:
                coverage = top_plan.medication_coverage_details.get(medication.name, "NOT_COVERED")
                summary += f"- **{medication.name}**: {coverage}\n"
        
        summary += f"\n### Risk Analysis\n"
        summary += f"- **Best Case Scenario**: ${top_plan.plan.monthly_premium * 12:,.2f} (premiums only)\n"
        summary += f"- **Worst Case Scenario**: ${top_plan.plan.oop_max_individual + (top_plan.plan.monthly_premium * 12):,.2f} (max out-of-pocket + premiums)\n"
        summary += f"- **Expected Cost**: ${top_plan.estimated_annual_cost:,.2f}\n"
        summary += "\n*This analysis is based on your current medical needs and utilization patterns. Actual costs may vary.*"
        
        return summary
    
    def generate_scoring_matrix_csv(self, report: AnalysisReport) -> str:
        """Generate detailed scoring matrix as CSV."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"scoring_matrix_{timestamp}.csv"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'Rank', 'Plan Name', 'Plan ID', 'Issuer', 'Metal Level',
                'Monthly Premium', 'Deductible', 'Out-of-Pocket Max',
                'Estimated Annual Cost',
                'Provider Network Score', 'Medication Coverage Score',
                'Total Cost Score', 'Financial Protection Score',
                'Administrative Score', 'Plan Quality Score',
                'OVERALL SCORE'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for rank, analysis in enumerate(report.plan_analyses, 1):
                writer.writerow({
                    'Rank': rank,
                    'Plan Name': analysis.plan.marketing_name,
                    'Plan ID': analysis.plan.plan_id,
                    'Issuer': analysis.plan.issuer,
                    'Metal Level': analysis.plan.metal_level.value,
                    'Monthly Premium': f"${analysis.plan.monthly_premium:.2f}",
                    'Deductible': f"${analysis.plan.deductible_individual:,.2f}",
                    'Out-of-Pocket Max': f"${analysis.plan.oop_max_individual:,.2f}",
                    'Estimated Annual Cost': f"${analysis.estimated_annual_cost:,.2f}",
                    'Provider Network Score': f"{analysis.metrics.provider_network_score:.1f}",
                    'Medication Coverage Score': f"{analysis.metrics.medication_coverage_score:.1f}",
                    'Total Cost Score': f"{analysis.metrics.total_cost_score:.1f}",
                    'Financial Protection Score': f"{analysis.metrics.financial_protection_score:.1f}",
                    'Administrative Score': f"{analysis.metrics.administrative_simplicity_score:.1f}",
                    'Plan Quality Score': f"{analysis.metrics.plan_quality_score:.1f}",
                    'OVERALL SCORE': f"{analysis.metrics.weighted_total_score:.1f}"
                })
        
        return str(filepath)
    
    def generate_json_export(self, report: AnalysisReport) -> str:
        """Generate complete analysis data as JSON."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis_export_{timestamp}.json"
        filepath = self.output_dir / filename
        
        # Convert report to JSON-serializable format
        export_data = {
            'metadata': {
                'generated_at': report.generated_at.isoformat(),
                'total_plans_analyzed': len(report.plan_analyses),
                'client_name': report.client.personal.full_name
            },
            'client_profile': {
                'personal': {
                    'full_name': report.client.personal.full_name,
                    'household_size': report.client.personal.household_size,
                    'annual_income': report.client.personal.annual_income,
                    'zipcode': report.client.personal.zipcode
                },
                'providers': [
                    {
                        'name': p.name,
                        'specialty': p.specialty,
                        'priority': p.priority.value,
                        'visit_frequency': p.visit_frequency
                    } for p in report.client.medical_profile.providers
                ],
                'medications': [
                    {
                        'name': m.name,
                        'dosage': m.dosage,
                        'frequency': m.frequency,
                        'annual_doses': m.annual_doses
                    } for m in report.client.medical_profile.medications
                ]
            },
            'plan_analyses': [
                {
                    'rank': idx + 1,
                    'plan': {
                        'plan_id': analysis.plan.plan_id,
                        'issuer': analysis.plan.issuer,
                        'marketing_name': analysis.plan.marketing_name,
                        'metal_level': analysis.plan.metal_level.value,
                        'monthly_premium': analysis.plan.monthly_premium,
                        'deductible_individual': analysis.plan.deductible_individual,
                        'oop_max_individual': analysis.plan.oop_max_individual
                    },
                    'scores': {
                        'provider_network': analysis.metrics.provider_network_score,
                        'medication_coverage': analysis.metrics.medication_coverage_score,
                        'total_cost': analysis.metrics.total_cost_score,
                        'financial_protection': analysis.metrics.financial_protection_score,
                        'administrative_simplicity': analysis.metrics.administrative_simplicity_score,
                        'plan_quality': analysis.metrics.plan_quality_score,
                        'overall_weighted': analysis.metrics.weighted_total_score
                    },
                    'estimated_annual_cost': analysis.estimated_annual_cost,
                    'provider_coverage': analysis.provider_coverage_details,
                    'medication_coverage': analysis.medication_coverage_details
                } for idx, analysis in enumerate(report.plan_analyses)
            ]
        }
        
        with open(filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump(export_data, jsonfile, indent=2)
        
        return str(filepath)
    
    def generate_html_dashboard(self, report: AnalysisReport) -> str:
        """Generate interactive HTML dashboard."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"dashboard_{timestamp}.html"
        filepath = self.output_dir / filename
        
        # Create JSON data for JavaScript
        chart_data = self._prepare_chart_data(report)
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HealthPlan Navigator - Analysis Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .card {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .metric-card {{ display: inline-block; width: 150px; text-align: center; margin: 10px; padding: 15px; background: #e8f4fd; border-radius: 8px; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #2196F3; }}
        .metric-label {{ font-size: 12px; color: #666; }}
        .recommendation {{ background: #e8f5e8; border-left: 4px solid #4CAF50; padding: 15px; margin: 10px 0; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f2f2f2; }}
        .score-high {{ color: #4CAF50; font-weight: bold; }}
        .score-medium {{ color: #FF9800; font-weight: bold; }}
        .score-low {{ color: #f44336; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏥 HealthPlan Navigator Analysis</h1>
            <p><strong>Client:</strong> {report.client.personal.full_name} | 
               <strong>Generated:</strong> {report.generated_at.strftime('%Y-%m-%d %H:%M')} |
               <strong>Plans Analyzed:</strong> {len(report.plan_analyses)}</p>
        </div>
        
        {self._generate_recommendation_card(report)}
        
        <div class="card">
            <h2>📊 Score Comparison</h2>
            <div id="scoreChart" style="height: 400px;"></div>
        </div>
        
        <div class="card">
            <h2>💰 Cost Analysis</h2>
            <div id="costChart" style="height: 400px;"></div>
        </div>
        
        <div class="card">
            <h2>📋 Detailed Scoring Matrix</h2>
            {self._generate_scoring_table(report)}
        </div>
    </div>
    
    <script>
        {self._generate_javascript_charts(chart_data)}
    </script>
</body>
</html>"""
        
        with open(filepath, 'w', encoding='utf-8') as htmlfile:
            htmlfile.write(html_content)
        
        return str(filepath)
    
    def _generate_recommendation_card(self, report: AnalysisReport) -> str:
        """Generate the top recommendation card."""
        if not report.top_recommendations:
            return "<div class='card'><h2>No recommendations available</h2></div>"
        
        top_plan = report.top_recommendations[0]
        
        return f"""
        <div class="card recommendation">
            <h2>🥇 Top Recommendation: {top_plan.plan.marketing_name}</h2>
            <div class="metric-card">
                <div class="metric-value">{top_plan.metrics.weighted_total_score:.1f}/10</div>
                <div class="metric-label">Overall Score</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${top_plan.plan.monthly_premium:.0f}</div>
                <div class="metric-label">Monthly Premium</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${top_plan.estimated_annual_cost:,.0f}</div>
                <div class="metric-label">Est. Annual Cost</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{top_plan.plan.metal_level.value}</div>
                <div class="metric-label">Metal Level</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{top_plan.plan.issuer}</div>
                <div class="metric-label">Issuer</div>
            </div>
        </div>
        """
    
    def _generate_scoring_table(self, report: AnalysisReport) -> str:
        """Generate HTML table with scoring details."""
        table_html = """
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Plan Name</th>
                    <th>Overall Score</th>
                    <th>Provider Network</th>
                    <th>Medication Coverage</th>
                    <th>Total Cost</th>
                    <th>Financial Protection</th>
                    <th>Administrative</th>
                    <th>Plan Quality</th>
                    <th>Est. Annual Cost</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for rank, analysis in enumerate(report.plan_analyses, 1):
            def score_class(score):
                if score >= 7: return "score-high"
                elif score >= 4: return "score-medium"
                else: return "score-low"
            
            table_html += f"""
                <tr>
                    <td>{rank}</td>
                    <td><strong>{analysis.plan.marketing_name}</strong><br><small>{analysis.plan.issuer}</small></td>
                    <td class="{score_class(analysis.metrics.weighted_total_score)}">{analysis.metrics.weighted_total_score:.1f}/10</td>
                    <td class="{score_class(analysis.metrics.provider_network_score)}">{analysis.metrics.provider_network_score:.1f}/10</td>
                    <td class="{score_class(analysis.metrics.medication_coverage_score)}">{analysis.metrics.medication_coverage_score:.1f}/10</td>
                    <td class="{score_class(analysis.metrics.total_cost_score)}">{analysis.metrics.total_cost_score:.1f}/10</td>
                    <td class="{score_class(analysis.metrics.financial_protection_score)}">{analysis.metrics.financial_protection_score:.1f}/10</td>
                    <td class="{score_class(analysis.metrics.administrative_simplicity_score)}">{analysis.metrics.administrative_simplicity_score:.1f}/10</td>
                    <td class="{score_class(analysis.metrics.plan_quality_score)}">{analysis.metrics.plan_quality_score:.1f}/10</td>
                    <td>${analysis.estimated_annual_cost:,.0f}</td>
                </tr>
            """
        
        table_html += "</tbody></table>"
        return table_html
    
    def _prepare_chart_data(self, report: AnalysisReport) -> Dict:
        """Prepare data for JavaScript charts."""
        plans = [analysis.plan.marketing_name[:20] + "..." if len(analysis.plan.marketing_name) > 20 
                else analysis.plan.marketing_name for analysis in report.plan_analyses[:10]]
        
        return {
            'plans': plans,
            'overall_scores': [analysis.metrics.weighted_total_score for analysis in report.plan_analyses[:10]],
            'provider_scores': [analysis.metrics.provider_network_score for analysis in report.plan_analyses[:10]],
            'medication_scores': [analysis.metrics.medication_coverage_score for analysis in report.plan_analyses[:10]],
            'cost_scores': [analysis.metrics.total_cost_score for analysis in report.plan_analyses[:10]],
            'annual_costs': [analysis.estimated_annual_cost for analysis in report.plan_analyses[:10]],
            'premiums': [analysis.plan.monthly_premium * 12 for analysis in report.plan_analyses[:10]]
        }
    
    def _generate_javascript_charts(self, data: Dict) -> str:
        """Generate JavaScript code for Plotly charts."""
        return f"""
        // Score comparison chart
        var scoreData = [{{
            x: {data['plans']},
            y: {data['overall_scores']},
            type: 'bar',
            name: 'Overall Score',
            marker: {{color: '#2196F3'}}
        }}];
        
        var scoreLayout = {{
            title: 'Plan Scores (0-10 Scale)',
            xaxis: {{title: 'Plans', tickangle: -45}},
            yaxis: {{title: 'Score', range: [0, 10]}},
            margin: {{b: 100}}
        }};
        
        Plotly.newPlot('scoreChart', scoreData, scoreLayout);
        
        // Cost comparison chart
        var costData = [{{
            x: {data['plans']},
            y: {data['annual_costs']},
            type: 'bar',
            name: 'Estimated Annual Cost',
            marker: {{color: '#4CAF50'}}
        }}, {{
            x: {data['plans']},
            y: {data['premiums']},
            type: 'bar',
            name: 'Annual Premiums Only',
            marker: {{color: '#FF9800'}}
        }}];
        
        var costLayout = {{
            title: 'Cost Comparison',
            xaxis: {{title: 'Plans', tickangle: -45}},
            yaxis: {{title: 'Cost ($)'}},
            margin: {{b: 100}},
            barmode: 'group'
        }};
        
        Plotly.newPlot('costChart', costData, costLayout);
        """