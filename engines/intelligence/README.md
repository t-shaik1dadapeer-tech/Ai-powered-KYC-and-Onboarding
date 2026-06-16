# Repository Intelligence Engine

Analyzes codebases and generates inventories, API maps, ER diagrams, and flow traces.

## Supported Frameworks

- **FastAPI** (Python)
- **Spring Boot** (Java)
- **Node.js / Express**

## Usage

```bash
cd engines/intelligence
python3 -m venv .venv
source .venv/bin/activate
pip install pydantic pytest ruff

# Analyze onboarding-api
PYTHONPATH=src python -m intelligence.cli \
  "../../services/onboarding-api" \
  -o ../../evidence/api-maps/onboarding-api

# JSON summary
PYTHONPATH=src python -m intelligence.cli ../../services/onboarding-api -o /tmp/reports --json
```

## Output Reports

| File | Description |
|------|-------------|
| `service-inventory.md` | Service classes |
| `controller-inventory.md` | Controllers / routers |
| `api-inventory.md` | HTTP endpoints |
| `model-inventory.md` | ORM / entity models |
| `test-inventory.md` | Test functions |
| `dependency-inventory.md` | Dependencies |
| `er-diagram.mmd` | Mermaid ER diagram |
| `api-map.md` | API mapping document |
| `flow-tracing-report.md` | Request flow chains |
| `uncertainty-report.md` | Low-confidence trace notes |
| `analysis-manifest.json` | Full JSON export |

## Test

```bash
PYTHONPATH=src pytest -v
```
