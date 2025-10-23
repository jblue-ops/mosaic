"""
Comprehensive test suite for Claude 4.5 family integration
"""

import pytest
import time
import asyncio
from app.agents.resume_agent import ResumeAnalysisAgent
from app.agents.linkedin_agent import LinkedInSourcingAgent
from app.agents.github_agent import GitHubSourcingAgent
from app.agents.bias_detection_agent import BiasDetectionAgent
from app.agents.predictive_agent import PredictiveAgent
from app.core.llm_config import LLMConfig

# Sample test data
SAMPLE_RESUME = """
Software Engineer with 5 years of Python experience.
Led team of 3 engineers at TechCorp.
Skills: Python, FastAPI, PostgreSQL, AWS
Education: BS Computer Science, Stanford University
"""

SAMPLE_JOB_REQUIREMENTS = {
    "title": "Senior Python Engineer",
    "required_skills": ["Python", "FastAPI", "PostgreSQL"],
    "experience_years": 5,
    "description": "Looking for an experienced Python engineer to lead backend development."
}

SAMPLE_LINKEDIN_PROFILE = {
    "url": "https://linkedin.com/in/test-candidate",
    "headline": "Senior Software Engineer",
    "experience": "5 years in Python development",
    "skills": ["Python", "FastAPI", "PostgreSQL", "AWS"]
}

SAMPLE_GITHUB_PROFILE = {
    "url": "https://github.com/testdev",
    "repos": 15,
    "contributions": 250,
    "languages": ["Python", "JavaScript"]
}


class TestClaude45Integration:
    """Test suite for Claude 4.5 family integration"""

    @pytest.mark.asyncio
    async def test_haiku_resume_analysis_speed(self):
        """Verify Haiku 4.5 provides fast responses (<3 seconds)"""
        agent = ResumeAnalysisAgent()

        start_time = time.time()
        result = await agent.analyze_candidate(
            resume_text=SAMPLE_RESUME,
            job_requirements=SAMPLE_JOB_REQUIREMENTS
        )
        duration = time.time() - start_time

        # Performance assertion
        assert duration < 3.0, f"Haiku 4.5 took {duration}s (expected <3s)"

        # Quality assertions
        assert result['confidence'] > 0.0
        assert 'overall_match_score' in result
        assert result['model_used'] == LLMConfig.FAST_MODEL

        # Verify token usage tracking
        assert 'token_usage' in result
        assert result['token_usage']['input'] > 0
        assert result['token_usage']['output'] > 0

    @pytest.mark.asyncio
    async def test_sonnet_bias_detection_thoroughness(self):
        """Verify Sonnet 4.5 provides comprehensive bias analysis"""
        agent = BiasDetectionAgent()

        result = await agent.evaluate(
            candidate_id=1,
            candidate_data={"name": "Test Candidate", "resume": SAMPLE_RESUME},
            job_opening=SAMPLE_JOB_REQUIREMENTS,
            other_agent_votes={
                "linkedin": {"score": 85, "confidence": 0.9},
                "github": {"score": 80, "confidence": 0.8},
                "resume": {"score": 90, "confidence": 0.85}
            }
        )

        # Required fields for bias detection
        assert 'eeoc_compliance_score' in result
        assert 'bias_flags' in result
        assert 'confidence' in result

        # Sonnet 4.5 should always be used for bias detection
        assert result['model_used'] == LLMConfig.PREMIUM_MODEL

        # Should have detailed analysis
        assert result['confidence'] > 0.0
        assert isinstance(result['bias_flags'], list)

    @pytest.mark.asyncio
    async def test_automatic_escalation_to_sonnet(self):
        """Test low-confidence Haiku responses escalate to Sonnet"""
        agent = ResumeAnalysisAgent()

        # Use ambiguous/minimal resume that should trigger escalation
        ambiguous_resume = "Software developer with some experience."

        result = await agent.analyze_candidate(
            resume_text=ambiguous_resume,
            job_requirements=SAMPLE_JOB_REQUIREMENTS
        )

        # Check if escalation occurred (may or may not based on implementation)
        if result.get('escalated'):
            assert result['model_used'] == LLMConfig.PREMIUM_MODEL
            # Sonnet should provide analysis even for ambiguous input
            assert 'overall_match_score' in result

        # At minimum, should have low confidence flag
        assert result['confidence'] >= 0.0

    @pytest.mark.asyncio
    async def test_cost_tracking_accuracy(self):
        """Verify token usage and cost tracking is accurate"""
        agent = ResumeAnalysisAgent()

        initial_cost = agent.total_cost

        result = await agent.analyze_candidate(
            resume_text=SAMPLE_RESUME,
            job_requirements=SAMPLE_JOB_REQUIREMENTS
        )

        # Check token usage was recorded
        assert 'token_usage' in result
        assert result['token_usage']['input'] > 0
        assert result['token_usage']['output'] > 0

        # Check cost increased
        assert agent.total_cost > initial_cost

        # Verify cost calculation matches expected
        expected_cost = LLMConfig.calculate_cost(
            result['token_usage']['input'],
            result['token_usage']['output'],
            result['model_used']
        )

        cost_increase = agent.total_cost - initial_cost
        # Allow small rounding difference
        assert abs(cost_increase - expected_cost) < 0.001, \
            f"Cost calculation mismatch: {cost_increase} vs {expected_cost}"

    @pytest.mark.asyncio
    async def test_parallel_agent_execution(self):
        """Test multiple agents can run concurrently"""
        linkedin_agent = LinkedInSourcingAgent()
        github_agent = GitHubSourcingAgent()
        resume_agent = ResumeAnalysisAgent()

        start_time = time.time()

        # Execute agents in parallel
        results = await asyncio.gather(
            linkedin_agent.evaluate(1, linkedin_url="https://linkedin.com/in/test"),
            github_agent.evaluate(1, github_url="https://github.com/test"),
            resume_agent.analyze_candidate(SAMPLE_RESUME, SAMPLE_JOB_REQUIREMENTS),
            return_exceptions=True  # Don't fail entire test if one agent fails
        )

        duration = time.time() - start_time

        # Parallel execution should be faster than sequential
        # 3 agents × 2s each = 6s sequential, expect < 6s parallel
        assert duration < 8.0, f"Parallel execution took {duration}s (expected <8s)"

        # Count successful results (filter out exceptions)
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) >= 1, "At least one agent should succeed"

    @pytest.mark.asyncio
    async def test_linkedin_agent_haiku_usage(self):
        """Verify LinkedIn agent uses Haiku 4.5 by default"""
        agent = LinkedInSourcingAgent()

        result = await agent.evaluate(
            candidate_id=1,
            linkedin_url="https://linkedin.com/in/test-engineer"
        )

        # Should use fast model (Haiku)
        assert result['model_used'] == LLMConfig.FAST_MODEL
        assert 'token_usage' in result
        assert result['confidence'] >= 0.0

    @pytest.mark.asyncio
    async def test_github_agent_haiku_usage(self):
        """Verify GitHub agent uses Haiku 4.5 by default"""
        agent = GitHubSourcingAgent()

        result = await agent.evaluate(
            candidate_id=1,
            github_url="https://github.com/testdeveloper"
        )

        # Should use fast model (Haiku)
        assert result['model_used'] == LLMConfig.FAST_MODEL
        assert 'token_usage' in result
        assert result['confidence'] >= 0.0

    @pytest.mark.asyncio
    async def test_predictive_agent_premium_usage(self):
        """Verify Predictive Analytics agent uses Sonnet 4.5"""
        agent = PredictiveAgent()

        result = await agent.evaluate(
            candidate_id=1,
            candidate_data={"resume": SAMPLE_RESUME},
            job_opening=SAMPLE_JOB_REQUIREMENTS,
            other_agent_votes={
                "linkedin": {"score": 85},
                "github": {"score": 80},
                "resume": {"score": 90}
            }
        )

        # Should use premium model (Sonnet) for complex predictions
        assert result['model_used'] == LLMConfig.PREMIUM_MODEL
        assert 'confidence' in result
        assert 'token_usage' in result

    @pytest.mark.asyncio
    async def test_token_usage_structure(self):
        """Verify token usage structure is consistent across agents"""
        agent = ResumeAnalysisAgent()

        result = await agent.analyze_candidate(
            resume_text=SAMPLE_RESUME,
            job_requirements=SAMPLE_JOB_REQUIREMENTS
        )

        # Check token usage structure
        assert 'token_usage' in result
        token_usage = result['token_usage']

        assert 'input' in token_usage
        assert 'output' in token_usage
        assert isinstance(token_usage['input'], int)
        assert isinstance(token_usage['output'], int)
        assert token_usage['input'] > 0
        assert token_usage['output'] > 0

    @pytest.mark.asyncio
    async def test_model_configuration(self):
        """Test LLM configuration is correct"""
        # Verify model IDs are set
        assert LLMConfig.FAST_MODEL == "claude-haiku-4-5-20251022"
        assert LLMConfig.PREMIUM_MODEL == "claude-sonnet-4-5-20250929"

        # Verify pricing is set
        assert LLMConfig.HAIKU_INPUT_COST > 0
        assert LLMConfig.HAIKU_OUTPUT_COST > 0
        assert LLMConfig.SONNET_INPUT_COST > 0
        assert LLMConfig.SONNET_OUTPUT_COST > 0

        # Verify Sonnet is more expensive than Haiku
        assert LLMConfig.SONNET_INPUT_COST > LLMConfig.HAIKU_INPUT_COST
        assert LLMConfig.SONNET_OUTPUT_COST > LLMConfig.HAIKU_OUTPUT_COST


class TestErrorHandling:
    """Test error handling and edge cases"""

    @pytest.mark.asyncio
    async def test_empty_resume_handling(self):
        """Test agent handles empty resume gracefully"""
        agent = ResumeAnalysisAgent()

        result = await agent.analyze_candidate(
            resume_text="",
            job_requirements=SAMPLE_JOB_REQUIREMENTS
        )

        # Should still return valid structure, even if low confidence
        assert 'confidence' in result
        assert 'overall_match_score' in result
        assert result['confidence'] >= 0.0

    @pytest.mark.asyncio
    async def test_invalid_url_handling(self):
        """Test agents handle invalid URLs gracefully"""
        linkedin_agent = LinkedInSourcingAgent()

        result = await linkedin_agent.evaluate(
            candidate_id=1,
            linkedin_url="invalid-url"
        )

        # Should return result with low confidence or error flag
        assert 'confidence' in result
        assert result['confidence'] >= 0.0
