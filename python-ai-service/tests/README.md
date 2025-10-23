# HoneyBee AI Service - Test Suite

## Overview

Comprehensive test suite for the Claude 4.5 family integration in the HoneyBee Python AI service. Tests cover integration, performance, swarm intelligence, and error handling.

## Test Structure

```
tests/
├── README.md                      # This file
├── test_claude_integration.py     # Claude 4.5 API integration tests
├── test_swarm_integration.py      # Multi-agent orchestration tests
└── test_performance.py            # Performance benchmarks
```

## Test Files

### test_claude_integration.py
Tests for Claude 4.5 API integration and individual agent functionality.

**Test Classes:**
- `TestClaude45Integration` - Core Claude integration tests
- `TestErrorHandling` - Edge cases and error scenarios

**Coverage:**
- Haiku 4.5 response speed (<3 seconds)
- Sonnet 4.5 thoroughness (bias detection)
- Automatic escalation (Haiku → Sonnet)
- Cost tracking accuracy
- Parallel agent execution
- Token usage structure
- Model configuration
- Error handling (empty data, invalid URLs)

**Key Tests:**
- `test_haiku_resume_analysis_speed` - Verifies Haiku speed
- `test_sonnet_bias_detection_thoroughness` - Verifies Sonnet quality
- `test_automatic_escalation_to_sonnet` - Tests smart escalation
- `test_cost_tracking_accuracy` - Validates cost calculations
- `test_parallel_agent_execution` - Tests concurrent processing

### test_swarm_integration.py
Tests for multi-agent swarm intelligence orchestration.

**Test Classes:**
- `TestSwarmIntelligence` - Swarm coordination tests
- `TestSwarmErrorHandling` - Error recovery tests

**Coverage:**
- Full candidate evaluation workflow
- Multi-agent consensus building
- Bias detection with Sonnet
- Cost distribution (80/20 Haiku/Sonnet)
- Metrics aggregation
- Error handling (missing data, agent failures)

**Key Tests:**
- `test_full_candidate_evaluation` - End-to-end evaluation
- `test_consensus_with_multiple_agents` - Agent coordination
- `test_80_20_cost_split` - Cost distribution verification
- `test_orchestrator_performance` - Speed benchmarks

### test_performance.py
Performance benchmarks and scalability tests.

**Test Classes:**
- `TestPerformance` - Performance benchmarks
- `TestScalability` - Scalability tests

**Coverage:**
- P95 latency targets (<1.5s Haiku)
- Throughput capacity (concurrent requests)
- Sequential vs parallel execution
- Cost per request averages
- Memory efficiency
- Token efficiency
- Sustained load handling
- Cost at scale (50-100 candidates)

**Key Tests:**
- `test_haiku_latency_p95` - P95 latency benchmark
- `test_throughput_capacity` - Concurrent request handling
- `test_parallel_vs_sequential_performance` - Speedup verification
- `test_cost_at_scale` - Cost predictability

**Note:** Tests marked with `@pytest.mark.slow` are longer-running benchmarks.

## Running Tests

### Prerequisites

1. **Install dependencies:**
   ```bash
   cd python-ai-service
   pip install -r requirements.txt
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .env
   # Add your ANTHROPIC_API_KEY to .env
   ```

3. **Verify API key:**
   ```bash
   export ANTHROPIC_API_KEY=sk-ant-your-key-here
   ```

### Basic Test Execution

#### Run all tests:
```bash
pytest
```

#### Run with verbose output:
```bash
pytest -v
```

#### Run specific test file:
```bash
pytest tests/test_claude_integration.py -v
pytest tests/test_swarm_integration.py -v
pytest tests/test_performance.py -v
```

#### Run specific test:
```bash
pytest tests/test_claude_integration.py::TestClaude45Integration::test_haiku_resume_analysis_speed -v
```

#### Run specific test class:
```bash
pytest tests/test_claude_integration.py::TestClaude45Integration -v
```

### Advanced Test Execution

#### Run with coverage:
```bash
pytest --cov=app --cov-report=html
open htmlcov/index.html  # View coverage report
```

#### Run only fast tests (skip slow):
```bash
pytest -v -m "not slow"
```

#### Run only slow/performance tests:
```bash
pytest -v -m slow
```

#### Run with output capture disabled (see print statements):
```bash
pytest -v -s
```

#### Run in parallel (faster):
```bash
pip install pytest-xdist
pytest -n auto  # Use all CPU cores
```

#### Run with detailed failure info:
```bash
pytest -v --tb=long
```

#### Run and stop on first failure:
```bash
pytest -x
```

#### Run last failed tests only:
```bash
pytest --lf
```

## Test Configuration

### pytest.ini
Configure pytest behavior:

```ini
[tool:pytest]
asyncio_mode = auto
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

### Environment Variables

Required for testing:
```bash
ANTHROPIC_API_KEY=sk-ant-...           # Required for API calls
DEFAULT_FAST_MODEL=claude-haiku-4-5-20251022
DEFAULT_PREMIUM_MODEL=claude-sonnet-4-5-20250929
```

Optional for testing:
```bash
ANTHROPIC_TIMEOUT=30
ANTHROPIC_MAX_TOKENS=4096
LOW_CONFIDENCE_THRESHOLD=0.6
ENABLE_AUTO_ESCALATION=true
```

### Mock vs Real Tests

#### Real API Tests (Default)
By default, tests use **real Claude API calls**. This provides:
- Real-world performance data
- Actual cost tracking
- True integration validation

**Pros**: Accurate, realistic
**Cons**: Requires API key, slower, costs money (~$0.50 for full suite)

#### Mock Tests (Coming Soon)
To run tests without API calls:
```bash
export ANTHROPIC_API_KEY=test  # Use "test" to skip real calls
pytest
```

Mock tests will:
- Skip real API calls
- Use pre-recorded responses
- Run faster and free
- Still validate structure/logic

## Test Assertions

### Performance Assertions
```python
# Response time
assert duration < 3.0, "Haiku took too long"

# Throughput
assert requests_per_second > 10, "Low throughput"

# Cost
assert cost_per_request < 0.02, "Cost too high"
```

### Quality Assertions
```python
# Confidence
assert result['confidence'] > 0.0

# Required fields
assert 'overall_match_score' in result
assert 'token_usage' in result

# Model usage
assert result['model_used'] == LLMConfig.FAST_MODEL
```

### Structure Assertions
```python
# Token usage structure
assert 'input' in token_usage
assert 'output' in token_usage
assert token_usage['input'] > 0

# Metrics structure
assert 'total_cost' in metrics
assert 'total_input_tokens' in metrics
```

## Expected Results

### Test Duration
- **Integration tests**: ~30-60 seconds
- **Swarm tests**: ~45-90 seconds
- **Performance tests**: ~2-5 minutes
- **All tests**: ~3-6 minutes

### Test Counts
- **Integration**: 12-15 tests
- **Swarm**: 8-10 tests
- **Performance**: 10-12 tests
- **Total**: ~30-40 tests

### Success Criteria
- ✅ All tests passing
- ✅ No API timeout errors
- ✅ Coverage > 80%
- ✅ P95 latency < 2s
- ✅ Average cost < $0.15/evaluation

## Troubleshooting

### Issue: "ANTHROPIC_API_KEY not set"

**Solution:**
```bash
export ANTHROPIC_API_KEY=sk-ant-your-key-here
```

Or add to `.env`:
```bash
echo "ANTHROPIC_API_KEY=sk-ant-your-key-here" >> .env
```

### Issue: Tests timing out

**Causes:**
- Slow API responses
- Network issues
- API rate limiting

**Solutions:**
```bash
# Increase timeout
export ANTHROPIC_TIMEOUT=60

# Run fewer tests in parallel
pytest -n 2  # Instead of -n auto

# Run tests one at a time
pytest  # No parallel flag
```

### Issue: "Module not found" errors

**Solution:**
```bash
# Ensure you're in the right directory
cd python-ai-service

# Reinstall dependencies
pip install -r requirements.txt

# Verify imports work
python -c "from app.agents.resume_agent import ResumeAnalysisAgent"
```

### Issue: High test costs

**Causes:**
- Running full suite multiple times
- Performance tests with many iterations

**Solutions:**
```bash
# Skip slow/expensive tests
pytest -m "not slow"

# Run specific test file only
pytest tests/test_claude_integration.py

# Use mocked tests (when available)
export ANTHROPIC_API_KEY=test
```

### Issue: Inconsistent test results

**Causes:**
- API latency variation
- Rate limiting
- Network conditions

**Solutions:**
```bash
# Increase tolerance in assertions
# (edit test files to adjust thresholds)

# Run tests during off-peak hours
# (fewer API congestion issues)

# Retry failed tests
pytest --lf  # Re-run last failed
```

### Issue: Import errors for base_agent

**Solution:**
```bash
# Verify migration is complete
ls app/agents/base_agent.py  # Should exist

# Check for old imports
grep -r "BaseAgent" app/agents/

# Should be EnhancedBaseAgent
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          cd python-ai-service
          pip install -r requirements.txt

      - name: Run tests
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          cd python-ai-service
          pytest -v --cov=app

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Best Practices

### Writing New Tests

1. **Use descriptive names:**
   ```python
   def test_haiku_resume_analysis_speed():  # ✅ Good
   def test_speed():                         # ❌ Bad
   ```

2. **Include docstrings:**
   ```python
   async def test_feature(self):
       """Test feature does X when Y happens"""
   ```

3. **Test one thing:**
   ```python
   # ✅ Good - focused test
   async def test_cost_tracking(self):
       result = await agent.evaluate(...)
       assert 'token_usage' in result

   # ❌ Bad - testing too much
   async def test_everything(self):
       # Tests 10 different things
   ```

4. **Use clear assertions:**
   ```python
   # ✅ Good - clear failure message
   assert cost < 0.02, f"Cost ${cost:.4f} exceeds $0.02 target"

   # ❌ Bad - no context
   assert cost < 0.02
   ```

5. **Clean up after tests:**
   ```python
   @pytest.fixture
   def agent():
       agent = ResumeAnalysisAgent()
       yield agent
       # Cleanup if needed
   ```

## Contributing

When adding new tests:

1. **Choose correct file:**
   - Agent-specific → `test_claude_integration.py`
   - Multi-agent coordination → `test_swarm_integration.py`
   - Performance/benchmarks → `test_performance.py`

2. **Follow existing patterns:**
   - Use async/await for async functions
   - Include print statements for debugging
   - Add appropriate markers (`@pytest.mark.slow`)

3. **Update this README:**
   - Add new test descriptions
   - Update test counts
   - Document new fixtures

4. **Run full suite before committing:**
   ```bash
   pytest -v
   ```

## Support

For test-related questions:
- **Documentation**: See `/context/CLAUDE_4_5_ARCHITECTURE.md`
- **Migration Notes**: See `/python-ai-service/MIGRATION_NOTES.md`
- **Slack**: #ai-engineering
- **Email**: engineering@honeybee.ai

---

**Last Updated**: October 22, 2025
**Test Suite Version**: 1.0.0
**Claude Version**: 4.5 (Haiku + Sonnet)
