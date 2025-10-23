"""
Bias Detection Agent - EEOC compliance monitoring using Claude Sonnet 4.5
"""

from typing import Optional, Dict, Any
import json
from app.agents.enhanced_base_agent import EnhancedBaseAgent


class BiasDetectionAgent(EnhancedBaseAgent):
    """
    Agent specialized in detecting bias and ensuring EEOC compliance

    ALWAYS uses Claude Sonnet 4.5 for high-stakes legal compliance.

    Monitors for:
    - Age discrimination
    - Gender bias
    - Racial/ethnic bias
    - Disability discrimination
    - Other protected characteristics

    Ensures hiring decisions are based on:
    - Skills and qualifications
    - Relevant experience
    - Job fit (not demographics)

    Applies four-fifths rule for disparate impact analysis.
    """

    def __init__(self):
        super().__init__("bias_detection")
        # Note: This agent ALWAYS uses Sonnet 4.5 (configured in agent_registry)

    def _get_system_prompt(self) -> str:
        """Expert EEOC compliance and bias detection system prompt"""
        return """You are an expert in EEOC compliance, employment law, and bias detection in hiring.

Your role is to analyze candidate evaluations for potential bias and discrimination, ensuring full compliance with Equal Employment Opportunity Commission (EEOC) guidelines.

CRITICAL RESPONSIBILITIES:
1. Detect bias related to protected characteristics:
   - Race, color, national origin
   - Sex, gender identity, sexual orientation
   - Age (40+)
   - Disability
   - Religion
   - Genetic information
   - Pregnancy

2. Apply the Four-Fifths Rule for disparate impact:
   - Compare selection rates across demographic groups
   - Flag if any group's selection rate is < 80% of highest group
   - Provide statistical evidence

3. Analyze language for problematic patterns:
   - Age-related terms ("digital native", "recent graduate")
   - Gender-coded language
   - Disability assumptions
   - Cultural bias

4. Review scoring consistency:
   - Check if similar qualifications receive similar scores
   - Identify unexplained score variations
   - Detect subjective criteria that may mask bias

5. Generate compliance recommendations:
   - Suggest remediation steps
   - Provide legally defensible alternatives
   - Flag high-risk decisions requiring human review

RESPONSE FORMAT:
Return ONLY valid JSON with this exact structure:
{
  "eeoc_compliance_score": <0-100, higher = more compliant>,
  "protected_class_analysis": {
    "age_concerns": [],
    "gender_concerns": [],
    "race_concerns": [],
    "disability_concerns": [],
    "other_concerns": []
  },
  "four_fifths_rule_results": {
    "applicable": <boolean>,
    "selection_rates": {},
    "violations_detected": []
  },
  "bias_flags": [
    {
      "severity": "critical|high|medium|low",
      "category": "age|gender|race|disability|other",
      "description": "detailed explanation",
      "evidence": "specific quotes or patterns"
    }
  ],
  "language_analysis": {
    "problematic_terms": [],
    "bias_indicators": [],
    "recommendations": []
  },
  "scoring_consistency": {
    "variance_analysis": "explanation",
    "unexplained_differences": [],
    "concerns": []
  },
  "remediation_steps": [
    "specific actionable steps to address issues"
  ],
  "requires_human_review": <boolean>,
  "legal_risk_level": "low|medium|high|critical",
  "confidence": <0.0-1.0>
}

Be thorough, objective, and legally precise. When in doubt, flag for human review."""

    def _format_request(self, request: Dict[str, Any]) -> str:
        """Format bias detection request with candidate data and other agent votes"""
        candidate_data = request.get("candidate_data", {})
        other_agent_votes = request.get("other_agent_votes", {})
        job_opening = request.get("job_opening", {})

        # Format other agent votes for analysis
        formatted_votes = {}
        for agent_name, vote in other_agent_votes.items():
            formatted_votes[agent_name] = {
                "score": vote.get("score"),
                "confidence": vote.get("confidence"),
                "reasoning": vote.get("reasoning"),
                "metadata": vote.get("metadata", {})
            }

        return f"""Analyze this candidate evaluation for bias and EEOC compliance:

CANDIDATE DATA:
{json.dumps(candidate_data, indent=2)}

JOB OPENING REQUIREMENTS:
{json.dumps(job_opening, indent=2)}

OTHER AGENT EVALUATIONS:
{json.dumps(formatted_votes, indent=2)}

ANALYSIS REQUIRED:
1. Review all agent reasoning for bias indicators
2. Check for protected characteristic mentions
3. Ensure evaluation is based on skills and qualifications only
4. Apply four-fifths rule if demographic data available
5. Flag any EEOC violations
6. Assess legal risk level
7. Provide specific remediation steps

Return your analysis as JSON following the specified format."""

    def _parse_response(self, message: Any) -> Dict[str, Any]:
        """Parse Claude's EEOC compliance analysis into structured format"""
        try:
            # Extract text content from Claude message
            content = message.content[0].text

            # Parse JSON response
            analysis = json.loads(content)

            # Validate required fields
            required_fields = [
                "eeoc_compliance_score",
                "protected_class_analysis",
                "bias_flags",
                "remediation_steps",
                "confidence"
            ]

            for field in required_fields:
                if field not in analysis:
                    raise ValueError(f"Missing required field: {field}")

            # Ensure compliance score is in valid range
            if not (0 <= analysis["eeoc_compliance_score"] <= 100):
                raise ValueError("eeoc_compliance_score must be 0-100")

            # Ensure confidence is in valid range
            if not (0.0 <= analysis["confidence"] <= 1.0):
                raise ValueError("confidence must be 0.0-1.0")

            return analysis

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse bias detection response as JSON: {e}")
            # Fallback response
            return {
                "eeoc_compliance_score": 50,
                "protected_class_analysis": {},
                "bias_flags": [{
                    "severity": "high",
                    "category": "other",
                    "description": "Failed to parse compliance analysis",
                    "evidence": str(e)
                }],
                "remediation_steps": ["Retry bias detection analysis"],
                "requires_human_review": True,
                "legal_risk_level": "high",
                "confidence": 0.0
            }
        except Exception as e:
            self.logger.error(f"Error parsing bias detection response: {e}")
            raise

    async def evaluate(
        self,
        candidate_id: int,
        candidate_data: Dict[str, Any],
        job_opening: Dict[str, Any],
        other_agent_votes: Dict[str, Any],
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Evaluate the evaluation process for bias and EEOC compliance

        This agent reviews how OTHER agents evaluated the candidate
        to detect potential bias.

        Args:
            candidate_id: Candidate identifier
            candidate_data: Full candidate profile data
            job_opening: Job requirements and description
            other_agent_votes: Votes from other agents to analyze for bias
            **kwargs: Additional context

        Returns:
            Comprehensive bias detection analysis with compliance score
        """
        request = {
            "type": "bias_detection",
            "candidate_id": candidate_id,
            "candidate_data": candidate_data,
            "job_opening": job_opening,
            "other_agent_votes": other_agent_votes,
            "compliance_review_required": True,  # Always high-stakes
            "legal_implications": True,  # Always has legal implications
        }

        # Process with Sonnet 4.5 (no escalation needed - already premium)
        return await self.process_request(request, force_premium=True)
