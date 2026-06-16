# onboarding-api

FastAPI KYC & customer onboarding service (Phase 2).

## Setup

```bash
cd services/onboarding-api
python3 -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn sqlalchemy pydantic pydantic-settings email-validator structlog prometheus-client httpx pytest pytest-asyncio pytest-cov ruff
```

## Run

```bash
PYTHONPATH=. uvicorn app.main:app --reload --port 8000
```

OpenAPI docs: http://localhost:8000/docs

## Test

```bash
PYTHONPATH=. pytest -v
PYTHONPATH=. pytest --cov=app --cov-report=term-missing
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/customers` | Create customer |
| GET | `/customer/{id}` | Get customer |
| POST | `/kyc` | Submit KYC (PAN + bank) |
| GET | `/kyc-status/{id}` | KYC status |
| POST | `/pan-verify` | Standalone PAN verification |
| POST | `/bank-verify` | Standalone bank verification |
| POST | `/risk-score` | Calculate risk score |
| GET | `/health` | Health check |
| GET | `/metrics` | Prometheus metrics |

## Architecture

Layered design: **routers → services → repositories → models**

See `docs/architecture/` for full system design.
