def test_pan_verify_success(client, sample_customer):
    response = client.post(
        "/pan-verify",
        json={"customer_id": sample_customer["id"], "pan": "ABCDE1234F"},
    )
    assert response.status_code == 200
    assert response.json()["verification_status"] == "verified"


def test_pan_verify_invalid_format(client, sample_customer):
    response = client.post(
        "/pan-verify",
        json={"customer_id": sample_customer["id"], "pan": "BADPAN"},
    )
    assert response.status_code == 422


def test_bank_verify_success(client, sample_customer):
    response = client.post(
        "/bank-verify",
        json={
            "customer_id": sample_customer["id"],
            "account_number": "123456789012",
            "ifsc": "HDFC0001234",
        },
    )
    assert response.status_code == 200
    assert response.json()["verification_status"] == "verified"


def test_bank_verify_invalid_account(client, sample_customer):
    response = client.post(
        "/bank-verify",
        json={
            "customer_id": sample_customer["id"],
            "account_number": "000000999999",
            "ifsc": "HDFC0001234",
        },
    )
    assert response.status_code == 422
