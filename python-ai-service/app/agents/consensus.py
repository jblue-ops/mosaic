"""
Consensus Mechanism - Aggregates agent votes using Claude Sonnet 4.5

This orchestrates voting and consensus-building among all agents,
using algorithmic methods for simple cases and Sonnet 4.5 for complex decisions.
"""

from typing import Dict, Any
import json
from app.agents.enhanced_base_agent import EnhancedBaseAgent
from app.core.llm_config import LLMConfig


class ConsensusBuilder(EnhancedBaseAgent):
    """
    Aggregates votes from multiple agents and reaches consensus

    ALWAYS uses Claude Sonnet 4.5 for final hiring recommendations
    and complex disagreement resolution.

    Voting Mechanisms:
    - Weighted Average: Each agent vote weighted by confidence (simple cases)
    - Majority Voting: Agents vote yes/no, majority wins (simple cases)
    - LLM-Powered Consensus: Sonnet 4.5 resolves complex disagreements
    - Trust-Weighted: Higher confidence agents have more influence
    """

    def __init__(self, mechanism: str = "weighted_average"):
        super().__init__("consensus_engine")
        self.mechanism = mechanism
        # Note: This agent ALWAYS uses Sonnet 4.5 (configured in agent_registry)

    def _get_system_prompt(self) -> str:
        """Expert multi-agent consensus and conflict resolution system prompt"""
        return """You are an expert in multi-agent consensus building and decision synthesis.

Your role is to analyze votes from multiple specialized AI agents and synthesize a final, well-reasoned hiring recommendation.

CONSENSUS BUILDING EXPERTISE:
1. Vote Aggregation:
   - Weighted voting by confidence levels
   - Outlier detection and analysis
   - Trust-based weighting
   - Minority opinion consideration

2. Conflict Resolution:
   - Identify root causes of disagreement
   - Assess validity of conflicting perspectives
   - Synthesize balanced recommendations
   - Escalate genuinely ambiguous cases

3. Decision Synthesis:
   - Integrate technical, cultural, and predictive insights
   - Balance bias detection concerns with qualifications
   - Consider market and retention factors
   - Generate actionable recommendations

4. Quality Assurance:
   - Ensure reasoning is sound and defensible
   - Check for logical inconsistencies
   - Validate against EEOC compliance
   - Maintain transparency in decision-making

RESPONSE FORMAT:
Return ONLY valid JSON with this exact structure:
{
  "final_score": <0.0-1.0, consensus hiring score>,
  "recommendation": "strong_hire|hire|maybe|proceed_with_caution|pass",
  "confidence": <0.0-1.0, overall confidence in decision>,
  "vote_analysis": {
    "agreement_level": "unanimous|strong_agreement|moderate_agreement|significant_disagreement|major_conflict",
    "outliers": [{"agent": "name", "reason": "why outlier"}],
    "convergence_score": <0.0-1.0>
  },
  "agent_synthesis": {
    "technical_assessment": "summary of technical votes",
    "cultural_fit": "summary of cultural/LinkedIn analysis",
    "bias_concerns": "summary of bias detection findings",
    "predictive_outlook": "summary of success prediction",
    "key_strengths": [],
    "key_concerns": []
  },
  "decision_rationale": "comprehensive explanation integrating all perspectives",
  "risk_assessment": {
    "overall_risk": "low|medium|high|critical",
    "specific_risks": [],
    "mitigation_strategies": []
  },
  "next_steps": [
    "recommended actions (e.g., 'Schedule technical interview', 'Request additional references')"
  ],
  "requires_human_review": <boolean>,
  "complexity_score": <0.0-1.0, how complex was this consensus>
}

Be thorough, balanced, and decisive. When agents disagree significantly, analyze why and synthesize a nuanced recommendation rather than just averaging scores."""

    def _format_request(self, request: Dict[str, Any]) -> str:
        """Format consensus request with all agent votes"""
        agent_votes = request.get("agent_votes", {})
        candidate_data = request.get("candidate_data", {})
        job_opening = request.get("job_opening", {})

        # Format agent votes for LLM analysis
        formatted_votes = {}
        for agent_name, vote_data in agent_votes.items():
            formatted_votes[agent_name] = {
                "score": vote_data.get("score"),
                "confidence": vote_data.get("confidence"),
                "reasoning": vote_data.get("reasoning"),
                "metadata": vote_data.get("metadata", {})
            }

        return f"""Build consensus from these agent evaluations:

CANDIDATE SUMMARY:
{json.dumps(candidate_data, indent=2)}

JOB REQUIREMENTS:
{json.dumps(job_opening, indent=2)}

AGENT VOTES:
{json.dumps(formatted_votes, indent=2)}

CONSENSUS TASK:
1. Analyze agreement/disagreement patterns
2. Identify outlier votes and assess validity
3. Synthesize technical, cultural, and predictive insights
4. Consider bias detection findings carefully
5. Generate final recommendation with clear rationale
6. Assess decision complexity and risk
7. Flag if human review is warranted

Return your consensus analysis as JSON following the specified format."""

    def _parse_response(self, message: Any) -> Dict[str, Any]:
        """Parse Claude's consensus decision into structured format"""
        try:
            # Extract text content from Claude message
            content = message.content[0].text

            # Parse JSON response
            consensus = json.loads(content)

            # Validate required fields
            required_fields = [
                "final_score",
                "recommendation",
                "confidence",
                "vote_analysis",
                "decision_rationale"
            ]

            for field in required_fields:
                if field not in consensus:
                    raise ValueError(f"Missing required field: {field}")

            # Validate score and confidence ranges
            if not (0.0 <= consensus["final_score"] <= 1.0):
                raise ValueError("final_score must be 0.0-1.0")

            if not (0.0 <= consensus["confidence"] <= 1.0):
                raise ValueError("confidence must be 0.0-1.0")

            # Validate recommendation values
            valid_recommendations = ["strong_hire", "hire", "maybe", "proceed_with_caution", "pass"]
            if consensus["recommendation"] not in valid_recommendations:
                raise ValueError(f"recommendation must be one of {valid_recommendations}")

            return consensus

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse consensus response as JSON: {e}")
            # Fallback response
            return {
                "final_score": 0.5,
                "recommendation": "proceed_with_caution",
                "confidence": 0.0,
                "vote_analysis": {
                    "agreement_level": "major_conflict",
                    "outliers": [],
                    "convergence_score": 0.0
                },
                "agent_synthesis": {},
                "decision_rationale": f"Consensus building failed: {str(e)}",
                "risk_assessment": {
                    "overall_risk": "critical",
                    "specific_risks": ["Failed to build consensus"],
                    "mitigation_strategies": ["Retry consensus or escalate to human review"]
                },
                "next_steps": ["Human review required"],
                "requires_human_review": True,
                "complexity_score": 1.0
            }
        except Exception as e:
            self.logger.error(f"Error parsing consensus response: {e}")
            raise

    def build_consensus(
        self, agent_votes: Dict[str, Any], use_llm: bool = None
    ) -> Dict[str, Any]:
        """
        Aggregate agent votes into consensus decision

        Args:
            agent_votes: Dictionary of agent_name -> vote data
            use_llm: Force LLM-powered consensus (default: auto-detect complexity)

        Returns:
            Consensus details with overall score and agreement metrics
        """
        if not agent_votes:
            return {
                "mechanism": self.mechanism,
                "final_score": 0.0,
                "recommendation": "pass",
                "confidence": 0.0,
                "agents_total": 0,
            }

        # Determine if we should use LLM-powered consensus
        should_use_llm = use_llm if use_llm is not None else self._should_use_llm_consensus(agent_votes)

        if should_use_llm:
            # Use Sonnet 4.5 for complex consensus
            self.logger.info("Using LLM-powered consensus for complex case")
            # This will be called asynchronously from build_consensus_advanced
            return {
                "mechanism": "llm_powered",
                "requires_advanced_consensus": True
            }
        elif self.mechanism == "weighted_average":
            return self._weighted_average_consensus(agent_votes)
        elif self.mechanism == "majority":
            return self._majority_consensus(agent_votes)
        else:
            raise ValueError(f"Unknown consensus mechanism: {self.mechanism}")

    def _should_use_llm_consensus(self, agent_votes: Dict[str, Any]) -> bool:
        """Determine if case is complex enough to require LLM-powered consensus"""
        if len(agent_votes) < 2:
            return False

        # Extract scores
        scores = []
        for vote in agent_votes.values():
            score = vote.get("score", 0.0)
            scores.append(score)

        # Calculate disagreement
        avg_score = sum(scores) / len(scores)
        variance = sum((s - avg_score) ** 2 for s in scores) / len(scores)
        max_deviation = max(abs(s - avg_score) for s in scores)

        # Use LLM if significant disagreement
        disagreement_threshold = LLMConfig.CONSENSUS_DISAGREEMENT_THRESHOLD
        return max_deviation > disagreement_threshold or variance > 0.15

    async def build_consensus_advanced(
        self,
        agent_votes: Dict[str, Any],
        candidate_data: Dict[str, Any],
        job_opening: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use LLM-powered consensus for complex cases

        Args:
            agent_votes: All agent votes
            candidate_data: Candidate profile
            job_opening: Job requirements

        Returns:
            Comprehensive consensus analysis from Sonnet 4.5
        """
        request = {
            "type": "complex_consensus",
            "agent_votes": agent_votes,
            "candidate_data": candidate_data,
            "job_opening": job_opening,
            "decision_type": "final_hiring_recommendation",  # High-stakes
            "agent_consensus_failed": True,  # Triggers premium model
        }

        # Process with Sonnet 4.5 (no escalation needed - already premium)
        return await self.process_request(request, force_premium=True)

    def _weighted_average_consensus(
        self, agent_votes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Weighted average: Each vote weighted by agent's confidence

        Formula: overall_score = Σ(score_i * confidence_i) / Σ(confidence_i)
        """
        if not agent_votes:
            return {
                "mechanism": "weighted_average",
                "final_score": 0.0,
                "recommendation": "pass",
                "confidence": 0.0,
                "agents_in_consensus": 0,
                "agents_total": 0,
            }

        # Extract scores and confidences
        weighted_sum = 0.0
        confidence_sum = 0.0
        scores = []

        for vote in agent_votes.values():
            score = vote.get("score", 0.0)
            confidence = vote.get("confidence", 1.0)
            scores.append(score)
            weighted_sum += score * confidence
            confidence_sum += confidence

        overall_score = weighted_sum / confidence_sum if confidence_sum > 0 else 0.0

        # Calculate agreement: variance in scores
        avg_score = sum(scores) / len(scores)
        variance = sum((s - avg_score) ** 2 for s in scores) / len(scores)
        agreement_score = 1.0 - min(variance, 1.0)  # High agreement = low variance

        # Count agents in consensus (within 0.15 of average)
        agents_in_consensus = sum(
            1 for score in scores if abs(score - avg_score) <= 0.15
        )

        # Determine recommendation
        if overall_score >= 0.85:
            recommendation = "strong_hire"
        elif overall_score >= 0.7:
            recommendation = "hire"
        elif overall_score >= 0.55:
            recommendation = "maybe"
        elif overall_score >= 0.4:
            recommendation = "proceed_with_caution"
        else:
            recommendation = "pass"

        return {
            "mechanism": "weighted_average",
            "final_score": round(overall_score, 4),
            "recommendation": recommendation,
            "confidence": round(agreement_score, 4),
            "agreement_score": round(agreement_score, 4),
            "agents_in_consensus": agents_in_consensus,
            "agents_total": len(agent_votes),
            "score_variance": round(variance, 4),
        }

    def _majority_consensus(
        self, agent_votes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Majority voting: Agents vote yes/no (score > 0.7 = yes)

        Returns whether majority voted yes
        """
        threshold = 0.7
        yes_votes = 0

        for vote in agent_votes.values():
            score = vote.get("score", 0.0)
            if score >= threshold:
                yes_votes += 1

        no_votes = len(agent_votes) - yes_votes
        overall_score = 1.0 if yes_votes > no_votes else 0.0
        recommendation = "hire" if yes_votes > no_votes else "pass"

        return {
            "mechanism": "majority",
            "final_score": overall_score,
            "recommendation": recommendation,
            "confidence": abs(yes_votes - no_votes) / len(agent_votes),
            "yes_votes": yes_votes,
            "no_votes": no_votes,
            "agents_total": len(agent_votes),
            "threshold": threshold,
        }
