"""
Platform E2E tests — cross-component validation without external services.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[2]
ONBOARDING_API = REPO_ROOT / "services" / "onboarding-api"
INTELLIGENCE = REPO_ROOT / "engines" / "intelligence"
NODE_CLI = REPO_ROOT / "clients" / "node-cli"
RUST_ANALYZER = REPO_ROOT / "engines" / "rust-analyzer" / "target" / "release" / "rust-analyzer"


@pytest.fixture
def api_client():
    sys.path.insert(0, str(ONBOARDING_API))
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
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_e2e_api_kyc_pipeline(api_client):
    """Simulates CLI payloads through the full API pipeline."""
    create = api_client.post(
        "/customers",
        json={"full_name": "E2E User", "email": "e2e@example.com", "phone": "9123456780"},
    )
    assert create.status_code == 201
    cid = create.json()["id"]

    kyc = api_client.post(
        "/kyc",
        json={
            "customer_id": cid,
            "pan": "ABCDE1234F",
            "account_number": "123456789012",
            "ifsc": "HDFC0001234",
        },
    )
    assert kyc.status_code == 201

    risk = api_client.post("/risk-score", json={"customer_id": cid})
    assert risk.status_code == 200
    assert risk.json()["factors"]["kyc_verified"] is True


def test_e2e_intelligence_analyzes_onboarding_api():
    env = {**os.environ, "PYTHONPATH": "src"}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "intelligence.cli",
            str(ONBOARDING_API),
            "-o",
            "/tmp/e2e-reports",
        ],
        cwd=str(INTELLIGENCE),
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr + result.stdout
    combined = result.stdout + result.stderr
    assert "fastapi" in combined.lower()


@pytest.mark.skipif(not RUST_ANALYZER.is_file(), reason="rust-analyzer not built")
def test_e2e_rust_scan_onboarding_api():
    result = subprocess.run(
        [str(RUST_ANALYZER), "scan", "--path", str(ONBOARDING_API)],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(result.stdout)
    assert data["file_count"] > 0
    assert "risk" in data


def test_e2e_node_cli_validators():
    """Node validator logic via subprocess node -c check modules load."""
    validators = NODE_CLI / "lib" / "validators.js"
    assert validators.is_file()
    result = subprocess.run(
        ["node", "-e", f"require('{validators}'); console.log('ok')"],
        capture_output=True,
        text=True,
        cwd=str(NODE_CLI),
    )
    assert result.returncode == 0
