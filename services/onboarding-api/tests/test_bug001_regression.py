"""BUG-001 regression: each test must use isolated in-memory DB (see docs/bug-investigation.md)."""

INTEGRATION_EMAIL = "integration@example.com"


def _create_customer(client, email: str = INTEGRATION_EMAIL):
    return client.post(
        "/customers",
        json={
            "full_name": "Integration User",
            "email": email,
            "phone": "9876543210",
        },
    )


def test_bug001_isolation_first_run(client):
    """Same email as test_integration; must succeed on fresh in-memory DB."""
    assert _create_customer(client).status_code == 201


def test_bug001_isolation_second_run(client):
    """Reuses email from sibling test; passes only when conftest resets DB per test."""
    assert _create_customer(client).status_code == 201
