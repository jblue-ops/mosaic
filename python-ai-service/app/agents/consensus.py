"""
Consensus Mechanism - Aggregates agent votes

This is not an "agent" that evaluates candidates, but rather
orchestrates the voting and consensus-building among the other agents.
"""

from typing import Dict, List, Any
from app.agents.base_agent import AgentVote


class ConsensusBuilder:
    """
    Aggregates votes from multiple agents and reaches consensus

    Voting Mechanisms:
    - Weighted Average: Each agent vote weighted by confidence
    - Majority Voting: Agents vote yes/no, majority wins
    - Unanimous: All agents must agree above threshold
    - Ranked Choice: Agents rank candidates, aggregate rankings
    """

    def __init__(self, mechanism: str = "weighted_average"):
        self.mechanism = mechanism

    def build_consensus(
        self, agent_votes: Dict[str, AgentVote]
    ) -> Dict[str, Any]:
        """
        Aggregate agent votes into consensus decision

        Args:
            agent_votes: Dictionary of agent_name -> AgentVote

        Returns:
            Consensus details with overall score and agreement metrics
        """
        if self.mechanism == "weighted_average":
            return self._weighted_average_consensus(agent_votes)
        elif self.mechanism == "majority":
            return self._majority_consensus(agent_votes)
        else:
            raise ValueError(f"Unknown consensus mechanism: {self.mechanism}")

    def _weighted_average_consensus(
        self, agent_votes: Dict[str, AgentVote]
    ) -> Dict[str, Any]:
        """
        Weighted average: Each vote weighted by agent's confidence

        Formula: overall_score = Σ(score_i * confidence_i) / Σ(confidence_i)
        """
        if not agent_votes:
            return {
                "mechanism": "weighted_average",
                "overall_score": 0.0,
                "agreement_score": 0.0,
                "agents_in_consensus": 0,
                "agents_total": 0,
            }

        weighted_sum = sum(
            vote.score * vote.confidence for vote in agent_votes.values()
        )
        confidence_sum = sum(vote.confidence for vote in agent_votes.values())

        overall_score = weighted_sum / confidence_sum if confidence_sum > 0 else 0.0

        # Calculate agreement: variance in scores
        scores = [vote.score for vote in agent_votes.values()]
        avg_score = sum(scores) / len(scores)
        variance = sum((s - avg_score) ** 2 for s in scores) / len(scores)
        agreement_score = 1.0 - min(variance, 1.0)  # High agreement = low variance

        # Count agents in consensus (within 0.15 of average)
        agents_in_consensus = sum(
            1 for score in scores if abs(score - avg_score) <= 0.15
        )

        return {
            "mechanism": "weighted_average",
            "overall_score": round(overall_score, 4),
            "agreement_score": round(agreement_score, 4),
            "agents_in_consensus": agents_in_consensus,
            "agents_total": len(agent_votes),
            "score_variance": round(variance, 4),
        }

    def _majority_consensus(
        self, agent_votes: Dict[str, AgentVote]
    ) -> Dict[str, Any]:
        """
        Majority voting: Agents vote yes/no (score > 0.7 = yes)

        Returns whether majority voted yes
        """
        threshold = 0.7
        yes_votes = sum(1 for vote in agent_votes.values() if vote.score >= threshold)
        no_votes = len(agent_votes) - yes_votes

        return {
            "mechanism": "majority",
            "overall_score": 1.0 if yes_votes > no_votes else 0.0,
            "yes_votes": yes_votes,
            "no_votes": no_votes,
            "agents_total": len(agent_votes),
            "threshold": threshold,
        }
