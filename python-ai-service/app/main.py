"""
HoneyBee AI Service - FastAPI Application

Main entry point for the Python AI microservice that orchestrates
6 specialized AI agents for candidate evaluation via swarm intelligence.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from contextlib import asynccontextmanager

from app.api import evaluate, health
from app.db.database import init_db

# Environment
ENV = os.getenv("ENV", "development")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for FastAPI app
    - Startup: Initialize database connection
    - Shutdown: Close connections
    """
    # Startup
    print("🚀 Starting HoneyBee AI Service...")
    await init_db()
    print("✅ Database connection initialized")

    yield

    # Shutdown
    print("👋 Shutting down HoneyBee AI Service...")


# Initialize FastAPI app
app = FastAPI(
    title="HoneyBee AI Service",
    description="Swarm intelligence recruiting platform - AI microservice",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS - allow Rails to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Rails development
        os.getenv("RAILS_URL", "http://localhost:3000"),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(evaluate.router, prefix="/api/v1", tags=["evaluation"])


@app.get("/")
async def root():
    """Root endpoint - service info"""
    return {
        "service": "HoneyBee AI Service",
        "version": "0.1.0",
        "status": "running",
        "environment": ENV,
        "docs": "/docs",
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=ENV == "development",
        log_level="info",
    )
