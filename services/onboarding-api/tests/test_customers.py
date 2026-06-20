def test_create_customer(client):
    response = client.post(
        "/customers",
        json={
            "full_name": "John Smith",
            "email": "john@example.com",
            "phone": "9876543210",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "john@example.com"
    assert body["status"] == "pending"
    assert "id" in body


def test_create_customer_duplicate_email(client, sample_customer):
    response = client.post(
        "/customers",
        json={
            "full_name": "Jane Doe",
            "email": sample_customer["email"],
            "phone": "+919876543210",
        },
    )
    assert response.status_code == 409


def test_create_customer_normalizes_email_case(client):
    response = client.post(
        "/customers",
        json={
            "full_name": "Case Test",
            "email": "Case.User@Example.COM",
            "phone": "9876543210",
        },
    )
    assert response.status_code == 201
    assert response.json()["email"] == "case.user@example.com"


def test_create_customer_duplicate_email_different_case(client, sample_customer):
    response = client.post(
        "/customers",
        json={
            "full_name": "Jane Duplicate",
            "email": "JANE@EXAMPLE.COM",
            "phone": "9876543211",
        },
    )
    assert response.status_code == 409


def test_create_customer_invalid_email(client):
    response = client.post(
        "/customers",
        json={"full_name": "Bad Email", "email": "not-an-email", "phone": "9876543210"},
    )
    assert response.status_code == 422


def test_get_customer(client, sample_customer):
    customer_id = sample_customer["id"]
    response = client.get(f"/customer/{customer_id}")
    assert response.status_code == 200
    assert response.json()["id"] == customer_id


def test_get_customer_not_found(client):
    response = client.get("/customer/00000000-0000-0000-0000-000000000099")
    assert response.status_code == 404
