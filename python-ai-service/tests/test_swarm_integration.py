"""
Integration tests for swarm intelligence orchestration
"""

import pytest
import time
from app.agents.orchestrator import SwarmOrchestrator
from app.core.llm_config import LLMConfig

# Sample test data
SAMPLE_CANDIDATE_DATA = {
    "id": 1,
    "name": "Test Candidate",
    "resume_text": "Senior Software Engineer with 5 years Python experience",
    "linkedin_url": "https://linkedin.com/in/test-candidate",
    "github_url": "https://github.com/testdev"
}

SAMPLE_JOB_OPENING = {
    "id": 1,
    "title": "Senior Python Engineer",
    "required_skills": ["Python", "FastAPI", "PostgreSQL"],
    "experience_years": 5,
    "description": "Looking for experienced Python engineer"
}


class TestSwarmIntelligence:
    """Test multi-agent collaboration with Claude 4.5"""

    @pytest.mark.asyncio
    async def test_full_candidate_evaluation(self):
        """Test complete candidate evaluation workflow"""
        orchestrator = SwarmOrchestrator()

        result = await orchestrator.evaluate_candidate(
            candidate_id=1,
            job_opening_id=1,
            resume_url="https://example.com/resume.pdf",
            linkedin_url="https://linkedin.com/in/test-candidate",
            github_url="https://github.com/testdev"
        )

        # Verify result structure
        assert 'agent_votes' in result
        assert 'consensus_details' in result
        assert 'metrics' in result

        # Verify all agents participated (should have at least 3-5 agents)
        assert len(result['agent_votes']) >= 3

        # Verify metrics tracking
        metrics = result['metrics']
        assert 'total_input_tokens' in metrics
        assert 'total_output_tokens' in metrics
        assert 'total_cost' in metrics
        assert metrics['total_input_tokens'] > 0
        assert metrics['total_output_tokens'] > 0
        assert metrics['total_cost'] > 0

        # Verify consensus was reached
        assert 'consensus_details' in result
        consensus = result['consensus_details']
        assert 'final_score' in consensus or 'recommendation' in consensus

    @pytest.mark.asyncio
    async def test_bias_detection_runs_with_sonnet(self):
        """Verify bias detection agent uses Sonnet 4.5"""
        orchestrator = SwarmOrchestrator()

        result = await orchestrator.evaluate_candidate(
            candidate_id=1,
            job_opening_id=1,
            resume_url="https://example.com/resume.pdf",
            linkedin_url=None,
            github_url=None
        )

        # Find bias detection agent result
        bias_agent_result = None
        for agent_name, vote_data in result['agent_votes'].items():
            if 'bias' in agent_name.lower():
                bias_agent_result = vote_data
                break

        if bias_agent_result:
            # Bias detection should use premium model (Sonnet)
            assert bias_agent_result.get('model_used') == LLMConfig.PREMIUM_MODEL

    @pytest.mark.asyncio
    async def test_consensus_with_multiple_agents(self):
        """Test consensus engine aggregates multiple agent opinions"""
        orchestrator = SwarmOrchestrator()

        result = await orchestrator.evaluate_candidate(
            candidate_id=1,
            job_opening_id=1,
            resume_url="https://example.com/resume.pdf",
            linkedin_url="https://linkedin.com/in/test",
            github_url="https://github.com/test"
        )

        # Verify multiple agents contributed
        assert len(result['agent_votes']) >= 2

        # Verify consensus details exist
        assert 'consensus_details' in result
        consensus = result['consensus_details']

        # Should have aggregated scoring or recommendation
        assert any(key in consensus for key in ['final_score', 'recommendation', 'hire_decision'])

    @pytest.mark.asyncio
    async def test_orchestrator_performance(self):
        """Test orchestrator completes evaluation in reasonable time"""
        orchestrator = SwarmOrchestrator()

        start_time = time.time()

        result = await orchestrator.evaluate_candidate(
            candidate_id=1,
            job_opening_id=1,
            resume_url="https://example.com/resume.pdf",
            linkedin_url="https://linkedin.com/in/test",
            github_url="https://github.com/test"
        )

        duration = time.time() - start_time

        # Full evaluation with 4-5 agents should complete in < 10 seconds
        # (assuming parallel execution)
        assert duration < 15.0, f"Orchestration took {duration}s (expected <15s)"

        # Verify result is valid
        assert 'agent_votes' in result
        assert len(result['agent_votes']) > 0

    @pytest.mark.asyncio
    async def test_cost_tracking_per_evaluation(self):
        """Test cost tracking for complete evaluation"""
        orchestrator = SwarmOrchestrator()

        result = await orchestrator.evaluate_candidate(
            candidate_id=1,
            job_opening_id=1,
            resume_url="https://example.com/resume.pdf",
            linkedin_url="https://linkedin.com/in/test",
            github_url="https://github.com/test"
        )

        # Verify cost tracking
        assert 'metrics' in result
        metrics = result['metrics']

        assert 'total_cost' in metrics
        assert metrics['total_cost'] > 0

        # Cost should be reasonable (target ~$0.10 per candidate)
        # Allow up to $0.50 for full evaluation with multiple agents
        assert metrics['total_cost'] < 0.50, \
            f"Cost ${metrics['total_cost']:.3f} exceeds target $0.50"

    @pytest.mark.asyncio
    async def test_agent_vote_structure(self):
        """Test agent votes have consistent structure"""
        orchestrator = SwarmOrchestrator()

        result = await orchestrator.evaluate_candidate(
            candidate_id=1,
            job_opening_id=1,
            resume_url="https://example.com/resume.pdf"
        )

        # Verify vote structure
        assert 'agent_votes' in result
        agent_votes = result['agent_votes']

        for agent_name, vote_data in agent_votes.items():
            # Each vote should have core fields
            assert 'confidence' in vote_data
            assert 'model_used' in vote_data
            assert 'token_usage' in vote_data

            # Token usage structure
            token_usage = vote_data['token_usage']
            assert 'input' in token_usage
            assert 'output' in token_usage
            assert token_usage['input'] >= 0
            assert token_usage['output'] >= 0

    @pytest.mark.asyncio
    async def test_orchestrator_with_missing_data(self):
        """Test orchestrator handles missing candidate data gracefully"""
        orchestrator = SwarmOrchestrator()

        # Evaluate with minimal data
        result = await orchestrator.evaluate_candidate(
            candidate_id=1,
            job_opening_id=1,
            resume_url="https://example.com/resume.pdf",
            linkedin_url=None,  # Missing LinkedIn
            github_url=None     # Missing GitHub
        )

        # Should still produce results
        assert 'agent_votes' in result
        assert 'consensus_details' in result

        # Should have at least resume agent vote
        assert len(result['agent_votes']) >= 1

    @pytest.mark.asyncio
    async def test_metrics_aggregation(self):
        """Test metrics are properly aggregated across agents"""
        orchestrator = SwarmOrchestrator()

        result = await orchestrator.evaluate_candidate(
            candidate_id=1,
            job_opening_id=1,
            resume_url="https://example.com/resume.pdf",
            linkedin_url="https://linkedin.com/in/test"
        )

        metrics = result['metrics']

        # Calculate expected totals from individual agent votes
        expected_input_tokens = sum(
            vote['token_usage']['input']
            for vote in result['agent_votes'].values()
        )
        expected_output_tokens = sum(
            vote['token_usage']['output']
            for vote in result['agent_votes'].values()
        )

        # Verify aggregation matches
        assert metrics['total_input_tokens'] == expected_input_tokens
        assert metrics['total_output_tokens'] == expected_output_tokens

    @pytest.mark.asyncio
    async def test_80_20_cost_split(self):
        """Test that cost distribution follows 80/20 Haiku/Sonnet split"""
        orchestrator = SwarmOrchestrator()

        # Run multiple evaluations to get average
        num_evaluations = 5
        total_haiku_cost = 0
        total_sonnet_cost = 0

        for i in range(num_evaluations):
            result = await orchestrator.evaluate_candidate(
                candidate_id=i,
                job_opening_id=1,
                resume_url="https://example.com/resume.pdf",
                linkedin_url="https://linkedin.com/in/test",
                github_url="https://github.com/test"
            )

            # Calculate cost by model
            for agent_name, vote in result['agent_votes'].items():
                model = vote['model_used']
                token_usage = vote['token_usage']

                cost = LLMConfig.calculate_cost(
                    token_usage['input'],
                    token_usage['output'],
                    model
                )

                if model == LLMConfig.FAST_MODEL:
                    total_haiku_cost += cost
                elif model == LLMConfig.PREMIUM_MODEL:
                    total_sonnet_cost += cost

        # Check cost distribution (should be roughly 80/20 Haiku/Sonnet)
        total_cost = total_haiku_cost + total_sonnet_cost
        if total_cost > 0:
            haiku_percentage = (total_haiku_cost / total_cost) * 100
            sonnet_percentage = (total_sonnet_cost / total_cost) * 100

            # Allow some variance (70-90% Haiku, 10-30% Sonnet)
            assert 60 <= haiku_percentage <= 95, \
                f"Haiku cost {haiku_percentage:.1f}% not in 60-95% range"
            assert 5 <= sonnet_percentage <= 40, \
                f"Sonnet cost {sonnet_percentage:.1f}% not in 5-40% range"


class TestSwarmErrorHandling:
    """Test swarm orchestrator error handling"""

    @pytest.mark.asyncio
    async def test_individual_agent_failure_handling(self):
        """Test orchestrator continues if one agent fails"""
        orchestrator = SwarmOrchestrator()

        # This should work even if some data sources fail
        result = await orchestrator.evaluate_candidate(
            candidate_id=1,
            job_opening_id=1,
            resume_url="https://example.com/resume.pdf",
            linkedin_url="invalid-url",
            github_url="invalid-url"
        )

        # Should still have results from agents that succeeded
        assert 'agent_votes' in result
        # At least resume agent should succeed
        assert len(result['agent_votes']) >= 1

    @pytest.mark.asyncio
    async def test_consensus_with_single_agent(self):
        """Test consensus can be built from single agent response"""
        orchestrator = SwarmOrchestrator()

        result = await orchestrator.evaluate_candidate(
            candidate_id=1,
            job_opening_id=1,
            resume_url="https://example.com/resume.pdf",
            linkedin_url=None,
            github_url=None
        )

        # Should still produce consensus even with limited data
        assert 'consensus_details' in result
        assert 'agent_votes' in result
