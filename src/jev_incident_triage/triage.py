"""Jev client orchestration."""

from __future__ import annotations

import os

from typesafe_sdk import TypeSafeClient

from .models import EnrichedIncident, TriageDecision
from .questions import build_questions
from .rules import decide_action


def triage_incident(enriched: EnrichedIncident, model: str | None = None) -> TriageDecision:
    selected_model = model or os.getenv("JEV_MODEL", "jev-latest")
    with TypeSafeClient(model=selected_model) as client:
        response = client.system_one(
            state=enriched.as_state(),
            questions=build_questions(),
        )

    incident_type = response.answers["incident_type"]
    business_impact = response.answers["business_impact"]
    urgency = response.answers["urgency"]
    human_review = response.answers["needs_human_review"]

    action = decide_action(
        incident_type_confidence=incident_type.confidence,
        business_impact=business_impact.score,
        urgency=urgency.score,
        needs_human_review=human_review.noul,
        sla_breached=enriched.sla_breached,
    )
    return TriageDecision(
        incident_id=enriched.incident.incident_id,
        incident_type=incident_type.choice,
        incident_type_confidence=incident_type.confidence,
        business_impact=business_impact.score,
        urgency=urgency.score,
        needs_human_review=human_review.noul,
        action=action,
    )
