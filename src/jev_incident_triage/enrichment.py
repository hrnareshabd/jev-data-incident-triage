"""Deterministic calculations that should not be delegated to an AI model."""

from .models import EnrichedIncident, Incident


def calculate_failed_row_rate(failed_rows: int, total_rows: int) -> float:
    if failed_rows < 0 or total_rows < 0:
        raise ValueError("Row counts cannot be negative")
    if failed_rows > total_rows:
        raise ValueError("failed_rows cannot exceed total_rows")
    if total_rows == 0:
        return 0.0
    return failed_rows / total_rows


def enrich_incident(incident: Incident) -> EnrichedIncident:
    return EnrichedIncident(
        incident=incident,
        failed_row_rate=calculate_failed_row_rate(incident.failed_rows, incident.total_rows),
        sla_breached=incident.elapsed_minutes > incident.sla_minutes,
    )
