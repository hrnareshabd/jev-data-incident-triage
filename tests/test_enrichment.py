import pytest

from jev_incident_triage.enrichment import calculate_failed_row_rate, enrich_incident
from jev_incident_triage.models import Incident


def make_incident(**overrides: object) -> Incident:
    values = {
        "incident_id": "INC-TEST",
        "pipeline": "test_pipeline",
        "environment": "production",
        "error_message": "test error",
        "failed_rows": 25,
        "total_rows": 100,
        "retry_count": 1,
        "elapsed_minutes": 31,
        "sla_minutes": 30,
        "business_impact": ["test impact"],
    }
    values.update(overrides)
    return Incident(**values)


def test_calculates_failed_row_rate() -> None:
    assert calculate_failed_row_rate(25, 100) == 0.25


def test_zero_total_rows_returns_zero() -> None:
    assert calculate_failed_row_rate(0, 0) == 0.0


def test_invalid_counts_raise_value_error() -> None:
    with pytest.raises(ValueError):
        calculate_failed_row_rate(101, 100)


def test_enrichment_marks_sla_breach() -> None:
    enriched = enrich_incident(make_incident())
    assert enriched.failed_row_rate == 0.25
    assert enriched.sla_breached is True
