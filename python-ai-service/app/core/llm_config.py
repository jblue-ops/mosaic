from anthropic import AsyncAnthropic
import os
from typing import Optional

class LLMConfig:
    """Centralized configuration for Claude 4.5 family"""

    # Model definitions
    FAST_MODEL = "claude-haiku-4-5-20251022"
    PREMIUM_MODEL = "claude-sonnet-4-5-20250929"

    # Pricing per 1M tokens
    HAIKU_INPUT_COST = 1.00
    HAIKU_OUTPUT_COST = 5.00
    SONNET_INPUT_COST = 3.00
    SONNET_OUTPUT_COST = 15.00

    # Performance settings
    DEFAULT_MAX_TOKENS = 4096
    DEFAULT_TEMPERATURE = 0.3
    REQUEST_TIMEOUT = 30.0

    # Escalation thresholds
    LOW_CONFIDENCE_THRESHOLD = 0.6
    CONSENSUS_DISAGREEMENT_THRESHOLD = 0.4

    @staticmethod
    def get_client() -> AsyncAnthropic:
        """Get configured Anthropic client"""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set in environment")
        return AsyncAnthropic(api_key=api_key, timeout=LLMConfig.REQUEST_TIMEOUT)

    @staticmethod
    def calculate_cost(input_tokens: int, output_tokens: int, model: str) -> float:
        """Calculate cost for a given request"""
        if "haiku" in model.lower():
            input_cost = (input_tokens / 1_000_000) * LLMConfig.HAIKU_INPUT_COST
            output_cost = (output_tokens / 1_000_000) * LLMConfig.HAIKU_OUTPUT_COST
        else:  # Sonnet
            input_cost = (input_tokens / 1_000_000) * LLMConfig.SONNET_INPUT_COST
            output_cost = (output_tokens / 1_000_000) * LLMConfig.SONNET_OUTPUT_COST
        return input_cost + output_cost
