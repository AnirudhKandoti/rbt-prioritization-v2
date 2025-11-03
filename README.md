# Risk-Based Testing Prioritization System (Incident-Aware v2)

A production-ready reference for **Risk-Based Testing (RBT)** that turns **telemetry + past incidents** into an explainable, ranked list of modules to test and monitor. Includes an **Ops Agent** endpoint that detects spikes and recommends **alert-threshold tweaks** and **runbook steps**.

---

## ✨ What’s inside

- **Incident-aware risk model** – factors in:
  - `incident_count`, `incident_max_severity (1..5)`, and **recency-decay** (`incident_recency`)
- **Telemetry-driven features** – error rate, change frequency, code churn, complexity, customer impact, SLA breaches, test flakiness
- **Explainable output (XAI)** – per-feature contributions and natural-language reasons
- **Ops Agent API** – detects spikes (EWMA on error_rate), suggests temporary alert thresholds, and returns runbook steps

Tech stack: **FastAPI**, **SQLite + SQLAlchemy**, **Pydantic**, **pytest**.

---

## 🚀 Quick Start

> Requires Python **3.11+**.

```bash
# 1) Install
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2) Init DB
python -m app.database --init

# 3) Seed sample data (optional but recommended)
python scripts/load_sample.py
python scripts/load_incidents.py

# 4) Run API
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
# Open interactive docs: http://127.0.0.1:8000/docs
```
Run tests
```
pytest -q

```
Docker (optional)
```
# minimal run if you add your own Dockerfile
# docker build -t rbt-system .
# docker run -p 8000:8000 rbt-system
```
🧭 API Overview

Ingest telemetry

POST /ingest/telemetry
```

{
  "module_name": "checkout",
  "owner": "payments@acme.io",
  "domain": "commerce",
  "events": [
    {"kind": "error_rate", "value": 0.085},
    {"kind": "change_frequency", "value": 8},
    {"kind": "code_churn", "value": 950},
    {"kind": "complexity", "value": 0.72},
    {"kind": "customer_impact", "value": 0.8},
    {"kind": "sla_breaches", "value": 1},
    {"kind": "test_flakiness", "value": 0.2}
  ]
}
```
Ingest incidents (NEW)

POST /ingest/incidents
```
{
  "module_name": "checkout",
  "incidents": [
    {
      "title": "Payment gateway timeout",
      "severity": 4,
      "started_at": "2025-10-12T10:00:00Z",
      "resolved_at": "2025-10-12T10:20:00Z",
      "root_cause": "Third-party latency"
    }
  ]
}
```
Get prioritized modules (incident-aware + XAI)

GET /priorities → example item
```
{
  "module_name": "checkout",
  "score": 78.5,
  "band": "High",
  "contributions": {
    "error_rate": 14.2,
    "incident_count": 7.8,
    "incident_max_severity": 5.0,
    "incident_recency": 6.3,
    "change_frequency": 6.1,
    "code_churn": 4.0,
    "customer_impact": 8.3,
    "sla_breaches": 3.2,
    "test_flakiness": 2.8,
    "complexity": 1.8
  },
  "reasons": [
    "Error rate above 5%.",
    "Multiple incidents recently (>=3).",
    "Recent high-severity incident (sev4+).",
    "Recent incident cluster (recency-weighted)."
  ]
}
```
Module details

GET /modules/{name} → features, score/band, contributions, reasons.

Ops Agent recommendations (NEW)

GET /ops/recommend
Detects spikes via EWMA on error_rate and returns:

suggested_thresholds (temporary adjustments)

runbook_steps (module-aware playbook)

Example:
```
[
  {
    "module_name": "checkout",
    "spike_detected": true,
    "suggested_thresholds": { "error_rate": 0.024 },
    "runbook_steps": [
      "Failover payment provider if persists",
      "Check latest deploys/flags",
      "Inspect error logs and traces",
      "Check dependencies",
      "Adjust canary %, scale up"
    ]
  }
]
```
🧮 Risk Model

The overall score is normalized to [0, 100]:
```
score = 100 * Σ (w_i * normalize_i(value_i)) / Σ (w_i)
```

Default feature weights (see app/config.py):
```
@dataclass
class RiskWeights:
    error_rate: float = 5.0
    change_frequency: float = 4.0
    code_churn: float = 3.0
    complexity: float = 2.0
    customer_impact: float = 4.0
    sla_breaches: float = 3.0
    test_flakiness: float = 2.0
    # Incident-aware
    incident_count: float = 3.5
    incident_max_severity: float = 2.5
    incident_recency: float = 3.0

```
Normalization caps (values beyond cap are clipped; see NORMALIZATION_CAPS):

error_rate: 0.20

change_frequency: 14

code_churn: 2000

complexity: 1.0

customer_impact: 1.0

sla_breaches: 10

test_flakiness: 0.5

incident_count: 10

incident_max_severity: 5

incident_recency: 1.0 (computed as recency-decay below)

Incident recency-decay
```
incident_recency = 1 / (1 + days_since_last_incident / 7)
# ~1.0 if today, ~0.5 at ~7 days, ~0.12 at ~49 days

```
Bands

High: ≥ 70

Medium: 40–69.99

Low: < 40

Explainability (XAI)
For each module, we return:

Per-feature contributions (how much each feature adds to the final score)

Human-readable reasons (threshold-based textual cues)

🧰 Data Model (SQLAlchemy)

Module: name, owner, domain, last_change_at

TelemetryEvent: module_id, kind, value, at

Incident (NEW): module_id, title, severity (1..5), started_at, resolved_at?, root_cause?

RiskSnapshot: module_id, score, band, contributions (JSON), created_at

Uses SQLite by default (rbt.db). To start fresh, delete rbt.db and re-init.

🧪 Testing
```
pytest -q

```
The suite includes spike-detection + recommendation coverage.

🔧 Configuration

Adjust weights/caps in app/config.py to match your environment’s risk posture.

Replace the EWMA spike detector in app/utils/spikes.py with your preferred anomaly detector (e.g., ESD, STL, Prophet) as needed.

🗺️ Roadmap

GitHub/GitLab webhook → auto-populate change_frequency and code_churn

Alembic migrations

Pluggable anomaly detectors (Prometheus/OTel sourced)

Optional UI dashboard (HTMX/React) for drill-downs

🤝 License

MIT — see LICENSE.

🧪 cURL examples
```
# Telemetry
curl -X POST http://127.0.0.1:8000/ingest/telemetry \
  -H "Content-Type: application/json" \
  -d '{"module_name":"checkout","events":[{"kind":"error_rate","value":0.08},{"kind":"code_churn","value":900}]}'

# Incidents
curl -X POST http://127.0.0.1:8000/ingest/incidents \
  -H "Content-Type: application/json" \
  -d '{"module_name":"checkout","incidents":[{"title":"Payment timeout","severity":4,"started_at":"2025-10-12T10:00:00Z"}]}'

# Priorities
curl http://127.0.0.1:8000/priorities

# Ops recommendations
curl http://127.0.0.1:8000/ops/recommend
```
🧩 Troubleshooting

Schema changed / errors reading DB → remove rbt.db, run python -m app.database --init.

Port 8000 busy → uvicorn app.main:app --port 8010.

No data → run scripts/load_sample.py and scripts/load_incidents.py.


