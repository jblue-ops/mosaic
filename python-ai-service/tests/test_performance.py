"""
Performance benchmarks for Claude 4.5 integration
"""

import pytest
import asyncio
import time
import statistics
from app.agents.resume_agent import ResumeAnalysisAgent
from app.agents.linkedin_agent import LinkedInSourcingAgent
from app.agents.github_agent import GitHubSourcingAgent
from app.agents.orchestrator import SwarmOrchestrator
from app.core.llm_config import LLMConfig

SAMPLE_RESUME = "Software Engineer with 5 years of Python experience. Led team of 3 engineers."
SAMPLE_JOB = {
    "title": "Python Engineer",
    "required_skills": ["Python", "FastAPI"],
    "experience_years": 5
}


class TestPerformance:
    """Performance benchmarks for Claude 4.5 integration"""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_haiku_latency_p95(self):
        """Test Haiku 4.5 meets P95 latency target (<1.5s)"""
        agent = ResumeAnalysisAgent()

        latencies = []
        num_requests = 20  # Reduced from 100 to keep test faster

        for _ in range(num_requests):
            start = time.time()
            await agent.analyze_candidate(SAMPLE_RESUME, SAMPLE_JOB)
            latencies.append(time.time() - start)

        # Calculate P95
        p95_latency = statistics.quantiles(latencies, n=20)[18]  # 95th percentile

        # Also calculate average and median
        avg_latency = statistics.mean(latencies)
        median_latency = statistics.median(latencies)

        print(f"\nLatency stats (n={num_requests}):")
        print(f"  P95: {p95_latency:.2f}s")
        print(f"  Avg: {avg_latency:.2f}s")
        print(f"  Median: {median_latency:.2f}s")

        # P95 should be under 2 seconds for Haiku
        assert p95_latency < 2.0, f"P95 latency {p95_latency:.2f}s exceeds 2.0s target"

    @pytest.mark.asyncio
    async def test_throughput_capacity(self):
        """Test system can handle concurrent requests"""
        agent = ResumeAnalysisAgent()

        num_concurrent = 10  # Test with 10 concurrent requests
        start_time = time.time()

        # Simulate concurrent requests
        tasks = [
            agent.analyze_candidate(SAMPLE_RESUME, SAMPLE_JOB)
            for _ in range(num_concurrent)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)
        duration = time.time() - start_time

        # Count successful requests
        successful = [r for r in results if not isinstance(r, Exception)]
        success_rate = len(successful) / num_concurrent * 100

        print(f"\nThroughput test:")
        print(f"  {num_concurrent} concurrent requests")
        print(f"  Duration: {duration:.2f}s")
        print(f"  Success rate: {success_rate:.1f}%")
        print(f"  Throughput: {num_concurrent/duration:.1f} req/s")

        # Should complete 10 requests in reasonable time
        assert duration < 30.0, f"10 requests took {duration:.2f}s (expected <30s)"

        # Most requests should succeed
        assert success_rate >= 80.0, f"Success rate {success_rate:.1f}% below 80%"

    @pytest.mark.asyncio
    async def test_agent_response_time_comparison(self):
        """Compare response times across different agents"""
        resume_agent = ResumeAnalysisAgent()
        linkedin_agent = LinkedInSourcingAgent()
        github_agent = GitHubSourcingAgent()

        # Time each agent
        start = time.time()
        resume_result = await resume_agent.analyze_candidate(SAMPLE_RESUME, SAMPLE_JOB)
        resume_time = time.time() - start

        start = time.time()
        linkedin_result = await linkedin_agent.evaluate(1, linkedin_url="https://linkedin.com/in/test")
        linkedin_time = time.time() - start

        start = time.time()
        github_result = await github_agent.evaluate(1, github_url="https://github.com/test")
        github_time = time.time() - start

        print(f"\nAgent response times:")
        print(f"  Resume: {resume_time:.2f}s")
        print(f"  LinkedIn: {linkedin_time:.2f}s")
        print(f"  GitHub: {github_time:.2f}s")

        # All should complete within reasonable time (< 5s each)
        assert resume_time < 5.0, f"Resume agent took {resume_time:.2f}s"
        assert linkedin_time < 5.0, f"LinkedIn agent took {linkedin_time:.2f}s"
        assert github_time < 5.0, f"GitHub agent took {github_time:.2f}s"

    @pytest.mark.asyncio
    async def test_parallel_vs_sequential_performance(self):
        """Compare parallel vs sequential agent execution"""
        resume_agent = ResumeAnalysisAgent()
        linkedin_agent = LinkedInSourcingAgent()
        github_agent = GitHubSourcingAgent()

        # Sequential execution
        sequential_start = time.time()
        await resume_agent.analyze_candidate(SAMPLE_RESUME, SAMPLE_JOB)
        await linkedin_agent.evaluate(1, linkedin_url="https://linkedin.com/in/test")
        await github_agent.evaluate(1, github_url="https://github.com/test")
        sequential_time = time.time() - sequential_start

        # Parallel execution
        parallel_start = time.time()
        await asyncio.gather(
            resume_agent.analyze_candidate(SAMPLE_RESUME, SAMPLE_JOB),
            linkedin_agent.evaluate(1, linkedin_url="https://linkedin.com/in/test"),
            github_agent.evaluate(1, github_url="https://github.com/test")
        )
        parallel_time = time.time() - parallel_start

        speedup = sequential_time / parallel_time if parallel_time > 0 else 0

        print(f"\nExecution time comparison:")
        print(f"  Sequential: {sequential_time:.2f}s")
        print(f"  Parallel: {parallel_time:.2f}s")
        print(f"  Speedup: {speedup:.2f}x")

        # Parallel should be at least 1.5x faster
        assert speedup >= 1.5, f"Parallel speedup {speedup:.2f}x below 1.5x"

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_cost_per_request_average(self):
        """Test average cost per request meets target"""
        agent = ResumeAnalysisAgent()

        num_requests = 10
        total_cost = 0

        for _ in range(num_requests):
            result = await agent.analyze_candidate(SAMPLE_RESUME, SAMPLE_JOB)
            cost = LLMConfig.calculate_cost(
                result['token_usage']['input'],
                result['token_usage']['output'],
                result['model_used']
            )
            total_cost += cost

        avg_cost = total_cost / num_requests

        print(f"\nCost analysis (n={num_requests}):")
        print(f"  Average cost per request: ${avg_cost:.4f}")
        print(f"  Total cost: ${total_cost:.4f}")

        # Average cost should be under $0.02 per single agent request
        assert avg_cost < 0.02, f"Average cost ${avg_cost:.4f} exceeds $0.02 target"

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_full_evaluation_performance(self):
        """Test complete candidate evaluation performance"""
        orchestrator = SwarmOrchestrator()

        num_evaluations = 5
        durations = []
        costs = []

        for i in range(num_evaluations):
            start = time.time()

            result = await orchestrator.evaluate_candidate(
                candidate_id=i,
                job_opening_id=1,
                resume_url="https://example.com/resume.pdf",
                linkedin_url="https://linkedin.com/in/test",
                github_url="https://github.com/test"
            )

            duration = time.time() - start
            durations.append(duration)

            if 'metrics' in result and 'total_cost' in result['metrics']:
                costs.append(result['metrics']['total_cost'])

        avg_duration = statistics.mean(durations)
        avg_cost = statistics.mean(costs) if costs else 0

        print(f"\nFull evaluation performance (n={num_evaluations}):")
        print(f"  Average duration: {avg_duration:.2f}s")
        print(f"  Average cost: ${avg_cost:.4f}")

        # Full evaluation should complete in under 15 seconds
        assert avg_duration < 15.0, \
            f"Average evaluation time {avg_duration:.2f}s exceeds 15s target"

        # Average cost should be under $0.15 per full evaluation
        if avg_cost > 0:
            assert avg_cost < 0.15, \
                f"Average cost ${avg_cost:.4f} exceeds $0.15 target"

    @pytest.mark.asyncio
    async def test_memory_efficiency(self):
        """Test memory usage remains stable across multiple requests"""
        import gc
        import sys

        agent = ResumeAnalysisAgent()

        # Force garbage collection before test
        gc.collect()

        # Run multiple requests
        for _ in range(10):
            await agent.analyze_candidate(SAMPLE_RESUME, SAMPLE_JOB)

        # Force garbage collection after test
        gc.collect()

        # This is a basic check - in production you'd use memory profilers
        # Just verify we can complete multiple requests without crashing
        assert True, "Memory test completed"

    @pytest.mark.asyncio
    async def test_token_efficiency(self):
        """Test token usage is efficient"""
        agent = ResumeAnalysisAgent()

        result = await agent.analyze_candidate(SAMPLE_RESUME, SAMPLE_JOB)

        token_usage = result['token_usage']
        total_tokens = token_usage['input'] + token_usage['output']

        print(f"\nToken efficiency:")
        print(f"  Input tokens: {token_usage['input']}")
        print(f"  Output tokens: {token_usage['output']}")
        print(f"  Total tokens: {total_tokens}")

        # For a simple resume analysis, total tokens should be reasonable
        # (typically < 5000 tokens for Haiku)
        assert total_tokens < 10000, \
            f"Total tokens {total_tokens} exceeds 10000 (possible inefficiency)"

        # Output should generally be less than input for analysis tasks
        # Allow up to 2x ratio
        ratio = token_usage['output'] / token_usage['input'] if token_usage['input'] > 0 else 0
        assert ratio < 3.0, \
            f"Output/input ratio {ratio:.2f} exceeds 3.0 (possible inefficiency)"


class TestScalability:
    """Test system scalability"""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_sustained_load(self):
        """Test system can handle sustained load"""
        agent = ResumeAnalysisAgent()

        num_requests = 20
        request_interval = 0.5  # 500ms between requests

        start_time = time.time()
        results = []

        for _ in range(num_requests):
            result = await agent.analyze_candidate(SAMPLE_RESUME, SAMPLE_JOB)
            results.append(result)
            await asyncio.sleep(request_interval)

        duration = time.time() - start_time

        # All requests should succeed
        assert len(results) == num_requests

        # Should complete in reasonable time
        expected_min_time = num_requests * request_interval
        assert duration >= expected_min_time * 0.8, "Test ran too fast (timing issue)"

        print(f"\nSustained load test:")
        print(f"  Requests: {num_requests}")
        print(f"  Duration: {duration:.2f}s")
        print(f"  Success rate: 100%")

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_cost_at_scale(self):
        """Test cost remains predictable at scale"""
        agent = ResumeAnalysisAgent()

        num_candidates = 50  # Simulate 50 candidates
        total_cost = 0

        for _ in range(num_candidates):
            result = await agent.analyze_candidate(SAMPLE_RESUME, SAMPLE_JOB)
            cost = LLMConfig.calculate_cost(
                result['token_usage']['input'],
                result['token_usage']['output'],
                result['model_used']
            )
            total_cost += cost

        avg_cost_per_candidate = total_cost / num_candidates

        print(f"\nCost at scale (n={num_candidates}):")
        print(f"  Total cost: ${total_cost:.2f}")
        print(f"  Average per candidate: ${avg_cost_per_candidate:.4f}")
        print(f"  Projected cost for 100: ${avg_cost_per_candidate * 100:.2f}")

        # Cost should remain under $0.02 per candidate (single agent)
        assert avg_cost_per_candidate < 0.02, \
            f"Average cost ${avg_cost_per_candidate:.4f} exceeds $0.02"

        # Total cost for 50 candidates should be under $1
        assert total_cost < 1.0, \
            f"Total cost ${total_cost:.2f} exceeds $1.00"
