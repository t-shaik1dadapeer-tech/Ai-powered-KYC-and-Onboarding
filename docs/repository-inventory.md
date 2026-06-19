# Repository Inventory

**Generated:** 2026-06-17  
**Source:** Direct codebase audit (not inferred)

---

## FastAPI Onboarding Service (`services/onboarding-api/`)

### Routers (Controllers)

| Name | Responsibility | Path |
|------|----------------|------|
| `customers` | Create customer | `app/routers/customers.py` |
| `customer_read` | Get customer by ID | `app/routers/customer_read.py` |
| `kyc` | Submit KYC, get status | `app/routers/kyc.py` |
| `verification` | Standalone PAN/bank verify | `app/routers/verification.py` |
| `risk` | Risk score calculation | `app/routers/risk.py` |
| `health` | Health + Prometheus metrics | `app/routers/health.py` |

### Services

| Name | Responsibility | Path |
|------|----------------|------|
| `CustomerService` | Customer creation, conflict check | `app/services/customer_service.py` |
| `KycService` | Full KYC submission pipeline | `app/services/kyc_service.py` |
| `PanVerificationService` | Mock PAN verification | `app/services/pan_verification_service.py` |
| `BankVerificationService` | Mock bank verification | `app/services/bank_verification_service.py` |
| `StandaloneVerificationService` | PAN/bank without full KYC | `app/services/standalone_verification_service.py` |
| `RiskScoreService` | Risk scoring algorithm | `app/services/risk_score_service.py` |

### Repositories

| Name | Responsibility | Path |
|------|----------------|------|
| `CustomerRepository` | Customer CRUD | `app/repositories/customer_repository.py` |
| `KycRepository` | KYC submissions, PAN/bank records | `app/repositories/kyc_repository.py` |
| `DocumentRepository` | Risk assessment persistence | `app/repositories/document_repository.py` |

### Models (ORM)

| Name | Table | Path |
|------|-------|------|
| `Customer` | `customers` | `app/models/customer.py` |
| `KycSubmission` | `kyc_submissions` | `app/models/kyc.py` |
| `PanRecord` | `pan_records` | `app/models/kyc.py` |
| `BankRecord` | `bank_records` | `app/models/kyc.py` |
| `RiskAssessment` | `risk_assessments` | `app/models/risk.py` |

### Core / Config

| Name | Responsibility | Path |
|------|----------------|------|
| `Settings` | Env-based config | `app/core/config.py` |
| `get_db` | SQLAlchemy session | `app/core/database.py` |
| `metrics` | Prometheus instruments | `app/core/metrics.py` |
| `configure_logging` | structlog JSON | `app/core/logging.py` |
| `AppException` | HTTP error mapping | `app/core/exceptions.py` |

### Tests (21)

| Module | Focus | Path |
|--------|-------|------|
| `test_customers` | Customer API | `tests/test_customers.py` |
| `test_kyc` | KYC API | `tests/test_kyc.py` |
| `test_verification` | PAN/bank | `tests/test_verification.py` |
| `test_risk` | Risk score | `tests/test_risk.py` |
| `test_health` | Health/metrics | `tests/test_health.py` |
| `test_metrics` | Domain metrics | `tests/test_metrics.py` |
| `test_integration` | Full KYC flow | `tests/test_integration.py` |
| `conftest` | In-memory DB fixtures | `tests/conftest.py` |

---

## Intelligence Engine (`engines/intelligence/`)

| Component | Responsibility | Path |
|-----------|----------------|------|
| `RepositoryAnalyzer` | Orchestrate scan pipeline | `src/intelligence/analyzer.py` |
| `cli` | CLI entry point | `src/intelligence/cli.py` |
| Detectors | Framework detection | `src/intelligence/detectors/` |
| Extractors | Inventory extraction | `src/intelligence/extractors/` |
| Generators | Report output | `src/intelligence/generators/` |
| Tracing | Flow + sequence | `src/intelligence/tracing/` |
| Rust bridge | Subprocess enrichment | `src/intelligence/rust_bridge/cli.py` |

**Tests:** 18 — `engines/intelligence/tests/`

---

## Rust Analyzer (`engines/rust-analyzer/`)

| Component | Responsibility | Path |
|-----------|----------------|------|
| `scan` | Full repo scan JSON | `src/scan.rs` |
| `file_walker` | Directory walk + ignore | `src/file_walker.rs` |
| `parser` | Multi-language regex parse | `src/parser/` |
| `graph` | Import graph edges | `src/graph/mod.rs` |
| `risk` | Risk score 0–100 | `src/risk/mod.rs` |
| `main` | CLI (`scan`, `risk`) | `src/main.rs` |

**Tests:** 10 — unit + `tests/integration_test.rs`

---

## Node CLI (`clients/node-cli/`)

| Command | Responsibility | Path |
|---------|----------------|------|
| `customer-create` | POST /customers | `commands/customer-create.js` |
| `submit-kyc` | POST /kyc | `commands/submit-kyc.js` |
| `generate-report` | Run intelligence CLI | `commands/generate-report.js` |
| `ApiClient` | HTTP client | `lib/api-client.js` |
| `validators` | Input validation | `lib/validators.js` |

**Tests:** 17 — `clients/node-cli/tests/`

---

## Infrastructure

| Component | Path |
|-----------|------|
| Docker Compose | `infra/docker/docker-compose.yml` |
| Prometheus | `infra/prometheus/prometheus.yml` |
| Grafana dashboard | `infra/grafana/dashboards/kyc-platform.json` |
| K8s scaffold | `infra/kubernetes/onboarding-api-deployment.yaml` |
| Terraform (scope note) | `infra/terraform/README.md` |
| CI workflow | `.github/workflows/ci.yml` |

---

## Workers / Jobs / Consumers

**None implemented.** Batch/async processing not in scope. KYC is synchronous HTTP-only.

---

## Platform E2E

| Test | Path |
|------|------|
| Cross-stack validation | `tests/e2e/test_platform_e2e.py` (4 tests) |

**Evidence:** `evidence/test-results/phase-7-summary.txt`
