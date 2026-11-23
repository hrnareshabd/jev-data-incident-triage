"""Validate a complete batch before any external inference calls."""

from __future__ import annotations

import json
from pathlib import Path

from .models import Incident


def load_incidents(path: Path) -> list[Incident]:
    """Load a JSON array, preserving order and rejecting duplicate incident IDs."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("batch must be a JSON array")  # noqa: TRY004 -- invalid JSON shape
    incidents = []
    seen = set()
    for index, item in enumerate(data, start=1):
        try:
            incident = Incident.from_dict(item)
            if incident.incident_id in seen:
                raise ValueError("duplicate incident_id")
        except ValueError as exc:
            raise ValueError(f"incident {index}: {exc}") from exc
        seen.add(incident.incident_id)
        incidents.append(incident)
    return incidents
