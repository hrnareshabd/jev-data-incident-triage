"""Focused Jev questions for one shared incident state."""

from typesafe_sdk import Choice, Noul, Score


def build_questions() -> dict[str, Choice | Score | Noul]:
    return {
        "incident_type": Choice(
            instructions=(
                "Which category best describes the primary failure in `error_message`, "
                "considering the other incident fields?"
            ),
            criteria={
                "schema_drift": "A field, type, or schema changed incompatibly.",
                "data_quality": "Data is missing, duplicated, invalid, or outside expectations.",
                "authentication_failure": "Credentials, secrets, tokens, or permissions failed.",
                "infrastructure_failure": "Compute, network, storage, or orchestration failed.",
                "other": "The incident does not fit the other categories.",
            },
        ),
        "business_impact": Score(
            instructions="How severe is the operational impact described in `business_impact`?",
            criteria=[
                "No user-visible effect and no dependent workload is blocked.",
                "Minor delay or one non-critical downstream consumer is affected.",
                "Several consumers are delayed or an important report is stale.",
                "A business-critical workflow is blocked or its SLA is breached.",
                "Widespread outage, major financial risk, or regulatory impact.",
            ],
        ),
        "urgency": Score(
            instructions=(
                "How urgently should this incident be handled, using `environment`, "
                "`retry_count`, `sla_breached`, and `business_impact`?"
            ),
            criteria=[
                "Can wait for routine backlog review.",
                "Should be investigated during normal working hours.",
                "Needs prompt same-day investigation.",
                "Needs immediate on-call attention.",
                "Critical response and leadership escalation are required.",
            ],
        ),
        "needs_human_review": Noul(
            instructions=(
                "Does this incident require a human to inspect, approve, or remediate it "
                "rather than relying only on an automatic retry?"
            ),
        ),
    }
