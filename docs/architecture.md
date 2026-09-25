# Architecture

```text
Pipeline incident (JSON)
        |
        v
Deterministic Python enrichment
  - failed-row rate
  - SLA breach
        |
        v
One Jev System One request
  - Choice: incident type
  - Score: business impact
  - Score: urgency
  - Noul: human review required?
        |
        v
Transparent Python rules
  - standard queue
  - human review
  - escalation
```

## Why split the work this way?

Arithmetic and fixed comparisons are exact, cheap, and auditable in Python. Jev is used only
for semantic judgments that require interpreting the incident text. The typed results then feed
ordinary rules whose thresholds can be reviewed and changed without rewriting a prompt.

All four questions share one state and are sent in one request. They are independent: no answer
can secretly influence another. A later judgment that truly depends on an earlier result would
belong in a second request.

## Production considerations

- Calibrate thresholds using labelled incidents from the target environment.
- Record model ID, question version, probabilities, action, and human outcome.
- Keep a human-review path for low-confidence or high-impact cases.
- Treat incident text as untrusted input and restrict automated actions.
- Add timeouts, retry limits, observability, and cost monitoring around the API call.
