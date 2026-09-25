# Jev Data Incident Triage

A portfolio-ready Python project that uses **TypeSafe AI's Jev System One model** to turn
data-pipeline incidents into typed judgments and transparent operational actions.

Instead of asking a generative model to write an incident analysis and then parsing prose, the
project sends one structured incident state to Jev and asks four focused questions:

| Primitive | Project question | Result used by the application |
|---|---|---|
| `Choice` | What kind of incident is this? | A fixed category, probabilities, and confidence |
| `Score` | How severe is the business impact? | A position on a defined five-level rubric |
| `Score` | How urgent is the response? | A position on a defined five-level rubric |
| `Noul` | Is human review required? | Probability from 0 (no) to 1 (yes) |

The project is original and focused on Data Engineering operations. TypeSafe AI documentation
and Dave Ebbelaar's AI Cookbook are credited as learning references below.

## The core idea

```text
Incident evidence -> Python enrichment -> Jev typed judgments -> Python rules -> Action
```

`state` is the evidence Jev sees: the error, pipeline, environment, retry count, impact, and
deterministically calculated fields. `Choice`, `Score`, and `Noul` define the shape of each
judgment. Jev returns typed values rather than a free-form explanation.

Python deliberately calculates the failed-row rate and SLA breach because arithmetic and exact
comparisons should remain deterministic. Jev handles semantic interpretation, such as deciding
whether an error represents schema drift or an authentication failure. Plain Python then applies
auditable thresholds to route, review, or escalate the incident.

## Example

Input:

```text
Pipeline: customer_360_daily
Environment: production
Error: customer_id expected BIGINT but received STRING after a CRM deployment
Retries: 3
SLA: 48 minutes elapsed against a 30-minute target
Impact: executive dashboard stale; customer segmentation blocked
```

Illustrative output (real values depend on the model response):

```json
{
  "incident_id": "INC-001",
  "incident_type": "schema_drift",
  "incident_type_confidence": 0.95,
  "business_impact": 3.4,
  "urgency": 3.6,
  "needs_human_review": 0.94,
  "action": "escalate"
}
```

## Setup

Prerequisites: Python 3.10+ and a TypeSafe API key.

```bash
git clone https://github.com/hrnareshabd/jev-data-incident-triage.git
cd jev-data-incident-triage
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
```

Put your key in `.env`:

```dotenv
TYPESAFE_API_KEY=your-key-here
JEV_MODEL=jev-latest
```

`.env` is ignored by Git. Never commit API keys.

## Run

One incident:

```bash
python examples/01_single_incident.py
```

All included samples:

```bash
python examples/02_batch_incidents.py
```

Installed command:

```bash
jev-triage data/sample_incidents.json
```

## Test

```bash
pytest
ruff check .
```

The unit tests do not call Jev or require an API key. They verify deterministic enrichment and
business rules. A GitHub Actions workflow runs linting and tests on Python 3.10 and 3.12.

## Project structure

```text
.
├── .github/workflows/tests.yml
├── data/sample_incidents.json
├── docs/
│   ├── architecture.md
│   └── references.md
├── examples/
│   ├── 01_single_incident.py
│   └── 02_batch_incidents.py
├── src/jev_incident_triage/
│   ├── cli.py
│   ├── enrichment.py
│   ├── models.py
│   ├── questions.py
│   ├── rules.py
│   └── triage.py
├── tests/
│   ├── test_enrichment.py
│   └── test_rules.py
├── .env.example
├── LICENSE
├── pyproject.toml
└── README.md
```

## Limitations

- Jev can make incorrect judgments even when the response is typed.
- The included thresholds are examples, not production policy.
- A real deployment needs evaluation against labelled incidents, monitoring, audit logs, access
  controls, and a safe human-review process.
- No live API test runs in CI because repository secrets are intentionally not required.
- The model accepts text and structured text fields; non-text evidence must be preprocessed.

## References

- [TypeSafe AI introduction](https://docs.typesafe.ai/introduction)
- [TypeSafe AI primitives](https://docs.typesafe.ai/primitives)
- [TypeSafe AI Python SDK](https://docs.typesafe.ai/sdks/python)
- [TypeSafe AI models](https://docs.typesafe.ai/models)
- [Dave Ebbelaar's AI Cookbook Jev examples](https://github.com/daveebbelaar/ai-cookbook/tree/main/models/jev)

See [docs/references.md](docs/references.md) for attribution details. These sources are learning
references; the implementation and Data Engineering use case in this repository are independent.

## Interview explanation

> I built a data-incident triage service that separates deterministic engineering from semantic
> AI judgment. Python calculates exact metrics and SLA status. Jev evaluates four small typed
> questions over the same incident state. Transparent Python rules combine the results into an
> operational action, with confidence gates and a human-review path. This avoids parsing generated
> prose and makes the system easier to test, audit, and calibrate.

## License

MIT
