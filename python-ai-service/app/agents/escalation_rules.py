from typing import Dict, Any, Callable
from dataclasses import dataclass

@dataclass
class EscalationRule:
    """Definition of an escalation trigger"""
    name: str
    check_function: Callable[[Dict[str, Any]], bool]
    description: str
    severity: str  # "low" | "medium" | "high"

class EscalationEngine:
    """Centralized escalation logic for all agents"""

    RULES = [
        EscalationRule(
            name="low_confidence",
            check_function=lambda r: r.get("confidence", 1.0) < 0.6,
            description="Agent confidence below threshold",
            severity="high"
        ),
        EscalationRule(
            name="uncertainty_flags",
            check_function=lambda r: len(r.get("uncertainty_flags", [])) > 0,
            description="Agent flagged uncertain findings",
            severity="medium"
        ),
        EscalationRule(
            name="requires_review",
            check_function=lambda r: r.get("requires_review") is True,
            description="Agent explicitly requests human/premium review",
            severity="high"
        ),
        EscalationRule(
            name="edge_case",
            check_function=lambda r: r.get("edge_case_detected") is True,
            description="Unusual or edge case scenario",
            severity="high"
        ),
        EscalationRule(
            name="contradictions",
            check_function=lambda r: r.get("contradictions_found") is True,
            description="Contradictory information detected",
            severity="medium"
        ),
        EscalationRule(
            name="incomplete_data",
            check_function=lambda r: r.get("data_completeness", 1.0) < 0.5,
            description="Insufficient data for reliable analysis",
            severity="medium"
        ),
        EscalationRule(
            name="multiple_red_flags",
            check_function=lambda r: len(r.get("concerns", [])) > 3,
            description="Multiple concerns requiring careful review",
            severity="high"
        ),
    ]

    @classmethod
    def should_escalate(cls, response: Dict[str, Any]) -> tuple[bool, list[str]]:
        """Check if response should be escalated to premium model"""
        triggered = []

        for rule in cls.RULES:
            if rule.check_function(response):
                triggered.append(rule.name)

        # Escalate if any high-severity rule triggered
        high_severity_triggered = any(
            rule.severity == "high"
            for rule in cls.RULES
            if rule.name in triggered
        )

        # Or if multiple medium-severity rules triggered
        medium_severity_count = sum(
            1 for rule in cls.RULES
            if rule.name in triggered and rule.severity == "medium"
        )

        should_escalate = (
            high_severity_triggered or
            medium_severity_count >= 2
        )

        return should_escalate, triggered
