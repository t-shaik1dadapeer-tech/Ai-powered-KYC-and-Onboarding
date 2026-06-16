"""End-to-end KYC onboarding flow integration tests."""

def test_full_kyc_onboarding_flow(client):
    """Create customer → submit KYC → check status → calculate risk score."""
    create_resp = client.post(
        "/customers",
        json={
            "full_name": "Integration User",
            "email": "integration@example.com",
            "phone": "9876543210",
        },
    )
    assert create_resp.status_code == 201
    customer = create_resp.json()
    customer_id = customer["id"]
    assert customer["status"] == "pending"

    kyc_resp = client.post(
        "/kyc",
        json={
            "customer_id": customer_id,
            "pan": "ABCDE1234F",
            "account_number": "123456789012",
            "ifsc": "HDFC0001234",
        },
    )
    assert kyc_resp.status_code == 201
    kyc = kyc_resp.json()
    assert kyc["status"] == "verified"

    status_resp = client.get(f"/kyc-status/{customer_id}")
    assert status_resp.status_code == 200
    assert status_resp.json()["status"] == "verified"

    risk_resp = client.post("/risk-score", json={"customer_id": customer_id})
    assert risk_resp.status_code == 200
    risk = risk_resp.json()
    assert risk["score"] < 50
    assert risk["band"] in ("low", "medium", "high")

    get_resp = client.get(f"/customer/{customer_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["status"] == "kyc_verified"


def test_health_and_metrics_available(client):
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "healthy"

    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    assert "http_requests_total" in metrics.text
