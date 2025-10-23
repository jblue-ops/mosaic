"""
Swarm Orchestrator - Coordinates all AI agents

This is the main entry point for candidate evaluation.
It orchestrates the 6 specialized agents and builds consensus.
"""

from typing import Dict, Any, Optional
import time
from datetime import datetime

from app.agents.linkedin_agent import LinkedInAgent
from app.agents.github_agent import GitHubAgent
from app.agents.resume_agent import ResumeAgent
from app.agents.bias_detection_agent import BiasDetectionAgent
from app.agents.predictive_agent import PredictiveAgent
from app.agents.consensus import ConsensusBuilder
from app.agents.base_agent import AgentVote


class SwarmOrchestrator:
    """
    Orchestrates swarm intelligence evaluation

    Workflow:
    1. Instantiate all 6 agents
    2. Run evaluations in parallel (when possible)
    3. Bias detection agent reviews other agents' votes
    4. Consensus builder aggregates all votes
    5. Return comprehensive evaluation result
    """

    def __init__(self):
        # Initialize all agents
        self.linkedin_agent = LinkedInAgent()
        self.github_agent = GitHubAgent()
        self.resume_agent = ResumeAgent()
        self.bias_agent = BiasDetectionAgent()
        self.predictive_agent = PredictiveAgent()

        # Initialize consensus builder
        self.consensus_builder = ConsensusBuilder(mechanism="weighted_average")

    async def evaluate_candidate(
        self,
        candidate_id: int,
        resume_url: Optional[str] = None,
        linkedin_url: Optional[str] = None,
        github_url: Optional[str] = None,
        job_opening_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Run full swarm evaluation on a candidate

        Args:
            candidate_id: ID of candidate to evaluate
            resume_url: URL to resume
            linkedin_url: LinkedIn profile URL
            github_url: GitHub profile URL
            job_opening_id: Job opening being evaluated for

        Returns:
            Complete evaluation with all agent votes and consensus
        """
        start_time = time.time()

        # Step 1: Run initial agents in parallel
        # TODO: Actually run these in parallel using asyncio.gather()
        linkedin_vote = await self.linkedin_agent.evaluate(
            candidate_id, resume_url, linkedin_url, github_url, job_opening_id
        )

        github_vote = await self.github_agent.evaluate(
            candidate_id, resume_url, linkedin_url, github_url, job_opening_id
        )

        resume_vote = await self.resume_agent.evaluate(
            candidate_id, resume_url, linkedin_url, github_url, job_opening_id
        )

        predictive_vote = await self.predictive_agent.evaluate(
            candidate_id, resume_url, linkedin_url, github_url, job_opening_id
        )

        # Step 2: Bias detection agent reviews other agents' votes
        other_votes = {
            "linkedin": linkedin_vote,
            "github": github_vote,
            "resume": resume_vote,
            "predictive": predictive_vote,
        }

        bias_vote = await self.bias_agent.evaluate(
            candidate_id,
            resume_url,
            linkedin_url,
            github_url,
            job_opening_id,
            other_agent_votes=other_votes,
        )

        # Step 3: Build consensus
        all_votes = {
            "linkedin_agent": linkedin_vote,
            "github_agent": github_vote,
            "resume_agent": resume_vote,
            "bias_detection_agent": bias_vote,
            "predictive_agent": predictive_vote,
        }

        consensus = self.consensus_builder.build_consensus(all_votes)

        # Step 4: Compile result
        processing_time_ms = (time.time() - start_time) * 1000

        result = {
            "candidate_id": candidate_id,
            "job_opening_id": job_opening_id,
            "agent_votes": {
                name: {
                    "score": vote.score,
                    "confidence": vote.confidence,
                    "reasoning": vote.reasoning,
                    "metadata": vote.metadata,
                }
                for name, vote in all_votes.items()
            },
            "consensus_details": consensus,
            "overall_confidence": consensus["overall_score"],
            "bias_flags": bias_vote.metadata.get("bias_flags", []),
            "evaluated_at": datetime.utcnow(),
            "processing_time_ms": round(processing_time_ms, 2),
        }

        return result

    def get_agent_status(self) -> list:
        """Get status of all agents"""
        return [
            self.linkedin_agent.get_status(),
            self.github_agent.get_status(),
            self.resume_agent.get_status(),
            self.bias_agent.get_status(),
            self.predictive_agent.get_status(),
        ]

    def get_metrics(self) -> Dict[str, Any]:
        """Get swarm metrics"""
        # TODO: Track actual metrics
        return {
            "total_evaluations": 0,
            "average_confidence": 0.0,
            "bias_flags_detected": 0,
        }
