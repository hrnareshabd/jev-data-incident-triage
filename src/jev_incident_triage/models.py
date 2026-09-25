"""Domain models for incidents and triage results."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class Incident:
    incident_id: str
    pipeline: str
    environment: str
    error_message: str
    failed_rows: int
    total_rows: int
    retry_count: int
    elapsed_minutes: int
    sla_minutes: int
    business_impact: list[str]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Incident:
        return cls(**data)


@dataclass(frozen=True)
class EnrichedIncident:
    incident: Incident
    failed_row_rate: float
    sla_breached: bool

    def as_state(self) -> dict[str, Any]:
        state = asdict(self.incident)
        state.update(
            failed_row_rate=round(self.failed_row_rate, 4),
            sla_breached=self.sla_breached,
        )
        return state


@dataclass(frozen=True)
class TriageDecision:
    incident_id: str
    incident_type: str
    incident_type_confidence: float
    business_impact: float
    urgency: float
    needs_human_review: float
    action: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
