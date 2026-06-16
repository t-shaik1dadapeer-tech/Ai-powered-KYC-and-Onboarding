def test_submit_kyc_success(client, sample_customer):
    response = client.post(
        "/kyc",
        json={
            "customer_id": sample_customer["id"],
            "pan": "ABCDE1234F",
            "account_number": "123456789012",
            "ifsc": "HDFC0001234",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "verified"
    assert body["pan_verification_status"] == "verified"
    assert body["bank_verification_status"] == "verified"


def test_submit_kyc_invalid_pan(client, sample_customer):
    response = client.post(
        "/kyc",
        json={
            "customer_id": sample_customer["id"],
            "pan": "INVALID",
            "account_number": "123456789012",
            "ifsc": "HDFC0001234",
        },
    )
    assert response.status_code == 422


def test_submit_kyc_rejected_pan(client, sample_customer):
    response = client.post(
        "/kyc",
        json={
            "customer_id": sample_customer["id"],
            "pan": "ABCDE0000A",
            "account_number": "123456789012",
            "ifsc": "HDFC0001234",
        },
    )
    assert response.status_code == 422


def test_get_kyc_status(client, sample_customer):
    client.post(
        "/kyc",
        json={
            "customer_id": sample_customer["id"],
            "pan": "ABCDE1234F",
            "account_number": "123456789012",
            "ifsc": "HDFC0001234",
        },
    )
    response = client.get(f"/kyc-status/{sample_customer['id']}")
    assert response.status_code == 200
    assert response.json()["status"] == "verified"


def test_get_kyc_status_not_found(client, sample_customer):
    response = client.get(f"/kyc-status/{sample_customer['id']}")
    assert response.status_code == 404
