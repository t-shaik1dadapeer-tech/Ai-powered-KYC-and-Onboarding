# AI Learning Coding Agent Skills Assignment — KYC Onboarding API Portfolio Evaluation

**Jira:** [PM4-6752](https://paytmmoney.atlassian.net/browse/PM4-6752)  
**Cloned from:** [PM4-6751](https://paytmmoney.atlassian.net/browse/PM4-6751)  
**Repository:** https://github.com/t-shaik1dadapeer-tech/Ai-powered-KYC-and-Onboarding

---

## Description (copy for Jira)

### Objective

Complete the 24-criterion coding-agent evaluation framework and validate the **onboarding-api** FastAPI service for customer KYC onboarding — PAN verification, bank account verification, and risk scoring. Demonstrate that the repository is production-ready for Front Office onboarding delivery work and that all agent-evaluation evidence is reproducible from the command line.

### What this service does

The **onboarding-api** is a REST backend that runs the KYC onboarding lifecycle:

1. **Register** a customer (`POST /customers`)
2. **Submit KYC** documents — PAN + bank account + IFSC (`POST /kyc`)
3. **Check status** of the latest submission (`GET /kyc-status/{customer_id}`)
4. **Score risk** based on verification outcome (`POST /risk-score`)

Verification is performed inside the API against mock providers (configurable for real PAN/bank integrations). Sensitive fields are hashed before persistence. A Node.js CLI (`kyc-cli`) and curl/Swagger can drive the same flow.

### Repository setup

```bash
make bootstrap          # install Python, Node, and Rust dependencies
make docker-up          # start API + Postgres + Prometheus + Grafana
make test               # run all test suites
make full-24-audit      # verify all 24 evaluation criteria
```

### Application URLs (Docker)

| Service | URL |
|---------|-----|
| Onboarding API | http://localhost:8101 |
| Swagger / OpenAPI UI | http://localhost:8101/docs |
| Prometheus | http://localhost:9191 |
| Grafana | http://localhost:3003 |

OpenAPI specification: `docs/api/openapi.json`

### API scope — 9 REST endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/customers` | Register customer (onboarding step 1) |
| GET | `/customer/{customer_id}` | Fetch customer profile |
| POST | `/kyc` | Submit PAN + bank KYC (onboarding step 2) |
| GET | `/kyc-status/{customer_id}` | Latest KYC submission status |
| POST | `/pan-verify` | Standalone PAN verification |
| POST | `/bank-verify` | Standalone bank account verification |
| POST | `/risk-score` | Risk assessment (score 0–100, band low/medium/high) |
| GET | `/health` | Liveness probe |
| GET | `/metrics` | Prometheus metrics |

**CLI client:** `clients/node-cli/bin/kyc-cli.js` — commands `customer-create`, `submit-kyc`

**Data flow:** Client → onboarding-api → mock PAN/bank providers → Postgres (Docker) or SQLite (local)

### 24 evaluation criteria

#### Beginner (B1–B6)

| ID | Name | Verify command | Primary evidence |
|----|------|----------------|------------------|
| B1 | Repository Inventory | `pytest engines/intelligence/tests/test_analyzer.py -q` | `evidence/api-maps/onboarding-api/` |
| B2 | API Endpoint Mapping | `jq '.paths \| keys \| length' docs/api/openapi.json` | `docs/api/openapi.json` (9 paths) |
| B3 | Test Discovery | `make test` | `evidence/test-results/phase-7-summary.txt` |
| B4 | FastAPI Greenfield | `pytest services/onboarding-api -q` | `services/onboarding-api/app/` |
| B5 | Node.js Greenfield | `npm test` in `clients/node-cli` | `clients/node-cli/` |
| B6 | Rust Greenfield | `cargo test -q` in `engines/rust-analyzer` | `engines/rust-analyzer/` |

#### Intermediate (I1–I6)

| ID | Name | Verify command | Primary evidence |
|----|------|----------------|------------------|
| I1 | ER Diagram | `grep ForeignKey services/onboarding-api/app/models/*.py` | 5 tables: customers, kyc_submissions, pan_records, bank_records, risk_assessments |
| I2 | E2E Flow Trace | `ls evidence/flow-traces/onboarding-api/sequence-diagrams/*.mmd` | 9 sequence diagrams |
| I3 | Safe Change | `make safe-change-check` | `scripts/safe-change-check.sh` |
| I4 | Polyglot Service Pair | `pytest tests/e2e/test_platform_e2e.py -q` | API + CLI + Rust integration |
| I5 | Dockerization | `make docker-verify` | `infra/docker/docker-compose.yml` |
| I6 | Bug Diagnosis | `grep BUG-001 docs/bug-investigation.md` | `docs/bug-investigation.md` |

#### Advanced (A1–A6)

| ID | Name | Verify command | Primary evidence |
|----|------|----------------|------------------|
| A1 | Parallel Planning | `test -f docs/worktrees/merge-strategy.md` | `docs/worktrees/merge-strategy.md` |
| A2 | Git Worktree Execution | `make worktree-demo` | `evidence/worktrees/` |
| A3 | Polyglot Mini-System | `make test` | full monorepo |
| A4 | Repository Modernization | `test -f .github/dependabot.yml` | Dependabot, API key middleware |
| A5 | Agent Code Review | `make ci-local` | `.github/workflows/ci.yml` |
| A6 | Performance Profiling | `make load-test` | `evidence/performance/load-test.txt` |

#### DevOps (D1–D6)

| ID | Name | Verify command | Primary evidence |
|----|------|----------------|------------------|
| D1 | Terraform | `make terraform-verify` | `infra/terraform/` |
| D2 | Docker Compose | `docker compose -f infra/docker/docker-compose.yml config` | compose stack |
| D3 | CI/CD | `make ci-local` | GitHub Actions |
| D4 | Kubernetes | `make k8s-verify` | `infra/kubernetes/` |
| D5 | Reproducible Environment | `make bootstrap && make test` | `scripts/bootstrap.sh` |
| D6 | Observability | `make observability-verify` | Prometheus + Grafana dashboards |

### Verification commands

```bash
make full-24-audit      # 24/24 audit → evidence/evaluation-results/full-24-audit-latest.txt
make evidence-index     # regenerate evidence/INDEX.md
make final-review       # phase 14 scorecard
```

Per-criterion deep reports: `docs/beginner/B1-*` through `docs/beginner/D6-*`

### Current status

**24/24 criteria PASS** — proof: `evidence/evaluation-results/full-24-audit-latest.txt`

---

## Acceptance Criteria

1. All 9 onboarding API endpoints are documented in OpenAPI and callable via Swagger at `/docs`.
2. Full KYC onboarding flow works end-to-end: `POST /customers` → `POST /kyc` → `GET /kyc-status/{id}` → `POST /risk-score`.
3. Node CLI drives onboarding against the Docker API (`customer-create`, `submit-kyc`).
4. All 24 evaluation criteria have reports under `docs/beginner/` with linked evidence paths.
5. `make full-24-audit` passes 24/24; output saved to `evidence/evaluation-results/full-24-audit-latest.txt`.
6. API maps live in `evidence/api-maps/`; flow traces in `evidence/flow-traces/` (no duplicate inventories).
7. Docker stack runs API + Postgres + observability; `GET /health` returns HTTP 200.
8. GitHub Actions CI is green (lint → test → docker build).
9. Final evaluation report exists at `docs/final-evaluation-report.md`.

---

## Manual QA — API onboarding test script

```bash
# 1. Start the stack
make docker-up

# 2. Create a customer
curl -s -X POST http://localhost:8101/customers \
  -H "Content-Type: application/json" \
  -d '{"full_name":"QA User","email":"qa@example.com","phone":"9876543210"}'

# 3. Submit KYC (replace CUSTOMER_ID with UUID from step 2)
curl -s -X POST http://localhost:8101/kyc \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"CUSTOMER_ID","pan":"ABCDE1234F","account_number":"123456789012","ifsc":"HDFC0001234"}'

# 4. Check KYC status and risk score
curl -s http://localhost:8101/kyc-status/CUSTOMER_ID
curl -s -X POST http://localhost:8101/risk-score \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"CUSTOMER_ID"}'
```

---

## References

| Document | Path |
|----------|------|
| 24-criterion quick index | `docs/evaluation-index.md` |
| Architecture overview | `docs/architecture/README.md` |
| Documentation map | `docs/README.md` |
| Beginner reports index | `docs/beginner/README.md` |
| Evidence catalog | `evidence/INDEX.md` |
