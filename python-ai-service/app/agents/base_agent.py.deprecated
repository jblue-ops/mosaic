"""
Base Agent - Abstract class for all AI agents
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel
import openai
import os


class AgentVote(BaseModel):
    """Standard vote format from an agent"""

    score: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    reasoning: str
    metadata: Dict[str, Any] = {}


class BaseAgent(ABC):
    """
    Abstract base class for all HoneyBee AI agents

    Each agent evaluates a candidate from a different perspective
    and returns a vote with score, confidence, and reasoning.
    """

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    @abstractmethod
    async def evaluate(
        self,
        candidate_id: int,
        resume_url: Optional[str] = None,
        linkedin_url: Optional[str] = None,
        github_url: Optional[str] = None,
        job_opening_id: Optional[int] = None,
        **kwargs,
    ) -> AgentVote:
        """
        Evaluate a candidate and return a vote

        Args:
            candidate_id: ID of candidate being evaluated
            resume_url: URL to resume (if available)
            linkedin_url: LinkedIn profile URL (if available)
            github_url: GitHub profile URL (if available)
            job_opening_id: Job being evaluated for (if applicable)
            **kwargs: Additional context

        Returns:
            AgentVote with score, confidence, and reasoning
        """
        pass

    async def call_llm(self, prompt: str, temperature: float = 0.3) -> str:
        """
        Helper method to call OpenAI LLM

        Args:
            prompt: The prompt to send
            temperature: Creativity level (0.0 to 1.0)

        Returns:
            LLM response text
        """
        response = self.openai_client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4"),
            messages=[
                {
                    "role": "system",
                    "content": f"You are {self.name}, an AI agent specialized in: {self.description}",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content

    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "name": self.name,
            "description": self.description,
            "status": "ready",
            "version": "0.1.0",
        }
