"""
Enhanced Base Agent - Intelligent model selection with automatic escalation

This base class provides:
- Automatic Haiku → Sonnet escalation on low confidence
- Cost tracking and metrics
- High-stakes detection for immediate premium model use
"""

from anthropic import AsyncAnthropic
from typing import Any
import logging

# Import from core modules (created by parallel agent)
# If these don't exist yet, the other agent is creating them
try:
    from app.core.llm_config import LLMConfig
    from app.agents.agent_registry import AgentConfiguration
except ImportError:
    # Placeholder for parallel execution - will be available once Agent 1 completes
    pass


class EnhancedBaseAgent:
    """Base class for all swarm intelligence agents using Claude 4.5"""

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.llm_client = LLMConfig.get_client()
        self.default_model = AgentConfiguration.get_model_for_agent(agent_name)
        self.logger = logging.getLogger(f"agent.{agent_name}")

        # Metrics tracking
        self.total_requests = 0
        self.escalations = 0
        self.total_tokens = {"input": 0, "output": 0}
        self.total_cost = 0.0

    async def process_request(
        self,
        request: dict[str, Any],
        force_premium: bool = False
    ) -> dict[str, Any]:
        """
        Process request with intelligent model selection

        Args:
            request: Agent request data
            force_premium: Force use of Sonnet 4.5 (for escalations)

        Returns:
            Dict containing analysis, confidence, and metadata
        """
        self.total_requests += 1

        # Step 1: Select appropriate model
        model = self._select_model(request, force_premium)

        # Step 2: Log model selection
        self.logger.info(
            f"Processing request with {model}",
            extra={
                "request_type": request.get("type"),
                "agent": self.agent_name,
                "force_premium": force_premium
            }
        )

        # Step 3: Generate response
        response = await self._generate_response(request, model)

        # Step 4: Track metrics
        self._update_metrics(response, model)

        # Step 5: Check if escalation needed
        if self._should_escalate(response) and not force_premium:
            self.logger.warning(
                f"Low confidence detected, escalating to Sonnet 4.5",
                extra={"confidence": response.get("confidence")}
            )
            self.escalations += 1
            return await self.process_request(request, force_premium=True)

        return response

    def _select_model(
        self,
        request: dict[str, Any],
        force_premium: bool
    ) -> str:
        """Intelligent model selection based on request complexity"""

        # Force premium if requested (escalation)
        if force_premium:
            return LLMConfig.PREMIUM_MODEL

        # Check if high-stakes decision
        if self._is_high_stakes(request):
            return LLMConfig.PREMIUM_MODEL

        # Use agent's default model
        return self.default_model

    def _is_high_stakes(self, request: dict[str, Any]) -> bool:
        """Identify high-stakes decisions requiring Sonnet 4.5"""
        high_stakes_indicators = [
            request.get("decision_type") == "final_hiring_recommendation",
            request.get("compliance_review_required") is True,
            request.get("bias_check_critical") is True,
            request.get("legal_implications") is True,
            request.get("customer_escalation") is True,
            request.get("agent_consensus_failed") is True,
            request.get("edge_case_detected") is True,
        ]

        return any(high_stakes_indicators)

    def _should_escalate(self, response: dict[str, Any]) -> bool:
        """Check if response quality requires escalation to Sonnet 4.5"""
        escalation_triggers = [
            # Low confidence score
            response.get("confidence", 1.0) < LLMConfig.LOW_CONFIDENCE_THRESHOLD,

            # Uncertainty flags present
            len(response.get("uncertainty_flags", [])) > 0,

            # Agent explicitly requests review
            response.get("requires_review") is True,

            # Edge case detected
            response.get("edge_case_detected") is True,

            # Contradictory findings
            response.get("contradictions_found") is True,
        ]

        return any(escalation_triggers)

    async def _generate_response(
        self,
        request: dict[str, Any],
        model: str
    ) -> dict[str, Any]:
        """Generate response using specified Claude 4.5 model"""

        try:
            # Build prompt from request
            user_prompt = self._format_request(request)
            system_prompt = self._get_system_prompt()

            # Call Claude API
            message = await self.llm_client.messages.create(
                model=model,
                max_tokens=LLMConfig.DEFAULT_MAX_TOKENS,
                temperature=LLMConfig.DEFAULT_TEMPERATURE,
                system=system_prompt,
                messages=[{
                    "role": "user",
                    "content": user_prompt
                }]
            )

            # Parse and enrich response
            parsed = self._parse_response(message)
            parsed["model_used"] = model
            parsed["agent_name"] = self.agent_name
            parsed["escalated"] = model == LLMConfig.PREMIUM_MODEL

            # Add token usage
            parsed["token_usage"] = {
                "input": message.usage.input_tokens,
                "output": message.usage.output_tokens,
                "total": message.usage.input_tokens + message.usage.output_tokens
            }

            return parsed

        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            raise

    def _update_metrics(self, response: dict[str, Any], model: str):
        """Update agent performance metrics"""
        usage = response.get("token_usage", {})
        input_tokens = usage.get("input", 0)
        output_tokens = usage.get("output", 0)

        self.total_tokens["input"] += input_tokens
        self.total_tokens["output"] += output_tokens

        # Calculate cost
        cost = LLMConfig.calculate_cost(input_tokens, output_tokens, model)
        self.total_cost += cost

    def get_metrics(self) -> dict[str, Any]:
        """Get agent performance metrics"""
        return {
            "agent_name": self.agent_name,
            "total_requests": self.total_requests,
            "escalations": self.escalations,
            "escalation_rate": (
                self.escalations / self.total_requests
                if self.total_requests > 0
                else 0
            ),
            "total_tokens": self.total_tokens,
            "total_cost": round(self.total_cost, 2),
            "avg_cost_per_request": (
                round(self.total_cost / self.total_requests, 4)
                if self.total_requests > 0
                else 0
            )
        }

    # Abstract methods - must be implemented by subclasses
    def _get_system_prompt(self) -> str:
        """Get agent-specific system prompt"""
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement _get_system_prompt()"
        )

    def _format_request(self, request: dict[str, Any]) -> str:
        """Format request data into prompt"""
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement _format_request()"
        )

    def _parse_response(self, message: Any) -> dict[str, Any]:
        """Parse Claude response into structured format"""
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement _parse_response()"
        )
