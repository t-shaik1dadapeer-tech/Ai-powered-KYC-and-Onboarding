#!/usr/bin/env bash
# Generate observability evidence: metrics snapshot + dashboard SVG
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EVIDENCE="$ROOT/evidence/observability-results"
SCREENSHOTS="$ROOT/evidence/screenshots"
METRICS_FILE="$EVIDENCE/metrics-snapshot.txt"
LOG="$EVIDENCE/phase-10-observability.txt"
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

mkdir -p "$EVIDENCE" "$SCREENSHOTS"
: > "$LOG"

log() { echo "$1" | tee -a "$LOG"; }

log "Observability Verification — $TIMESTAMP"
log "========================================"
log ""

log "▶ Generate sample traffic + scrape /metrics"
cd "$ROOT/services/onboarding-api"

METRICS_OUT="$METRICS_FILE" PYTHONPATH=. .venv/bin/python - <<'PY' | tee -a "$LOG"
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import get_db
from app.main import app
from app.models.base import Base

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Session = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

with TestClient(app) as client:
    for i in range(3):
        r = client.post(
            "/customers",
            json={
                "full_name": f"Obs User {i}",
                "email": f"obs{i}@example.com",
                "phone": f"900000000{i}",
            },
        )
        assert r.status_code == 201, r.text
        cid = r.json()["id"]
        client.post(
            "/kyc",
            json={
                "customer_id": cid,
                "pan": "ABCDE1234F",
                "account_number": "123456789012",
                "ifsc": "HDFC0001234",
            },
        )
        client.post("/risk-score", json={"customer_id": cid})

    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    out = os.environ["METRICS_OUT"]
    with open(out, "w") as f:
        f.write(metrics.text)

required = [
    "customers_created_total",
    "kyc_submissions_total",
    "pan_verifications_total",
    "bank_verifications_total",
    "risk_assessments_total",
    "risk_score_histogram",
]
body = open(os.environ["METRICS_OUT"]).read()
missing = [m for m in required if m not in body]
if missing:
    raise SystemExit(f"Missing metrics: {missing}")
print("  ✅ All domain metrics present")
PY

log ""
log "▶ Generate dashboard SVG evidence"
SVG="$("$ROOT/scripts/generate-dashboard-evidence.py" "$METRICS_FILE" "$SCREENSHOTS")"
log "  ✅ Dashboard SVG: $SVG"

log ""
log "▶ Run metrics unit tests"
PYTHONPATH=. .venv/bin/pytest -q tests/test_metrics.py | tee -a "$LOG"

log ""
log "▶ Key metric samples"
grep -E "^(customers_created|kyc_submissions|pan_verifications|bank_verifications|risk_assessments)" \
  "$METRICS_FILE" | head -20 | tee -a "$LOG"

log ""
log "========================================"
log "✅ Observability verification complete"
log "Metrics: $METRICS_FILE"
log "Dashboard: $SVG"
log "Grafana JSON: infra/grafana/dashboards/kyc-platform.json"
