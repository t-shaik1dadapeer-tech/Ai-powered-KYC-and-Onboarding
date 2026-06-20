# I4 — Polyglot Service Pair Verification

**Evaluation criterion:** I4 (Polyglot Service Pair)  
**Pair:** FastAPI `services/onboarding-api/` + Node.js `clients/node-cli/`  
**Verification date:** 2026-06-20T05:34:23Z (UTC)  
**Evidence:** `evidence/test-results/i4-run-2026-06-20-1103/`  
**Machine-readable:** `endpoints.csv`

---

## 1. Executive Summary

| Check | Result | Confidence |
|-------|--------|------------|
| FastAPI service present | **PASS** — `app/main.py`, 9 business endpoints | High |
| Node.js HTTP client present | **PASS** — `lib/api-client.js`, 3 CLI commands | High |
| Live API startup | **PASS** — uvicorn on `:8112` | High — executed |
| Live CLI → API communication | **PASS** — customer-create + submit-kyc | High — executed |
| Client validation (pre-HTTP) | **PASS** — bad email rejected locally | High |
| API error propagation | **PASS** — 409 duplicate email via curl | High |
| FastAPI tests | **26/26 PASS** | High |
| Node.js tests | **17/17 PASS** | High |
| Platform E2E | **4/4 PASS** | High |
| Two-terminal README workflow | **PARTIAL** — split across two READMEs | Medium |

**Overall I4 status: PASS (9/10)** — polyglot pair verified with live HTTP and full test suites.

---

## 2. System Architecture Overview

```
┌─────────────────────┐         HTTP/JSON          ┌──────────────────────────┐
│  clients/node-cli   │  POST /customers, /kyc     │  services/onboarding-api │
│  (Node.js 18+)      │ ─────────────────────────► │  (FastAPI + SQLAlchemy)  │
│  lib/api-client.js  │ ◄───────────────────────── │  :8000 default           │
└─────────────────────┘         JSON responses     └──────────────────────────┘
```

| Component | Role | Technology |
|-----------|------|------------|
| **Server** | KYC REST API, persistence, validation | FastAPI, Pydantic, SQLAlchemy |
| **Client** | Operator CLI, outbound HTTP | Node.js, commander, native `fetch` |

**Source:** `docs/architecture.md` — Operator / CLI → FastAPI

---

## 3. FastAPI Service Analysis

### Entry point

| Item | Value | File |
|------|-------|------|
| ASGI app | `app` | `app/main.py:68` |
| Factory | `create_app()` | `app/main.py:47-65` |
| Startup | `uvicorn app.main:app` | `README.md:17` |

### Layers

| Layer | Path | Count |
|-------|------|-------|
| Routers | `app/routers/` | 6 modules |
| Services | `app/services/` | 6 modules |
| Repositories | `app/repositories/` | 3 modules |
| Models | `app/models/` | 5 entities |
| Schemas | `app/schemas/` | Pydantic DTOs |

### Configuration

| Setting | Default | File |
|---------|---------|------|
| `database_url` | `sqlite:///./onboarding.db` | `app/core/config.py:13` |
| `api_key` | empty (auth off) | `app/core/config.py:16` |
| `app_version` | `0.1.0` | `app/core/config.py:10` |

### Live startup (executed)

```bash
cd services/onboarding-api
DATABASE_URL="sqlite:////tmp/i4-onboarding.db" PYTHONPATH=. .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8112
```

**Log excerpt:** `Application startup complete. Uvicorn running on http://127.0.0.1:8112`  
**Health:** `{"status":"healthy","service":"onboarding-api","version":"0.1.0"}`

---

## 4. Node.js Client Analysis

### Entry point

| Item | Value | File |
|------|-------|------|
| CLI binary | `bin/kyc-cli.js` | `package.json` bin |
| HTTP client | `ApiClient` | `lib/api-client.js` |
| Validators | `lib/validators.js` | PAN, IFSC, email, UUID |

### API-facing commands

| Command | HTTP call | File |
|---------|-----------|------|
| `customer-create` | `POST /customers` | `commands/customer-create.js` |
| `submit-kyc` | `POST /kyc` | `commands/submit-kyc.js` |
| `generate-report` | Python subprocess (not HTTP) | `commands/generate-report.js` |

### Configuration

| Variable | Default | Purpose |
|----------|---------|---------|
| `API_BASE_URL` | `http://localhost:8000` | API base URL |
| `--api-url` | overrides per command | `bin/kyc-cli.js` |

### Client execution (executed)

```bash
node bin/kyc-cli.js customer-create --name "I4 User" --email "i4-cli-...@example.com" \
  --phone "9876543210" --api-url http://127.0.0.1:8112
node bin/kyc-cli.js submit-kyc --customer-id "<UUID>" --pan "ABCDE1234F" \
  --account "123456789012" --ifsc "HDFC0001234" --api-url http://127.0.0.1:8112
```

**Result:** `ok: true`, KYC `status: verified`

---

## 5. Endpoint Inventory

| Method | Path | Request | Response | CLI uses |
|--------|------|---------|----------|----------|
| POST | `/customers` | `CustomerCreate` | `CustomerResponse` 201 | **Yes** |
| GET | `/customer/{id}` | path UUID | `CustomerResponse` 200 | No |
| POST | `/kyc` | `KycSubmitRequest` | `KycStatusResponse` 201 | **Yes** |
| GET | `/kyc-status/{id}` | path UUID | `KycStatusResponse` 200 | No |
| POST | `/pan-verify` | `PanVerifyRequest` | 200 | No |
| POST | `/bank-verify` | `BankVerifyRequest` | 200 | No |
| POST | `/risk-score` | `RiskScoreRequest` | 200 | No |
| GET | `/health` | — | JSON 200 | No (`getHealth` in client, unused by CLI) |
| GET | `/metrics` | — | Prometheus 200 | No |

**OpenAPI:** `docs/api/openapi.json` (9 paths)  
**CSV:** `endpoints.csv`

---

## 6. End-to-End Communication Verification

### Flow: Node CLI → FastAPI (live)

| Step | Actor | Action | Result |
|------|-------|--------|--------|
| 1 | uvicorn | Start API | Healthy |
| 2 | CLI | `customer-create` → `POST /customers` | 201, `customerId` returned |
| 3 | CLI | `submit-kyc` → `POST /kyc` | 201, `status: verified` |
| 4 | CLI | bad email (local validation) | `validation_error`, no HTTP |
| 5 | curl | duplicate email | HTTP 409 conflict |

### Request/response mapping (verified)

**CLI `createCustomer`** sends:

```json
{"full_name": "...", "email": "...", "phone": "..."}
```

Maps to `CustomerCreate` — `api-client.js:9-14`

**CLI `submitKyc`** sends:

```json
{"customer_id": "...", "pan": "...", "account_number": "...", "ifsc": "..."}
```

Maps to `KycSubmitRequest` — `api-client.js:17-23`

### Error handling

| Layer | Behavior | Evidence |
|-------|----------|----------|
| CLI validators | Reject before fetch | `validation-error.json` |
| API Pydantic | 422 on invalid body | unit tests |
| API business | 409 conflict JSON `{error:{code,message}}` | `duplicate-email.txt` |
| CLI ApiClient | Parses `error.message`, sets `statusCode` | `api-client.js:57-64` |

**Evidence:** `customer-create.json`, `submit-kyc.json`, `health.json`

---

## 7. Input Validation Analysis

### FastAPI (server)

| Field | Rules | File |
|-------|-------|------|
| `email` | EmailStr + lowercase normalize (I3) | `schemas/customer.py` |
| `pan` | PAN regex | `schemas/kyc.py` |
| `ifsc` | IFSC regex | `schemas/kyc.py` |
| `account_number` | 9–18 digits | `schemas/kyc.py` |

### Node.js (client, before HTTP)

| Field | Rules | File |
|-------|-------|------|
| `email` | Basic pattern | `lib/validators.js` |
| `pan` / `ifsc` | Same patterns as API | `lib/validators.js` |
| `phone` | 10–20 digits | `lib/validators.js` |

**Note:** Dual validation — CLI catches errors early; API remains authoritative.

---

## 8. Test Discovery and Execution

### FastAPI

| Item | Value |
|------|-------|
| Framework | pytest |
| Location | `services/onboarding-api/tests/` |
| Command | `cd services/onboarding-api && PYTHONPATH=. .venv/bin/pytest -q` |
| Result | **26/26 PASS** (1.38s) |

### Node.js

| Item | Value |
|------|-------|
| Framework | `node:test` |
| Location | `clients/node-cli/tests/` |
| Command | `cd clients/node-cli && npm test` |
| Result | **17/17 PASS** (1137ms) |

### Platform E2E (polyglot simulation)

| Test | Purpose | Result |
|------|---------|--------|
| `test_e2e_api_kyc_pipeline` | Full API pipeline (in-process TestClient) | PASS |
| `test_e2e_node_cli_validators` | Node validators load | PASS |

```bash
PYTHONPATH=. services/onboarding-api/.venv/bin/pytest tests/e2e/test_platform_e2e.py -v
# 4 passed in 6.02s
```

**Evidence:** `platform-e2e.txt`, `onboarding-api-pytest.txt`, `node-cli-test.txt`

---

## 9. README Verification

### `services/onboarding-api/README.md`

| Section | Present |
|---------|---------|
| Setup (venv, pip) | ✅ |
| Run (`uvicorn ... --port 8000`) | ✅ |
| Test (`pytest`) | ✅ |
| Endpoint table | ✅ |

### `clients/node-cli/README.md`

| Section | Present |
|---------|---------|
| Install (`npm install`) | ✅ |
| `customer-create` with `--api-url` | ✅ |
| `submit-kyc` | ✅ |
| `API_BASE_URL` env | ✅ |
| Test (`npm test`) | ✅ |

### Two-terminal workflow

**Documented implicitly** across both READMEs (not a single combined section in root README):

**Terminal 1 — API:**
```bash
cd services/onboarding-api
PYTHONPATH=. .venv/bin/uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — CLI:**
```bash
cd clients/node-cli
node bin/kyc-cli.js customer-create --name "Jane" --email "jane@example.com" --phone "9876543210"
node bin/kyc-cli.js submit-kyc --customer-id "<UUID>" --pan "ABCDE1234F" --account "123456789012" --ifsc "HDFC0001234"
```

**Gap:** Root `README.md` focuses on `make test` / Docker; no explicit two-terminal polyglot section.

---

## 10. Findings and Recommendations

### Strengths

1. Clean separation — CLI is HTTP client only; business logic stays in FastAPI.
2. Field names correctly mapped (`full_name`, `account_number`, etc.).
3. Live polyglot flow verified end-to-end.
4. Platform E2E test simulates CLI payloads through API.

### Gaps

| Gap | Severity | Recommendation |
|-----|----------|----------------|
| No combined two-terminal doc in root README | Low | Add `docs/polyglot-quickstart.md` |
| CLI has no `getHealth` command | Info | Optional ops command |
| No API key in CLI when auth enabled | Medium | `--api-key` flag |
| `getHealth` in ApiClient unused | Info | Wire to health command |
| Docker port 8101 vs README 8000 | Low | Cross-reference `infra/docker/.env` |

### Production risks

| Risk | Mitigation |
|------|------------|
| Network failure between CLI and API | `ApiError` with `network_error` code |
| Auth enabled breaks CLI | Document `API_KEY` requirement |

---

## 11. Areas Requiring Manual Verification

| Area | Reason |
|------|--------|
| CLI with `API_KEY` set on server | Auth not exercised in live I4 run |
| Docker Compose pair (api + cli containers) | Separate containers; not run together |
| TLS/HTTPS | Local HTTP only |

---

## 12. Verification Summary

| # | Step | Command | Result |
|---|------|---------|--------|
| 1 | Start FastAPI | `uvicorn app.main:app --port 8112` | PASS |
| 2 | Health check | `curl /health` | PASS |
| 3 | CLI customer-create | `node bin/kyc-cli.js customer-create ...` | PASS |
| 4 | CLI submit-kyc | `node bin/kyc-cli.js submit-kyc ...` | PASS |
| 5 | Validation error | bad email | PASS (CLI local) |
| 6 | API conflict | duplicate email curl | PASS (409) |
| 7 | Platform E2E | `pytest tests/e2e/test_platform_e2e.py` | **4/4 PASS** |
| 8 | FastAPI suite | `pytest -q` | **26/26 PASS** |
| 9 | Node suite | `npm test` | **17/17 PASS** |

**I4 verdict: PASS**

---

*Evidence: `evidence/test-results/i4-run-2026-06-20-1103/`*
