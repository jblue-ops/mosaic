"""
Swarm Orchestrator - Coordinates all AI agents

This is the main entry point for candidate evaluation.
It orchestrates the 6 specialized agents and builds consensus.
"""

from typing import Dict, Any, Optional
import time
import asyncio
from datetime import datetime

from app.agents.linkedin_agent import LinkedInSourcingAgent
from app.agents.github_agent import GitHubSourcingAgent
from app.agents.resume_agent import ResumeAnalysisAgent
from app.agents.bias_detection_agent import BiasDetectionAgent
from app.agents.predictive_agent import PredictiveAgent
from app.agents.consensus import ConsensusBuilder


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
        # Fast-tier agents (Haiku 4.5 with escalation to Sonnet 4.5)
        self.linkedin_agent = LinkedInSourcingAgent()
        self.github_agent = GitHubSourcingAgent()
        self.resume_agent = ResumeAnalysisAgent()

        # Premium-tier agents (Sonnet 4.5 only)
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

        # Step 1: Run fast-tier agents in parallel (Haiku 4.5 with auto-escalation)
        fast_agents_tasks = [
            self.linkedin_agent.evaluate(
                candidate_id, resume_url, linkedin_url, github_url, job_opening_id
            ),
            self.github_agent.evaluate(
                candidate_id, resume_url, linkedin_url, github_url, job_opening_id
            ),
            self.resume_agent.evaluate(
                candidate_id, resume_url, linkedin_url, github_url, job_opening_id
            ),
            self.predictive_agent.evaluate(
                candidate_id, resume_url, linkedin_url, github_url, job_opening_id
            ),
        ]

        # Execute fast agents concurrently
        fast_results = await asyncio.gather(*fast_agents_tasks)
        linkedin_vote, github_vote, resume_vote, predictive_vote = fast_results

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

        # Step 4: Track metrics
        processing_time_ms = (time.time() - start_time) * 1000

        # Track total tokens and cost across all agents
        total_input_tokens = 0
        total_output_tokens = 0
        total_cost = 0.0

        # Extract from each agent response
        for vote in [linkedin_vote, github_vote, resume_vote, predictive_vote, bias_vote]:
            if isinstance(vote, dict) and "token_usage" in vote:
                total_input_tokens += vote["token_usage"].get("input", 0)
                total_output_tokens += vote["token_usage"].get("output", 0)
            # Cost is tracked within each agent's metrics

        # Step 5: Compile result

        # Helper function to normalize vote format (all agents now return dicts)
        def normalize_vote(vote):
            return {
                "score": vote.get("score", 0),
                "confidence": vote.get("confidence", 0),
                "reasoning": vote.get("reasoning", ""),
                "metadata": vote.get("metadata", {}),
            }

        result = {
            "candidate_id": candidate_id,
            "job_opening_id": job_opening_id,
            "agent_votes": {
                name: normalize_vote(vote)
                for name, vote in all_votes.items()
            },
            "consensus_details": consensus,
            "overall_confidence": consensus["overall_score"],
            "bias_flags": (
                bias_vote.get("metadata", {}).get("bias_flags", [])
                if isinstance(bias_vote, dict)
                else bias_vote.metadata.get("bias_flags", [])
            ),
            "evaluated_at": datetime.utcnow(),
            "processing_time_ms": round(processing_time_ms, 2),
            "metrics": {
                "total_input_tokens": total_input_tokens,
                "total_output_tokens": total_output_tokens,
                "total_tokens": total_input_tokens + total_output_tokens,
                "processing_time_ms": round(processing_time_ms, 2),
                "agents_executed": 5,
                "agents_parallel": 4,  # 4 fast-tier agents run in parallel
                "escalations": sum(
                    1 for vote in all_votes.values()
                    if isinstance(vote, dict) and vote.get("escalated", False)
                ),
            },
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

    def get_detailed_metrics(self) -> Dict[str, Any]:
        """Get detailed metrics from all agents"""
        return {
            "linkedin": self.linkedin_agent.get_metrics(),
            "github": self.github_agent.get_metrics(),
            "resume": self.resume_agent.get_metrics(),
            "bias_detection": self.bias_agent.get_metrics(),
            "predictive": self.predictive_agent.get_metrics(),
        }
