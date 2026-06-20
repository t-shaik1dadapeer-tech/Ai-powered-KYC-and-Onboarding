# A3 — Polyglot Mini-System Verification

**Evaluation criterion:** A3 (Polyglot Mini-System)  
**Components:** FastAPI `services/onboarding-api/` · Node.js `clients/node-cli/` · Rust `engines/rust-analyzer/`  
**Bridge:** Python intelligence `engines/intelligence/` (Node→Python→Rust for analysis)  
**Verification date:** 2026-06-20T06:02:39Z (UTC)  
**Evidence:** `evidence/test-results/a3-run-2026-06-20T060239Z/`  
**Machine-readable:** `data-contract.md`, `architecture.mmd`

---

## 1. Executive Summary

| Check | Result | Confidence |
|-------|--------|------------|
| FastAPI ingestion service discovered | **PASS** — `app/main.py`, 9 endpoints | High |
| Node.js component discovered | **PASS** — CLI (not queue worker) | High |
| Rust scoring engine discovered | **PASS** — CLI + library, repo risk scoring | High |
| Data contracts documented | **PASS** — HTTP, subprocess, JSON schemas | High |
| Operational flow (Node → API → Python risk) | **PASS** — live on `:8113` | High |
| Intelligence flow (Node → Python → Rust) | **PASS** — `generate-report` + `rust_scan` in manifest | High |
| API startup | **PASS** | High |
| Node CLI execution | **PASS** | High |
| Rust release build | **PASS** | High |
| Python tests | **28/28 PASS** | High |
| Node tests | **17/17 PASS** | High |
| Rust tests | **10/10 PASS** (8 unit + 2 integration) | High |
| Intelligence tests | **18/18 PASS** (incl. rust bridge) | High |
| Platform E2E | **4/4 PASS** | High |
| README run order | **PARTIAL** — split across 4 READMEs, no single polyglot sequence | Medium |

**Overall A3 status: PASS (9/10)** — three-language system verified with live integration and full test matrix. Node is a **CLI client**, not a background worker; Rust scores **repository risk**, not per-customer KYC in the HTTP path.

---

## 2. Architecture Diagram

See [`architecture.mmd`](architecture.mmd). Two distinct polyglot flows coexist:

```
Operational:     Node CLI ──HTTP──► FastAPI ──► Python RiskScoreService ──► DB
Intelligence:    Node CLI ──spawn──► Python Intelligence ──spawn──► Rust Analyzer ──► Reports
```

There is **no** single runtime chain `FastAPI → Worker → Rust → Result` for KYC requests. The closest end-to-end polyglot path is **`generate-report`**: Node spawns Python, which optionally invokes Rust and writes artifacts.

---

## 3. Component Analysis

### 3.1 FastAPI Ingestion Service

| Item | Value |
|------|-------|
| **Entry point** | `services/onboarding-api/app/main.py` — `app = create_app()` |
| **ASGI run** | `uvicorn app.main:app --port 8000` |
| **Lifespan** | `Base.metadata.create_all` on startup |

**Endpoints (routers):**

| Method | Path | Handler | Schema |
|--------|------|---------|--------|
| POST | `/customers` | `customers.create_customer` | `CustomerCreate` |
| GET | `/customer/{id}` | `customer_read.get_customer` | `CustomerResponse` |
| POST | `/kyc` | `kyc.submit_kyc` | `KycSubmitRequest` |
| GET | `/kyc-status/{id}` | `kyc.get_kyc_status` | `KycStatusResponse` |
| POST | `/pan-verify` | `verification.verify_pan` | `PanVerifyRequest` |
| POST | `/bank-verify` | `verification.verify_bank` | `BankVerifyRequest` |
| POST | `/risk-score` | `risk.calculate_risk_score` | `RiskScoreRequest` |
| GET | `/health` | `health.health_check` | — |
| GET | `/metrics` | `health.metrics` | Prometheus text |

**Validation:** Pydantic v2 in `app/schemas/` — PAN/IFSC regex (`validators.py`), email normalization (`customer.py`).

**Data models (SQLAlchemy):** `Customer`, `KycSubmission`, `PanRecord`, `BankRecord`, `RiskAssessment` under `app/models/`.

### 3.2 Node.js Component (CLI, not worker)

| Item | Value |
|------|-------|
| **Entry** | `clients/node-cli/bin/kyc-cli.js` (commander) |
| **HTTP client** | `lib/api-client.js` — `ApiClient` |
| **Analyzer bridge** | `lib/analyzer-client.js` — `generateReport()` |
| **Commands** | `customer-create`, `submit-kyc`, `generate-report` |

**Processing model:** Synchronous CLI invocations. No queue (Bull, Redis, SQS), no file watcher worker, no daemon process.

**Data handling:** Client-side validation in `lib/validators.js` before HTTP; JSON mapping camelCase → snake_case in `ApiClient`.

### 3.3 Rust Scoring Engine

| Item | Value |
|------|-------|
| **CLI** | `engines/rust-analyzer/src/main.rs` — subcommands `scan`, `risk` |
| **Library** | `engines/rust-analyzer/src/lib.rs` — `scan_repository()` |
| **Risk logic** | `engines/rust-analyzer/src/risk/mod.rs` — `calculate_risk()` |
| **I/O** | stdin: `--path`; stdout: JSON `ScanResult` |

**Scoring factors (repository-level):** test ratio, avg lines/file, secret pattern hits, dependency count → score 0–100, band low/medium/high.

**Distinct from API risk:** FastAPI `RiskScoreService` uses KYC verification state (Python); Rust uses static repo analysis.

---

## 4. Data Contract Summary

Full contracts: [`data-contract.md`](data-contract.md)

| Link | Protocol | Payload |
|------|----------|---------|
| Node → FastAPI | HTTP/JSON | Customer + KYC DTOs |
| Node → Python | subprocess + stdout JSON | `intelligence.cli` args |
| Python → Rust | subprocess + stdout JSON | `ScanResult` / `risk` object |
| FastAPI → DB | SQLAlchemy | ORM entities |

---

## 5. Flow Trace

### Path 1: KYC operational (executed live)

```
1. node bin/kyc-cli.js customer-create  →  POST /customers  →  Customer row
2. node bin/kyc-cli.js submit-kyc       →  POST /kyc        →  PAN/bank verify, status=verified
3. (optional) POST /risk-score          →  Python RiskScoreService → factors.kyc_verified=true
```

**Live evidence:** `node-customer-create.txt`, `node-submit-kyc.txt` — customer `92343be3-7195-41fb-9266-2c2bbd8d6be3`, KYC verified.

### Path 2: Polyglot intelligence (executed live)

```
1. node bin/kyc-cli.js generate-report --path services/onboarding-api --output reports/
2. spawnSync: python -m intelligence.cli <path> -o <out> --json
3. analyzer.py → enrich_analysis_with_rust() → rust-analyzer scan --path ...
4. Writes: api-map.md, er-diagram.mmd, flow-tracing-report.md, analysis-manifest.json (with rust_scan)
```

**Live `rust_scan` excerpt:**

```json
{
  "file_count": 60,
  "graph_edges": 81,
  "risk": { "score": 55, "band": "medium" },
  "scan_duration_ms": 182
}
```

### Path 3: Rust standalone (executed live)

```bash
./target/release/rust-analyzer risk --path services/onboarding-api
# → score 55, band medium
```

---

## 6. Build & Startup Verification

| Component | Command | Result |
|-----------|---------|--------|
| Rust build | `cargo build --release` | **PASS** — Finished release profile |
| FastAPI startup | `uvicorn app.main:app --port 8113` | **PASS** — health after 3s |
| Node CLI | `node bin/kyc-cli.js customer-create ...` | **PASS** |
| Worker startup | N/A | **N/A** — no worker process in repo |

---

## 7. Integration Verification (executed)

| Step | Output |
|------|--------|
| `GET /health` | `{"status":"healthy","service":"onboarding-api","version":"0.1.0"}` |
| `customer-create` | `ok: true`, UUID returned |
| `submit-kyc` | `status: verified`, pan/bank verified |
| `rust-analyzer risk` | score 55, band medium |
| `generate-report` | 13 report files + `rust_scan` in manifest |

**Evidence log:** `a3-live-integration.log`

---

## 8. Test Results (executed 2026-06-20)

| Suite | Command | Result |
|-------|---------|--------|
| FastAPI | `make test-api` | **28 passed**, 98% coverage |
| Node | `make test-node` | **17 passed** |
| Rust | `make test-rust` | **10 passed** (8+2) |
| Intelligence | `make test-intelligence` | **18 passed** (rust bridge included) |
| Platform E2E | `make test-e2e` | **4 passed** |
| **Total** | `make test` equivalent | **77 tests, 0 failed** |

**E2E cases (`tests/e2e/test_platform_e2e.py`):**

| Test | Validates |
|------|-----------|
| `test_e2e_api_kyc_pipeline` | FastAPI full KYC + risk |
| `test_e2e_intelligence_analyzes_onboarding_api` | Python CLI on API tree |
| `test_e2e_rust_scan_onboarding_api` | Rust JSON scan |
| `test_e2e_node_cli_validators` | Node module load |

**Evidence:** `test-results.txt`

---

## 9. README Verification

| README | Run order documented? | Integration steps? | Gap |
|--------|----------------------|-------------------|-----|
| Root `README.md` | `make test`, Docker, CI | High-level only | No polyglot sequence |
| `services/onboarding-api/README.md` | uvicorn port 8000 | Endpoints table | Standalone |
| `clients/node-cli/README.md` | 3 commands + `API_BASE_URL` | CLI → API + generate-report | Calls Python, not Rust directly |
| `engines/rust-analyzer/README.md` | cargo build, scan/risk | Python auto-detect | Standalone |
| `engines/intelligence/README.md` | Python CLI | Rust bridge note | — |

**Finding:** Run order is **documented per component** but not as a single “start API → run CLI → build Rust → generate report” page. Root README `make test` covers verification orchestration.

---

## 10. Findings

| # | Finding | Severity | Notes |
|---|---------|----------|-------|
| F1 | Node is CLI, not worker | Info | No queue/file-worker; criterion wording “worker” maps to `kyc-cli` operator client |
| F2 | Two risk engines | Info | Python = customer KYC risk; Rust = repository static analysis |
| F3 | No FastAPI→Rust direct call | Info | Rust reached via Python bridge or standalone CLI |
| F4 | Polyglot E2E split across paths | Low | KYC path and intelligence path verified separately but both live |
| F5 | README fragmentation | Low | Acceptable for monorepo; root `make test` is integration entry |

---

## 11. Verification Summary

```bash
cd "/Users/shaikdadapeer/agent development"

# Build Rust
cd engines/rust-analyzer && cargo build --release && cd ../..

# All suites
make test-api test-node test-rust test-intelligence test-e2e

# Live polyglot (optional)
# Terminal 1: cd services/onboarding-api && PYTHONPATH=. .venv/bin/uvicorn app.main:app --port 8000
# Terminal 2: cd clients/node-cli && node bin/kyc-cli.js customer-create ...
# Terminal 2: node bin/kyc-cli.js generate-report --path ../../services/onboarding-api --output /tmp/reports
```

**A3 verdict: PASS** — FastAPI, Node CLI, and Rust analyzer form a verified polyglot mini-system with documented contracts, 77 passing tests, and live integration evidence for both HTTP KYC and Node→Python→Rust analysis paths.
