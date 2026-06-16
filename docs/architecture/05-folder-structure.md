# Repository Folder Structure

## 1. Top-Level Layout

```
kyc-repo-intelligence/
├── .github/
│   └── workflows/
│       ├── ci.yml                    # Lint, test, integration, docker
│       └── release-artifacts.yml     # Evidence artifact upload
│
├── services/
│   └── onboarding-api/               # I1 — FastAPI KYC service
│       ├── app/
│       │   ├── main.py
│       │   ├── routers/
│       │   ├── services/
│       │   ├── repositories/
│       │   ├── models/
│       │   ├── schemas/
│       │   └── core/
│       ├── tests/
│       ├── alembic/                  # DB migrations
│       ├── pyproject.toml
│       └── Dockerfile
│
├── engines/
│   ├── intelligence/                 # Python orchestrator (B1–B5)
│   │   ├── src/intelligence/
│   │   │   ├── detectors/
│   │   │   ├── extractors/
│   │   │   ├── generators/
│   │   │   └── rust_bridge/
│   │   ├── tests/
│   │   └── pyproject.toml
│   │
│   └── rust-analyzer/                # I3 — Rust parsing engine
│       ├── src/
│       │   ├── main.rs
│       │   ├── file_walker.rs
│       │   ├── parser/
│       │   ├── graph/
│       │   └── risk/
│       ├── benches/
│       ├── tests/
│       └── Cargo.toml
│
├── clients/
│   └── node-cli/                     # I2 — Node.js CLI
│       ├── bin/kyc-cli.js
│       ├── lib/
│       ├── commands/
│       ├── tests/
│       ├── package.json
│       └── Dockerfile
│
├── infra/
│   ├── docker/
│   │   ├── docker-compose.yml
│   │   └── docker-compose.dev.yml
│   ├── prometheus/
│   │   └── prometheus.yml
│   └── grafana/
│       ├── dashboards/
│       │   └── kyc-platform.json
│       └── provisioning/
│
├── docs/
│   ├── architecture/                 # Phase 1 (this folder)
│   ├── evaluation/                   # Phase 0 matrix
│   ├── api/                          # OpenAPI exports, API guides
│   └── worktrees/                    # Phase 11 worktree guide
│
├── evidence/                         # D2 — proof store
│   ├── architecture/
│   ├── diagrams/
│   ├── flow-traces/
│   ├── api-maps/
│   ├── test-results/
│   ├── docker-results/
│   ├── ci-results/
│   └── screenshots/
│
├── verification/                     # A2 — per-phase verification
│   ├── phase-0.md
│   ├── phase-1.md
│   └── ...
│
├── reports/                          # Generated analyzer markdown (gitignored runs)
│   └── .gitkeep
│
├── scripts/
│   ├── bootstrap.sh                  # Dev environment setup
│   ├── verify-phase.sh               # Run phase verification
│   └── generate-evidence-index.sh
│
├── Makefile                            # Unified commands for agents & humans
├── README.md
├── CONTRIBUTING.md
├── sdlc-config.yaml                  # Optional pipeline config
└── .analyzerignore                   # Paths skipped by Rust walker
```

---

## 2. FastAPI Service Layout (`services/onboarding-api/`)

```
app/
├── main.py                 # App factory, middleware, router registration
├── routers/
│   ├── customers.py        # POST/GET customers
│   ├── kyc.py              # POST /kyc, GET /kyc-status/{id}
│   ├── verification.py     # POST /pan-verify, POST /bank-verify
│   ├── risk.py             # POST /risk-score
│   └── health.py           # GET /health, GET /metrics
├── services/
│   ├── customer_service.py
│   ├── kyc_service.py
│   ├── pan_verification_service.py
│   ├── bank_verification_service.py
│   └── risk_score_service.py
├── repositories/
│   ├── customer_repository.py
│   ├── kyc_repository.py
│   └── document_repository.py
├── models/
│   ├── base.py             # Declarative base, mixins
│   ├── customer.py
│   ├── kyc.py
│   └── risk.py
├── schemas/
│   ├── customer.py         # CustomerCreate, CustomerResponse
│   ├── kyc.py
│   ├── verification.py
│   └── risk.py
└── core/
    ├── config.py           # Settings (DATABASE_URL, LOG_LEVEL, ...)
    ├── database.py         # Session factory
    ├── logging.py          # structlog configuration
    ├── exceptions.py       # AppException hierarchy
    └── metrics.py          # Prometheus instruments
```

### Layer Rules

| Layer | May Import | Must Not Import |
|-------|------------|-----------------|
| `routers` | services, schemas, core | repositories, models directly |
| `services` | repositories, schemas, models, core | FastAPI Request/Response |
| `repositories` | models, core.database | routers, services |
| `models` | SQLAlchemy only | everything else |

---

## 3. Intelligence Engine Layout

```
src/intelligence/
├── __init__.py
├── cli.py                  # `python -m intelligence analyze <path>`
├── api.py                  # Optional FastAPI wrapper (port 8001)
├── detectors/
│   ├── base.py
│   ├── spring_boot.py
│   ├── fastapi.py
│   └── nodejs.py
├── extractors/
│   ├── services.py
│   ├── controllers.py
│   ├── apis.py
│   ├── models.py
│   ├── tests.py
│   └── dependencies.py
├── generators/
│   ├── markdown.py
│   ├── er_diagram.py
│   ├── api_map.py
│   └── flow_trace.py
└── rust_bridge/
    ├── cli.py              # Invoke rust-analyzer subprocess
    └── adapter.py          # JSON → Python dataclasses
```

---

## 4. Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Python modules | snake_case | `customer_service.py` |
| Python classes | PascalCase | `CustomerService` |
| API paths | kebab-case | `/kyc-status/{id}` |
| Rust modules | snake_case | `file_walker.rs` |
| Node commands | kebab-case | `customer-create` |
| Test files | `test_*.py`, `*.test.js`, `*_test.rs` | `test_customers.py` |
| Evidence files | descriptive kebab | `flow-post-customers.md` |

---

## 5. Configuration Management

| Service | Config Source | Secrets |
|---------|---------------|---------|
| FastAPI | `app/core/config.py` + env | `DATABASE_URL`, API keys |
| Intelligence | `src/intelligence/config.py` | None (local FS) |
| Rust | CLI flags + env | None |
| Node CLI | `.env` (local) + flags | `API_BASE_URL` |
| Docker | compose env files | `infra/docker/.env.example` |
| Prometheus | `infra/prometheus/prometheus.yml` | None |

---

## 6. Evaluation Mapping

| Dimension | Coverage |
|-----------|----------|
| D6 | Layer rules, naming conventions |
| I1 | FastAPI folder layout |
| I2 | Node CLI layout |
| I3 | Rust engine layout |
| D2 | evidence/ tree definition |
| A2 | verification/ tree definition |
