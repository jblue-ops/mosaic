"""
SQLAlchemy models matching Rails schema

These models map to the same database tables that Rails uses.
Rails manages the schema via migrations.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text,
    Numeric,
    Index,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.database import Base


class Company(Base):
    """Multi-tenant root entity (matches Rails Company model)"""

    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    ats_provider = Column(String)
    ats_credentials = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    candidates = relationship("Candidate", back_populates="company")
    swarm_decisions = relationship(
        "SwarmDecision", secondary="candidates", viewonly=True
    )


class Candidate(Base):
    """External candidate (matches Rails Candidate model)"""

    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, index=True)
    resume_data = Column(JSONB, default={})
    linkedin_url = Column(String)
    github_url = Column(String)
    external_id = Column(String)
    ats_provider = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="candidates")
    swarm_decisions = relationship("SwarmDecision", back_populates="candidate")


class JobOpening(Base):
    """Job opening (matches Rails JobOpening model)"""

    __tablename__ = "job_openings"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    required_skills = Column(JSONB, default={})
    status = Column(Integer, default=0)  # 0=draft, 1=open, 2=closed, 3=filled
    external_id = Column(String)
    ats_provider = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    swarm_decisions = relationship("SwarmDecision", back_populates="job_opening")


class SwarmDecision(Base):
    """AI evaluation audit trail (matches Rails SwarmDecision model)"""

    __tablename__ = "swarm_decisions"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    job_opening_id = Column(Integer, ForeignKey("job_openings.id"))
    decision_type = Column(String)
    agent_votes = Column(JSONB, default={})
    consensus_details = Column(JSONB, default={})
    overall_confidence = Column(Numeric(precision=5, scale=4))
    bias_flags = Column(JSONB, default=[])
    evaluated_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    candidate = relationship("Candidate", back_populates="swarm_decisions")
    job_opening = relationship("JobOpening", back_populates="swarm_decisions")

    # Indexes
    __table_args__ = (
        Index("index_swarm_decisions_on_evaluated_at", "evaluated_at"),
        Index("index_swarm_decisions_on_overall_confidence", "overall_confidence"),
    )


class Skill(Base):
    """Skill taxonomy (matches Rails Skill model)"""

    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True, unique=True)
    category = Column(String)  # technical, soft, domain
    metadata = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CapabilityAssessment(Base):
    """Polymorphic skills assessment (matches Rails CapabilityAssessment model)"""

    __tablename__ = "capability_assessments"

    id = Column(Integer, primary_key=True, index=True)
    person_type = Column(String, nullable=False)  # "Candidate" or "Employee"
    person_id = Column(Integer, nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    proficiency = Column(Integer, default=0)  # 0=beginner, 1=intermediate, 2=advanced, 3=expert
    verified_by = Column(String)
    evidence = Column(JSONB, default={})
    confidence_score = Column(Numeric(precision=5, scale=4))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Indexes
    __table_args__ = (
        Index(
            "idx_unique_capability_per_person_skill",
            "person_type",
            "person_id",
            "skill_id",
            unique=True,
        ),
    )
