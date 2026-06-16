"""Prometheus metrics instrumentation tests."""

KYC_METRICS = (
    "customers_created_total",
    "kyc_submissions_total",
    "pan_verifications_total",
    "bank_verifications_total",
    "risk_assessments_total",
    "risk_score_histogram",
    "kyc_submissions_active",
    "http_requests_total",
    "http_request_duration_seconds",
)


def test_kyc_flow_exposes_domain_metrics(client):
    """Full onboarding flow increments KYC and risk metrics."""
    create = client.post(
        "/customers",
        json={
            "full_name": "Metrics User",
            "email": "metrics-user@example.com",
            "phone": "9111222333",
        },
    )
    assert create.status_code == 201
    customer_id = create.json()["id"]

    kyc = client.post(
        "/kyc",
        json={
            "customer_id": customer_id,
            "pan": "ABCDE1234F",
            "account_number": "123456789012",
            "ifsc": "HDFC0001234",
        },
    )
    assert kyc.status_code == 201

    risk = client.post("/risk-score", json={"customer_id": customer_id})
    assert risk.status_code == 200

    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    body = metrics.text

    for name in KYC_METRICS:
        assert name in body, f"Missing metric: {name}"

    assert 'kyc_submissions_total{status="verified"}' in body
    assert 'customers_created_total{status="pending"}' in body
    assert "risk_assessments_total" in body
