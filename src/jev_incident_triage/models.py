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

    def __post_init__(self) -> None:
        for name in ("incident_id", "pipeline", "environment", "error_message"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        for name in ("failed_rows", "total_rows", "retry_count", "elapsed_minutes", "sla_minutes"):
            value = getattr(self, name)
            if type(value) is not int or value < 0:
                raise ValueError(f"{name} must be a non-negative integer")
        if self.failed_rows > self.total_rows:
            raise ValueError("failed_rows cannot exceed total_rows")
        if not isinstance(self.business_impact, list) or any(
            not isinstance(value, str) or not value.strip() for value in self.business_impact
        ):
            raise ValueError("business_impact must be a list of non-empty strings")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Incident:
        if not isinstance(data, dict):
            raise ValueError("incident must be a JSON object")  # noqa: TRY004 -- invalid JSON shape
        fields = set(cls.__dataclass_fields__)
        missing = fields - data.keys()
        unknown = data.keys() - fields
        if missing:
            raise ValueError(f"missing fields: {', '.join(sorted(missing))}")
        if unknown:
            raise ValueError(f"unknown fields: {', '.join(sorted(unknown))}")
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
