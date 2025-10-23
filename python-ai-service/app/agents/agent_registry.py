from enum import Enum
from typing import Dict

class ModelTier(Enum):
    FAST = "claude-haiku-4-5-20251022"
    PREMIUM = "claude-sonnet-4-5-20250929"

class AgentConfiguration:
    """Define which model each agent uses"""

    AGENT_MODELS: Dict[str, ModelTier] = {
        # Haiku 4.5: High-volume, fast operations (80%)
        "linkedin_sourcing": ModelTier.FAST,
        "github_sourcing": ModelTier.FAST,
        "resume_analysis": ModelTier.FAST,
        "interview_orchestration": ModelTier.FAST,
        "swarm_orchestrator": ModelTier.FAST,

        # Sonnet 4.5: High-stakes, complex reasoning (20%)
        "bias_detection": ModelTier.PREMIUM,
        "predictive_analytics": ModelTier.PREMIUM,
        "consensus_engine": ModelTier.PREMIUM,
    }

    @classmethod
    def get_model_for_agent(cls, agent_name: str) -> str:
        """Get the appropriate model for an agent"""
        config = cls.AGENT_MODELS.get(
            agent_name.lower().replace(" ", "_"),
            ModelTier.FAST  # Default to Haiku
        )
        return config.value
