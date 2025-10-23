"""
Predictive Agent - Forecasts hiring success using Claude Sonnet 4.5
"""

from typing import Optional, Dict, Any
import json
from app.agents.enhanced_base_agent import EnhancedBaseAgent


class PredictiveAgent(EnhancedBaseAgent):
    """
    Agent specialized in predicting candidate success and retention

    ALWAYS uses Claude Sonnet 4.5 for high-stakes business decisions.

    Analyzes:
    - Historical hiring data patterns
    - Success indicators from similar candidates
    - Retention probability and tenure forecasting
    - Performance trajectory predictions
    - Cultural and team fit indicators
    - Market intelligence and industry trends
    - Risk factors and red flags
    """

    def __init__(self):
        super().__init__("predictive_analytics")
        # Note: This agent ALWAYS uses Sonnet 4.5 (configured in agent_registry)

    def _get_system_prompt(self) -> str:
        """Expert hiring success forecasting system prompt"""
        return """You are an expert in predictive analytics for hiring success, with deep knowledge of:
- Workforce analytics and retention patterns
- Performance indicators and success metrics
- Industry trends and market intelligence
- Risk assessment and mitigation
- Statistical modeling and forecasting

Your role is to predict the likelihood of a candidate's success, retention, and performance in a given role.

ANALYSIS FRAMEWORK:
1. Historical Pattern Recognition:
   - Identify similar successful/unsuccessful hires
   - Analyze career trajectory patterns
   - Compare tenure and performance metrics
   - Extract predictive signals from past data

2. Success Indicators:
   - Technical skill proficiency and growth
   - Leadership and collaboration signals
   - Learning agility and adaptability
   - Domain expertise relevance
   - Cultural alignment markers

3. Retention Forecasting:
   - Career stage and growth trajectory
   - Compensation competitiveness
   - Geographic and remote work fit
   - Industry mobility patterns
   - Stability indicators

4. Performance Prediction:
   - Ramp-up time estimation
   - Peak performance timeline
   - Skill development trajectory
   - Impact potential assessment
   - Contribution forecast

5. Risk Assessment:
   - Job-hopping patterns
   - Skill gaps and learning curves
   - Cultural misalignment risks
   - Compensation expectations
   - Market competition for talent

RESPONSE FORMAT:
Return ONLY valid JSON with this exact structure:
{
  "success_probability": <0.0-1.0, overall likelihood of success>,
  "retention_forecast": {
    "expected_tenure_months": <number>,
    "retention_probability_1yr": <0.0-1.0>,
    "retention_probability_2yr": <0.0-1.0>,
    "retention_probability_3yr": <0.0-1.0>
  },
  "performance_indicators": {
    "ramp_up_time_months": <number>,
    "time_to_peak_performance_months": <number>,
    "expected_performance_level": "below_average|average|above_average|exceptional",
    "impact_potential": "low|medium|high|transformative"
  },
  "success_factors": [
    {
      "factor": "specific success indicator",
      "strength": "low|medium|high",
      "evidence": "supporting data or pattern",
      "weight": <0.0-1.0>
    }
  ],
  "risk_factors": [
    {
      "risk": "specific concern",
      "severity": "low|medium|high|critical",
      "evidence": "supporting data",
      "mitigation": "suggested approach"
    }
  ],
  "comparable_candidates": {
    "similar_hires_analyzed": <number>,
    "success_rate": <0.0-1.0>,
    "average_tenure_months": <number>,
    "performance_distribution": {}
  },
  "market_intelligence": {
    "demand_for_skills": "low|medium|high",
    "compensation_competitiveness": "below_market|at_market|above_market",
    "retention_difficulty": "easy|moderate|challenging"
  },
  "recommendation": "strong_hire|hire|proceed_with_caution|pass",
  "confidence": <0.0-1.0>,
  "reasoning": "comprehensive explanation of prediction"
}

Be data-driven, objective, and thorough. Consider both quantitative signals and qualitative patterns."""

    def _format_request(self, request: Dict[str, Any]) -> str:
        """Format predictive analytics request with candidate background and context"""
        candidate_data = request.get("candidate_data", {})
        job_opening = request.get("job_opening", {})
        historical_data = request.get("historical_data", {})

        return f"""Predict hiring success for this candidate:

CANDIDATE PROFILE:
{json.dumps(candidate_data, indent=2)}

ROLE REQUIREMENTS:
{json.dumps(job_opening, indent=2)}

HISTORICAL CONTEXT:
{json.dumps(historical_data, indent=2)}

ANALYSIS REQUIRED:
1. Assess overall success probability
2. Forecast retention and tenure
3. Predict performance trajectory
4. Identify success factors and strengths
5. Flag risk factors and concerns
6. Compare to similar successful/unsuccessful hires
7. Incorporate market intelligence
8. Provide data-driven recommendation

Return your analysis as JSON following the specified format."""

    def _parse_response(self, message: Any) -> Dict[str, Any]:
        """Parse Claude's predictive analysis into structured format"""
        try:
            # Extract text content from Claude message
            content = message.content[0].text

            # Parse JSON response
            analysis = json.loads(content)

            # Validate required fields
            required_fields = [
                "success_probability",
                "retention_forecast",
                "performance_indicators",
                "success_factors",
                "risk_factors",
                "recommendation",
                "confidence"
            ]

            for field in required_fields:
                if field not in analysis:
                    raise ValueError(f"Missing required field: {field}")

            # Validate probability ranges
            if not (0.0 <= analysis["success_probability"] <= 1.0):
                raise ValueError("success_probability must be 0.0-1.0")

            if not (0.0 <= analysis["confidence"] <= 1.0):
                raise ValueError("confidence must be 0.0-1.0")

            # Validate recommendation values
            valid_recommendations = ["strong_hire", "hire", "proceed_with_caution", "pass"]
            if analysis["recommendation"] not in valid_recommendations:
                raise ValueError(f"recommendation must be one of {valid_recommendations}")

            return analysis

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse predictive analysis response as JSON: {e}")
            # Fallback response
            return {
                "success_probability": 0.5,
                "retention_forecast": {
                    "expected_tenure_months": 0,
                    "retention_probability_1yr": 0.5,
                    "retention_probability_2yr": 0.5,
                    "retention_probability_3yr": 0.5
                },
                "performance_indicators": {
                    "ramp_up_time_months": 0,
                    "time_to_peak_performance_months": 0,
                    "expected_performance_level": "average",
                    "impact_potential": "medium"
                },
                "success_factors": [],
                "risk_factors": [{
                    "risk": "Failed to generate predictive analysis",
                    "severity": "high",
                    "evidence": str(e),
                    "mitigation": "Retry analysis or use manual assessment"
                }],
                "comparable_candidates": {},
                "market_intelligence": {},
                "recommendation": "proceed_with_caution",
                "confidence": 0.0,
                "reasoning": "Analysis failed - fallback response"
            }
        except Exception as e:
            self.logger.error(f"Error parsing predictive analysis response: {e}")
            raise

    async def evaluate(
        self,
        candidate_id: int,
        candidate_data: Dict[str, Any],
        job_opening: Dict[str, Any],
        historical_data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Predict candidate success probability and performance trajectory

        Args:
            candidate_id: Candidate identifier
            candidate_data: Full candidate profile including background and skills
            job_opening: Role requirements and description
            historical_data: Optional historical hiring data for pattern matching
            **kwargs: Additional context

        Returns:
            Comprehensive predictive analysis with success probability and forecasts
        """
        request = {
            "type": "predictive_analytics",
            "candidate_id": candidate_id,
            "candidate_data": candidate_data,
            "job_opening": job_opening,
            "historical_data": historical_data or {},
            "decision_type": "hiring_decision",  # High-stakes business decision
        }

        # Process with Sonnet 4.5 (no escalation needed - already premium)
        return await self.process_request(request, force_premium=True)
