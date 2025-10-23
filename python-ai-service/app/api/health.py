"""
Health check endpoints
"""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "honeybee-ai",
    }


@router.get("/agents/status")
async def agent_status():
    """
    Check status of all AI agents

    Returns:
        dict: Status of each agent and swarm metrics
    """
    # TODO: Implement actual agent status checking
    return {
        "active_agents": [
            {"name": "linkedin_agent", "status": "ready", "version": "0.1.0"},
            {"name": "github_agent", "status": "ready", "version": "0.1.0"},
            {"name": "resume_agent", "status": "ready", "version": "0.1.0"},
            {"name": "bias_detection_agent", "status": "ready", "version": "0.1.0"},
            {"name": "predictive_agent", "status": "ready", "version": "0.1.0"},
            {"name": "consensus_agent", "status": "ready", "version": "0.1.0"},
        ],
        "swarm_metrics": {
            "total_evaluations": 0,
            "average_confidence": 0.0,
            "bias_flags_detected": 0,
        },
        "timestamp": datetime.utcnow().isoformat(),
    }
