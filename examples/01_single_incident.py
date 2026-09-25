"""Triage one realistic data-pipeline incident."""

import json

from dotenv import load_dotenv

from jev_incident_triage.enrichment import enrich_incident
from jev_incident_triage.models import Incident
from jev_incident_triage.triage import triage_incident

load_dotenv()

incident = Incident(
    incident_id="INC-001",
    pipeline="customer_360_daily",
    environment="production",
    error_message="customer_id expected BIGINT but received STRING after a CRM deployment.",
    failed_rows=18_420,
    total_rows=250_000,
    retry_count=3,
    elapsed_minutes=48,
    sla_minutes=30,
    business_impact=[
        "Power BI executive dashboard has not refreshed.",
        "Customer segmentation pipeline is blocked.",
    ],
)

decision = triage_incident(enrich_incident(incident))
print(json.dumps(decision.as_dict(), indent=2))
