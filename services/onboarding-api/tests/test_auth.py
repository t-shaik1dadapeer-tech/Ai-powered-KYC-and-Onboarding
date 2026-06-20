"""API key middleware — optional auth when API_KEY is set."""

import pytest


@pytest.fixture
def api_key_env(monkeypatch):
    monkeypatch.setenv("API_KEY", "test-secret-key")
    from app.core.config import get_settings

    get_settings.cache_clear()
    yield
    monkeypatch.delenv("API_KEY", raising=False)
    get_settings.cache_clear()


def test_health_public_without_key(api_key_env, client):
    r = client.get("/health")
    assert r.status_code == 200


def test_protected_route_requires_key(api_key_env, client):
    customer_id = "00000000-0000-0000-0000-000000000000"
    r = client.get(f"/customer/{customer_id}")
    assert r.status_code == 401

    r = client.get(
        f"/customer/{customer_id}",
        headers={"X-API-Key": "test-secret-key"},
    )
    assert r.status_code == 404  # auth passed; customer not found
