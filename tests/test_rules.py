from jev_incident_triage.rules import decide_action


def test_low_classification_confidence_routes_to_human() -> None:
    assert (
        decide_action(
            incident_type_confidence=0.60,
            business_impact=1.0,
            urgency=1.0,
            needs_human_review=0.1,
            sla_breached=False,
        )
        == "human_review"
    )


def test_sla_breach_escalates() -> None:
    assert (
        decide_action(
            incident_type_confidence=0.95,
            business_impact=2.0,
            urgency=2.0,
            needs_human_review=0.4,
            sla_breached=True,
        )
        == "escalate"
    )


def test_high_human_review_probability_routes_to_human() -> None:
    assert (
        decide_action(
            incident_type_confidence=0.95,
            business_impact=2.0,
            urgency=2.0,
            needs_human_review=0.90,
            sla_breached=False,
        )
        == "human_review"
    )


def test_low_risk_incident_uses_standard_queue() -> None:
    assert (
        decide_action(
            incident_type_confidence=0.95,
            business_impact=1.0,
            urgency=1.0,
            needs_human_review=0.10,
            sla_breached=False,
        )
        == "standard_queue"
    )
