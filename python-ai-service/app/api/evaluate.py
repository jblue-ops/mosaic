"""
Candidate evaluation endpoints
"""

from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import os

from app.agents.orchestrator import SwarmOrchestrator

router = APIRouter()

# API authentication
RAILS_API_KEY = os.getenv("AI_SERVICE_API_KEY", "development-key")


class EvaluationRequest(BaseModel):
    """Request model for candidate evaluation"""

    candidate_id: int = Field(..., description="Rails Candidate ID")
    resume_url: Optional[str] = Field(None, description="URL to candidate resume")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL")
    github_url: Optional[str] = Field(None, description="GitHub profile URL")
    job_opening_id: Optional[int] = Field(
        None, description="Rails JobOpening ID for matching"
    )


class EvaluationResponse(BaseModel):
    """Response model for candidate evaluation"""

    candidate_id: int
    job_opening_id: Optional[int]
    agent_votes: Dict[str, Any] = Field(
        ..., description="Individual agent evaluations"
    )
    consensus_details: Dict[str, Any] = Field(..., description="Voting mechanism used")
    overall_confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Overall confidence score"
    )
    bias_flags: List[Dict[str, Any]] = Field(
        default_factory=list, description="EEOC compliance issues"
    )
    evaluated_at: datetime
    processing_time_ms: float
    metrics: Dict[str, Any] = Field(
        default_factory=dict, description="Execution metrics (tokens, cost, escalations)"
    )


@router.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_candidate(
    request: EvaluationRequest,
    authorization: Optional[str] = Header(None),
):
    """
    Main endpoint: Evaluate a candidate using swarm intelligence

    This orchestrates 6 AI agents that collaborate to evaluate the candidate:
    1. LinkedIn Agent - Analyzes professional profile
    2. GitHub Agent - Analyzes code contributions
    3. Resume Agent - Parses and analyzes resume
    4. Bias Detection Agent - Checks for EEOC compliance
    5. Predictive Agent - Forecasts hiring success
    6. Consensus Agent - Aggregates votes and reaches decision

    Args:
        request: Candidate evaluation request
        authorization: Bearer token for API authentication

    Returns:
        EvaluationResponse with agent votes, consensus, and bias flags
    """
    # Verify API key
    if authorization:
        token = authorization.replace("Bearer ", "")
        if token != RAILS_API_KEY:
            raise HTTPException(status_code=401, detail="Invalid API key")
    elif os.getenv("ENV") != "development":
        raise HTTPException(status_code=401, detail="Missing authorization header")

    # Initialize orchestrator and run swarm evaluation
    orchestrator = SwarmOrchestrator()

    try:
        result = await orchestrator.evaluate_candidate(
            candidate_id=request.candidate_id,
            resume_url=request.resume_url,
            linkedin_url=request.linkedin_url,
            github_url=request.github_url,
            job_opening_id=request.job_opening_id
        )

        return EvaluationResponse(**result)

    except Exception as e:
        # Log error and return meaningful response
        raise HTTPException(
            status_code=500,
            detail=f"Error evaluating candidate: {str(e)}"
        )


@router.get("/evaluations/{candidate_id}")
async def get_candidate_evaluations(candidate_id: int):
    """
    Get all evaluations for a specific candidate

    Args:
        candidate_id: Rails Candidate ID

    Returns:
        List of evaluations for the candidate
    """
    # TODO: Query database for evaluations
    return {
        "candidate_id": candidate_id,
        "evaluations": [],
        "total_count": 0,
    }


@router.get("/metrics")
async def get_agent_metrics(
    authorization: Optional[str] = Header(None)
):
    """
    Get detailed agent performance metrics

    Returns metrics for all agents including:
    - Total requests processed
    - Escalation rates
    - Token usage
    - Cost tracking
    """
    # Verify API key
    if authorization:
        token = authorization.replace("Bearer ", "")
        if token != RAILS_API_KEY:
            raise HTTPException(status_code=401, detail="Invalid API key")

    orchestrator = SwarmOrchestrator()
    return orchestrator.get_detailed_metrics()


@router.get("/agents/status")
async def get_agents_status():
    """
    Get status of all agents

    Returns health check status for each agent in the swarm
    """
    orchestrator = SwarmOrchestrator()
    return {
        "agents": orchestrator.get_agent_status(),
        "status": "operational"
    }
