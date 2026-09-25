"""Transparent business rules composed from Jev's typed judgments."""


def decide_action(
    *,
    incident_type_confidence: float,
    business_impact: float,
    urgency: float,
    needs_human_review: float,
    sla_breached: bool,
) -> str:
    if incident_type_confidence < 0.70:
        return "human_review"
    if urgency >= 3.0 or business_impact >= 3.0 or sla_breached:
        return "escalate"
    if needs_human_review >= 0.75:
        return "human_review"
    return "standard_queue"
