def test_risk_score_without_kyc(client, sample_customer):
    response = client.post("/risk-score", json={"customer_id": sample_customer["id"]})
    assert response.status_code == 200
    body = response.json()
    assert 0 <= body["score"] <= 100
    assert body["band"] in ("low", "medium", "high")
    assert body["factors"]["kyc_verified"] is False


def test_risk_score_after_kyc(client, sample_customer):
    client.post(
        "/kyc",
        json={
            "customer_id": sample_customer["id"],
            "pan": "ABCDE1234F",
            "account_number": "123456789012",
            "ifsc": "HDFC0001234",
        },
    )
    response = client.post("/risk-score", json={"customer_id": sample_customer["id"]})
    assert response.status_code == 200
    body = response.json()
    assert body["score"] < 50
    assert body["factors"]["kyc_verified"] is True


def test_risk_score_customer_not_found(client):
    response = client.post(
        "/risk-score",
        json={"customer_id": "00000000-0000-0000-0000-000000000099"},
    )
    assert response.status_code == 404
