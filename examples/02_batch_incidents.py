"""Triage all sample incidents."""

import json
from pathlib import Path

from dotenv import load_dotenv

from jev_incident_triage.enrichment import enrich_incident
from jev_incident_triage.models import Incident
from jev_incident_triage.triage import triage_incident

load_dotenv()

path = Path(__file__).parents[1] / "data" / "sample_incidents.json"
incidents = json.loads(path.read_text(encoding="utf-8"))

for item in incidents:
    decision = triage_incident(enrich_incident(Incident.from_dict(item)))
    print(json.dumps(decision.as_dict(), indent=2))
