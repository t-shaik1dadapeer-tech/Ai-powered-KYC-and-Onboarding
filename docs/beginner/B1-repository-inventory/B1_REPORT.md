# B1 — Repository Artifact Inventory

**Evaluation criterion:** B1 (Repo Discovery)  
**Repository:** AI-Powered KYC & Onboarding Repository Intelligence Platform  
**Scan date:** 2026-06-19  
**Scope:** Application source, infra config, and test artifacts — excludes `.venv/`, `node_modules/`, `target/`, `.pytest_cache/`, `.tools/`, `.worktrees/`, generated coverage HTML  
**Machine-readable inventory:** `docs/beginner/B1-repository-inventory/artifact-inventory.csv` (72 rows)

---

## 1. Executive Summary

This monorepo contains **four application components** and shared infrastructure:

| Component | Role | Primary language |
|-----------|------|------------------|
| `services/onboarding-api/` | KYC & customer onboarding REST API | Python (FastAPI) |
| `engines/intelligence/` | Repository analysis & report generation | Python |
| `engines/rust-analyzer/` | High-performance repo parser & risk calculator | Rust |
| `clients/node-cli/` | Operator CLI (HTTP client + analyzer wrapper) | JavaScript (Node.js) |

**Artifact totals (application code only):**

| Category | Count | Confidence |
|----------|------:|------------|
| Route handlers (HTTP) | 9 | **Confirmed** |
| Router modules | 6 | **Confirmed** |
| Domain services | 6 | **Confirmed** |
| Repositories / DAOs | 3 | **Confirmed** |
| SQLAlchemy entities | 5 (+ 1 base) | **Confirmed** |
| Pydantic DTOs (onboarding-api) | 10 | **Confirmed** |
| Middleware / filters | 2 | **Confirmed** |
| Abstract interfaces | 1 ABC + 1 mixin | **Confirmed** |
| Bootstrap / entry points | 4 | **Confirmed** |
| Jobs / schedulers | **0** | **Confirmed** (none found) |
| Message consumers / listeners | **0** | **Confirmed** (none found) |
| Test files (executable) | 22 | **Confirmed** |
| Ops / verification scripts | 17 | **Confirmed** |

**B1 verify command (executed live 2026-06-19):**

```bash
cd engines/intelligence && PYTHONPATH=src .venv/bin/pytest tests/test_analyzer.py -q
# Result: 4 passed in 0.64s ✅
```

---

## 2. Architecture Overview

### Layered design (onboarding-api)

```
HTTP Client / CLI
       │
       ▼
┌──────────────────────────────────────┐
│  Routers (Controllers)               │  app/routers/*.py
│  ApiKeyMiddleware, MetricsMiddleware │  app/core/auth.py, app/main.py
└──────────────┬───────────────────────┘
               ▼
┌──────────────────────────────────────┐
│  Services (Business logic)           │  app/services/*.py
└──────────────┬───────────────────────┘
               ▼
┌──────────────────────────────────────┐
│  Repositories (Data access)          │  app/repositories/*.py
└──────────────┬───────────────────────┘
               ▼
┌──────────────────────────────────────┐
│  SQLAlchemy Models + SQLite/Postgres │  app/models/*.py
└──────────────────────────────────────┘
```

**Evidence — router registration:**

```58:63:services/onboarding-api/app/main.py
    app.include_router(customers.router)
    app.include_router(customer_read.router)
    app.include_router(kyc.router)
    app.include_router(verification.router)
    app.include_router(risk.router)
    app.include_router(health.router)
```

### Intelligence engine pipeline

```
CLI (repo-analyze)
    → RepositoryAnalyzer
        → FrameworkDetector (FastAPI / Spring / Node)
        → Extractors (inventory from source)
        → Flow tracers (sequence diagrams)
        → Generators (API map, ER, markdown reports)
        → Optional Rust bridge (rust-analyzer scan)
```

### Polyglot interaction

| From | To | Mechanism |
|------|-----|-----------|
| Node CLI | onboarding-api | HTTP REST (`lib/api-client.js`) |
| Node CLI | intelligence engine | subprocess (`lib/analyzer-client.js`) |
| intelligence engine | rust-analyzer | subprocess (`rust_bridge/cli.py`) |
| Prometheus | onboarding-api | HTTP scrape `/metrics` |
| Operator | rust-analyzer | CLI `scan` / `risk` subcommands |

---

## 3. Technology Stack

### Programming languages

| Language | Application paths | Confidence |
|----------|-------------------|------------|
| **Python 3.9+** | `services/onboarding-api/`, `engines/intelligence/`, `tests/e2e/` | **Confirmed** |
| **Rust 2021** | `engines/rust-analyzer/` | **Confirmed** |
| **JavaScript (Node ≥18)** | `clients/node-cli/` | **Confirmed** |
| **HCL** | `infra/terraform/` | **Confirmed** |
| **YAML** | `infra/`, `.github/` | **Confirmed** |
| **Shell** | `scripts/` | **Confirmed** |

### Frameworks and libraries

| Area | Technology | Evidence |
|------|------------|----------|
| HTTP API | FastAPI, uvicorn, Starlette | `services/onboarding-api/requirements.txt`, `app/main.py` |
| ORM | SQLAlchemy 2.x | `app/models/`, `app/core/database.py` |
| Validation / settings | Pydantic 2.x, pydantic-settings | `app/schemas/`, `app/core/config.py` |
| Logging | structlog | `app/core/logging.py` |
| Metrics | prometheus-client | `app/core/metrics.py` |
| HTTP client (tests/CLI) | httpx, fetch | `requirements.txt`, `lib/api-client.js` |
| CLI (Node) | commander | `clients/node-cli/package.json` |
| CLI (Rust) | clap | `engines/rust-analyzer/Cargo.toml` |
| Repo walking (Rust) | walkdir, regex, serde | `engines/rust-analyzer/Cargo.toml` |
| CI lint | ruff, cargo clippy, cargo fmt | `.github/workflows/ci.yml` |

### Build tools

| Tool | Purpose | Path |
|------|---------|------|
| **pip / hatchling** | Python package build | `*/pyproject.toml` |
| **npm** | Node CLI | `clients/node-cli/package.json` |
| **cargo** | Rust build & test | `engines/rust-analyzer/Cargo.toml` |
| **Make** | Unified commands | `Makefile` |
| **Docker Compose** | Local multi-service stack | `infra/docker/docker-compose.yml` |
| **Terraform** | Local infra registry simulation | `infra/terraform/` |
| **kubectl** (dry-run) | K8s manifest validation | `scripts/k8s-verify.sh` |

### Database technologies

| Technology | Usage | Confidence |
|------------|---------|------------|
| **SQLite** | Default dev/test (`sqlite:///./onboarding.db`) | **Confirmed** — `app/core/config.py:13` |
| **PostgreSQL 16** | Docker Compose + K8s production path | **Confirmed** — `infra/docker/docker-compose.yml`, `infra/kubernetes/kyc-platform.yaml` |
| **psycopg2-binary** | Postgres driver | **Confirmed** — `requirements.txt:10` |

### Messaging technologies

| Technology | Found |
|------------|-------|
| Kafka, RabbitMQ, Redis queues, Celery, SQS | **None** |

No message broker, event bus, or async job queue code exists in the repository (grep across `*.py`, `*.rs`, `*.js`, `*.yml`, `*.tf` returned zero matches).

---

## 4. Repository Structure

```
agent development/
├── services/onboarding-api/     # FastAPI KYC service (layered app/)
│   ├── app/
│   │   ├── core/                # config, auth, db, logging, metrics, exceptions
│   │   ├── models/              # SQLAlchemy entities
│   │   ├── repositories/        # Data access
│   │   ├── routers/             # HTTP controllers
│   │   ├── schemas/             # Pydantic DTOs + validators
│   │   ├── services/            # Business logic
│   │   └── main.py              # Application bootstrap
│   └── tests/                   # 24 pytest tests
├── engines/
│   ├── intelligence/            # Python repo analyzer
│   │   ├── src/intelligence/    # detectors, extractors, generators, tracing
│   │   └── tests/               # 18 pytest tests
│   └── rust-analyzer/           # Rust scan + risk CLI
│       ├── src/                 # parser, graph, risk, scan
│       └── tests/               # 2 integration tests (+ 8 unit in src/)
├── clients/node-cli/            # Node operator CLI
│   ├── bin/kyc-cli.js           # Entry point
│   ├── commands/                # CLI subcommands
│   ├── lib/                     # api-client, validators, errors
│   └── tests/                   # 17 node --test cases
├── tests/e2e/                   # Cross-stack E2E (4 pytest tests)
├── infra/                       # docker, k8s, terraform, prometheus, grafana
├── scripts/                     # 17 verification/automation shell scripts
├── docs/                        # Architecture, evaluation, beginner reports
├── evidence/                    # Test results, audits, generated artifacts
├── verification/                # Phase delivery proof (15 markdown files)
├── .github/workflows/ci.yml     # CI pipeline
└── Makefile                     # Unified dev commands
```

**Tracked source/doc files (excluding generated dirs):** ~269 files

---

## 5. Artifact Counts by Category

| Category | Count | Primary location |
|----------|------:|------------------|
| **Controllers / route handlers** | 9 handlers in 6 routers | `services/onboarding-api/app/routers/` |
| **Services** | 6 domain + 1 analyzer | `app/services/`, `engines/intelligence/.../analyzer.py` |
| **Interfaces / abstract classes** | 1 ABC, 1 mixin | `detectors/base.py`, `models/base.py` |
| **ORM entities** | 5 | `app/models/` |
| **Pydantic DTOs (API)** | 10 | `app/schemas/` |
| **Pydantic DTOs (intelligence)** | 8 | `engines/intelligence/.../models.py` |
| **Repositories / DAOs** | 3 | `app/repositories/` |
| **Jobs / schedulers / cron** | 0 | — |
| **Consumers / listeners / handlers** | 0 | — |
| **Configuration classes** | 1 (`Settings`) | `app/core/config.py` |
| **Configuration files (infra/CI)** | 12+ | `infra/`, `.github/`, `pyproject.toml` ×3 |
| **Middleware / filters** | 2 | `app/core/auth.py`, `app/main.py` |
| **Validators** | 3 modules + inline Pydantic | `schemas/`, `validators.js` |
| **Bootstrap / entry points** | 4 | `main.py`, `cli.py`, `main.rs`, `kyc-cli.js` |
| **Utilities / helpers** | 15+ | `core/`, `lib/`, intelligence extractors/utils |
| **Intelligence detectors** | 3 | `detectors/` |
| **Intelligence extractors** | 3 | `extractors/` |
| **Intelligence generators** | 4 modules | `generators/` |
| **Intelligence tracers** | 2 classes | `tracing/fastapi_tracer.py` |
| **Rust modules** | 10 source files | `engines/rust-analyzer/src/` |
| **Node CLI commands** | 3 | `clients/node-cli/commands/` |
| **Exception hierarchies** | 2 (Python + JS) | `exceptions.py`, `errors.js` |
| **Test files (platform)** | 22 | See §6 test inventory |
| **Shell automation scripts** | 17 | `scripts/` |

---

## 6. Detailed Inventory

### 6.1 Controllers / Route Handlers

| Handler | Method | Path | File | Lines |
|---------|--------|------|------|-------|
| `create_customer` | POST | `/customers` | `app/routers/customers.py` | 11–13 |
| `get_customer` | GET | `/customer/{customer_id}` | `app/routers/customer_read.py` | 13–15 |
| `submit_kyc` | POST | `/kyc` | `app/routers/kyc.py` | 13–15 |
| `get_kyc_status` | GET | `/kyc-status/{customer_id}` | `app/routers/kyc.py` | 18–20 |
| `verify_pan` | POST | `/pan-verify` | `app/routers/verification.py` | 16–18 |
| `verify_bank` | POST | `/bank-verify` | `app/routers/verification.py` | 21–23 |
| `calculate_risk_score` | POST | `/risk-score` | `app/routers/risk.py` | 11–15 |
| `health_check` | GET | `/health` | `app/routers/health.py` | 9–16 |
| `metrics` | GET | `/metrics` | `app/routers/health.py` | 19–21 |

### 6.2 Services

| Class | File | Responsibility |
|-------|------|----------------|
| `CustomerService` | `app/services/customer_service.py` | Create/get customers, duplicate email check |
| `KycService` | `app/services/kyc_service.py` | KYC submission orchestration |
| `RiskScoreService` | `app/services/risk_score_service.py` | Risk score calculation & persistence |
| `StandaloneVerificationService` | `app/services/standalone_verification_service.py` | Standalone PAN/bank endpoints |
| `PanVerificationService` | `app/services/pan_verification_service.py` | Mock PAN verification |
| `BankVerificationService` | `app/services/bank_verification_service.py` | Mock bank verification |
| `RepositoryAnalyzer` | `engines/intelligence/src/intelligence/analyzer.py` | Full-repo analysis orchestration |

### 6.3 Interfaces / Abstract Classes

| Name | Type | File | Evidence |
|------|------|------|----------|
| `FrameworkDetector` | `ABC` with `@abstractmethod detect()` | `engines/intelligence/src/intelligence/detectors/base.py:18` | Plugin interface for framework detection |
| `TimestampMixin` | Mixin (columns only) | `services/onboarding-api/app/models/base.py:14` | Shared timestamps on entities |

**No Java-style interfaces, Rust traits exposed as public API, or TypeScript interfaces in application code.**

### 6.4 Models / Entities / DTOs

**SQLAlchemy entities (`app/models/`):**

| Entity | File |
|--------|------|
| `Customer` | `customer.py` |
| `KycSubmission`, `PanRecord`, `BankRecord` | `kyc.py` |
| `RiskAssessment` | `risk.py` |
| `Base`, `TimestampMixin` | `base.py` |

**Pydantic DTOs (`app/schemas/`):**

| Schema | Type | File |
|--------|------|------|
| `CustomerCreate`, `CustomerResponse` | Request/Response | `customer.py` |
| `KycSubmitRequest`, `KycStatusResponse` | Request/Response | `kyc.py` |
| `PanVerifyRequest/Response`, `BankVerifyRequest/Response` | Request/Response | `verification.py` |
| `RiskScoreRequest`, `RiskScoreResponse` | Request/Response | `risk.py` |

**Intelligence analyzer models (`engines/intelligence/src/intelligence/models.py`):**

`InventoryItem`, `ApiItem`, `ModelItem`, `DependencyItem`, `FlowStep`, `FlowTrace`, `Inventories`, `AnalysisResult`

### 6.5 Repositories / DAOs

| Repository | File | Primary entity |
|------------|------|----------------|
| `CustomerRepository` | `app/repositories/customer_repository.py` | `Customer` |
| `KycRepository` | `app/repositories/kyc_repository.py` | `KycSubmission`, `PanRecord`, `BankRecord` |
| `DocumentRepository` | `app/repositories/document_repository.py` | `RiskAssessment` |

### 6.6 Jobs / Schedulers / Cron Tasks

**None found.** No Celery, APScheduler, cron definitions, or `@scheduled` decorators in application source.

### 6.7 Consumers / Listeners / Message Handlers

**None found.** No event subscribers, queue consumers, or WebSocket handlers.

### 6.8 Configuration

| Artifact | Path | Purpose |
|----------|------|---------|
| `Settings` | `app/core/config.py` | Env-driven app config (`DATABASE_URL`, `API_KEY`, etc.) |
| `docker-compose.yml` | `infra/docker/docker-compose.yml` | Postgres, API, Prometheus, Grafana |
| `.env.example` | `infra/docker/.env.example` | Port and Grafana template vars |
| `prometheus.yml` | `infra/prometheus/prometheus.yml` | Metrics scrape job |
| `kyc-platform.yaml` | `infra/kubernetes/kyc-platform.yaml` | Namespace, Postgres, Ingress |
| `onboarding-api-deployment.yaml` | `infra/kubernetes/onboarding-api-deployment.yaml` | API Deployment + Service |
| `main.tf`, `variables.tf`, `outputs.tf` | `infra/terraform/` | Local Terraform registry |
| `ci.yml` | `.github/workflows/ci.yml` | Lint + 5 test jobs + docker + infra |
| `dependabot.yml` | `.github/dependabot.yml` | Dependency updates |
| `pyproject.toml` | root + 2 services | pytest/ruff/build config |
| Grafana provisioning | `infra/grafana/provisioning/` | Dashboards + datasources |

### 6.9 Middleware / Filters / Interceptors

| Class | File | Behavior |
|-------|------|----------|
| `ApiKeyMiddleware` | `app/core/auth.py:10` | Optional `X-API-Key` when `API_KEY` env set |
| `MetricsMiddleware` | `app/main.py:22` | Records `http_requests_total` and latency histogram |

### 6.10 Validators

| Validator | Location | Mechanism |
|-----------|----------|-----------|
| `PAN_PATTERN`, `IFSC_PATTERN` | `app/schemas/validators.py` | Regex constants |
| Pydantic `@field_validator` | `app/schemas/kyc.py`, `verification.py`, `customer.py` | Schema-level validation |
| `validatePan`, `validateIfsc`, etc. | `clients/node-cli/lib/validators.js` | CLI pre-flight validation |

### 6.11 Bootstrap / Entry Points

| Entry | Command / invocation | File |
|-------|------------------------|------|
| FastAPI app | `uvicorn app.main:app` | `services/onboarding-api/app/main.py` |
| Intelligence CLI | `repo-analyze <path>` | `engines/intelligence/src/intelligence/cli.py` |
| Rust analyzer | `rust-analyzer scan --path <path>` | `engines/rust-analyzer/src/main.rs` |
| Node CLI | `kyc-cli customer-create ...` | `clients/node-cli/bin/kyc-cli.js` |

### 6.12 Test file inventory

| Suite | Files | Tests |
|-------|-------|------:|
| onboarding-api | 10 files in `services/onboarding-api/tests/` (+ `conftest.py`) | 24 |
| intelligence | 6 files in `engines/intelligence/tests/` | 18 |
| node-cli | 4 files in `clients/node-cli/tests/` | 17 |
| rust-analyzer | `tests/integration_test.rs` + 8 unit tests in `src/` | 10 |
| platform E2E | `tests/e2e/test_platform_e2e.py` | 4 |
| **Total** | **22 executable test modules** | **73** |

*Fixture-only:* `engines/intelligence/tests/fixtures/node/tests/users.test.js` — not run by `make test`.

### 6.13 Rust analyzer modules

| Module | File | Purpose |
|--------|------|---------|
| `file_walker` | `src/file_walker.rs` | Recursive repo walk, skip rules |
| `parser` | `src/parser/mod.rs`, `python.rs`, `universal.rs` | Import/class extraction |
| `graph` | `src/graph/mod.rs` | Import dependency graph |
| `risk` | `src/risk/mod.rs` | Repository risk scoring |
| `scan` | `src/scan.rs` | Scan orchestration |
| `error` | `src/error.rs` | Error types |
| `lib` / `main` | `src/lib.rs`, `src/main.rs` | Library + CLI entry |

---

## 7. Notable Findings

| Finding | Detail | Confidence |
|---------|--------|------------|
| **Strict layered architecture** | Routers contain no business logic; all delegate to services → repositories | **Confirmed** |
| **Polyglot but bounded** | Python owns domain; Rust/Node are analysis/CLI only — no duplicate business rules in JS/Rust for KYC | **Confirmed** |
| **Optional API key auth** | Middleware present; disabled when `API_KEY` empty (dev/test default) | **Confirmed** |
| **Mock external verifiers** | PAN/bank verification is in-process mock, not third-party API | **Confirmed** — `pan_verify_mode: mock` in config |
| **No messaging layer** | Synchronous HTTP + CLI only; no async events | **Confirmed** |
| **No Alembic migrations** | Schema via `Base.metadata.create_all()` at startup | **Confirmed** — `app/main.py:41` |
| **Intelligence engine is meta** | Analyzes FastAPI/Spring/Node repos including this one | **Confirmed** |
| **Evidence-driven repo** | `evidence/` holds test output, audits, terraform/k8s verify logs | **Confirmed** |
| **Spring/Node fixtures** | Sample apps under `engines/intelligence/tests/fixtures/` for detector tests — not deployed services | **Confirmed** |

### Missing architectural patterns (notable gaps)

| Pattern | Status |
|---------|--------|
| Database migrations (Alembic/Flyway) | **Not implemented** |
| OAuth2 / JWT auth | **Not implemented** (API key only) |
| Role-based access control | **Not implemented** |
| Message queue / event-driven architecture | **Not present** |
| API gateway code in repo | **Not present** (K8s Ingress manifest only) |
| Frontend SPA | **Not present** |
| Caching layer (Redis) | **Not present** |

---

## 8. Areas Requiring Manual Verification

| Item | Why manual check may be needed |
|------|-------------------------------|
| **Production `API_KEY` deployment** | Auth behavior depends on env var at runtime — verify in target environment |
| **Postgres vs SQLite in prod** | Default is SQLite; Docker/K8s use Postgres — confirm which DB is used per deployment |
| **Grafana external integration** | D6 file-provision paths in `.env` are machine-specific — not portable without edit |
| **Terraform cloud modules** | Current Terraform is local-registry simulation — not AWS/GCP production modules |
| **Spring/Node detector accuracy** | Intelligence engine marks Spring/Node traces as best-effort vs FastAPI deep trace |
| **Fixture tests** | `engines/intelligence/tests/fixtures/node/tests/users.test.js` excluded from platform runner |

---

## 9. Verification Summary

### B1 criterion verify

```bash
cd engines/intelligence && PYTHONPATH=src .venv/bin/pytest tests/test_analyzer.py -q
```

| Field | Value |
|-------|-------|
| **Executed** | 2026-06-19 (re-verified) |
| **Result** | ✅ **4 passed** in 0.64s |
| **Status** | **PASS** |
| **Score** | 9/10 |
| **Risk** | Low |

### Supporting verification

```bash
# Intelligence analyzer produces inventories for this repo
PYTHONPATH=src python -c "
from pathlib import Path
from intelligence.analyzer import analyze_repository
r = analyze_repository(Path('services/onboarding-api'))
print(r.framework, len(r.inventories.apis), 'apis')
"
# Expected: fastapi + 9 apis (Confirmed in test_analyzer.py)

make test   # 73/73 tests, 5/5 suites
```

### Deliverables

| File | Description |
|------|-------------|
| `docs/beginner/B1-repository-inventory/B1_REPORT.md` | This report |
| `docs/beginner/B1-repository-inventory/artifact-inventory.csv` | Machine-readable inventory (72 artifacts) |
| `docs/repository-inventory.md` | Existing concise inventory (reference) |
| `evidence/api-maps/onboarding-api/` | Analyzer-generated API map evidence |

### B1 response format

| Field | Value |
|-------|-------|
| **Status** | PASS |
| **Score** | 9/10 |
| **Completion** | 100% |
| **Risk** | Low |
| **Evidence** | `docs/beginner/B1-repository-inventory/`, `engines/intelligence/`, `evidence/api-maps/` |
| **Missing** | Alembic migrations; production auth hardening |
| **Verify** | `PYTHONPATH=src pytest engines/intelligence/tests/test_analyzer.py -q` |
