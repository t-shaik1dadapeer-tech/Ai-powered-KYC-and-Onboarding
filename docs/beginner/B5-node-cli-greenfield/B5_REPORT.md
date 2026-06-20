# B5 — Node.js Greenfield API/CLI Verification

**Evaluation criterion:** B5 (Node.js Greenfield)  
**Application:** `clients/node-cli/` (`kyc-cli`)  
**Verification date:** 2026-06-20T04:53:03Z (UTC)  
**Evidence:** `evidence/test-results/b5-run-2026-06-20-1022/`  
**Machine-readable:** `cli-commands.csv`, `structure-inventory.csv`

---

## 1. Executive Summary

| Check | Result | Confidence |
|-------|--------|------------|
| Application type identified | **CLI + HTTP client** (hybrid) | Confirmed |
| Layered structure (commands → lib) | **PASS** | Confirmed |
| CLI starts and parses commands | **PASS** | Confirmed |
| Client-side validation before API calls | **PASS** | Confirmed |
| Live API integration (customer + KYC) | **PASS** | Confirmed |
| API error propagation (409 conflict) | **PASS** | Confirmed |
| Intelligence engine subprocess (`generate-report`) | **PASS** | Confirmed |
| Test suite | **17/17 PASS** | Confirmed |
| Syntax lint (`node --check`) | **PASS** | Confirmed |
| README with install/run/test | **PASS** | Confirmed |
| Production gaps | No API key header support, no retry/timeout | Noted |

**Overall B5 status: PASS (10/10)** — well-structured Node.js CLI with validation, tests, and live backend verification.

---

## 2. Project Structure

```
clients/node-cli/
├── bin/
│   └── kyc-cli.js              # Entry point (commander)
├── commands/
│   ├── customer-create.js      # Command handler
│   ├── submit-kyc.js           # Command handler
│   └── generate-report.js      # Command handler
├── lib/
│   ├── api-client.js           # HTTP client (outbound REST)
│   ├── analyzer-client.js      # Python subprocess wrapper
│   ├── validators.js           # Input validation
│   └── errors.js               # CliError hierarchy
├── tests/
│   ├── api-client.test.js      # 3 tests
│   ├── commands.test.js        # 4 tests
│   ├── validators.test.js      # 9 tests
│   └── generate-report.test.js # 1 integration test
├── package.json
├── Dockerfile
└── README.md
```

**Layer mapping:**

| Layer | Present | Location |
|-------|---------|----------|
| Controllers | No (CLI, not HTTP server) | — |
| Routes | No | — |
| Commands (handlers) | Yes | `commands/` |
| Services | Implicit in `lib/` | `api-client.js`, `analyzer-client.js` |
| Models | No local persistence | API DTOs only |
| Repositories/DAOs | No | — |
| Middleware | No | — |
| Validators | Yes | `lib/validators.js` |
| Configuration | Yes | `package.json`, env `API_BASE_URL` |
| Utilities | Yes | `lib/errors.js` |

**Source file count:** 12 JavaScript files (4 lib · 3 commands · 1 bin · 4 tests)

---

## 3. Application Discovery

### Application classification

| Type | Applicable | Evidence |
|------|------------|----------|
| REST API (listening server) | **No** | No `http.createServer` or Express/Fastify |
| GraphQL API | **No** | No GraphQL dependencies or schema |
| CLI Application | **Yes** | `bin/kyc-cli.js`, commander |
| Worker/Background Service | **No** | One-shot commands only |
| Hybrid | **Yes** | CLI + outbound REST client + Python subprocess |

### Entry points

| Item | Value | File |
|------|-------|------|
| **CLI binary** | `kyc-cli` | `bin/kyc-cli.js` |
| **npm bin mapping** | `./bin/kyc-cli.js` | `package.json:5-7` |
| **Programmatic export** | `ApiClient` | `package.json:8` (`main`) |
| **Docker entrypoint** | `node bin/kyc-cli.js` | `Dockerfile:14` |

### Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `commander` | ^12.1.0 | CLI argument parsing |
| Node.js | ≥18.0.0 | Native `fetch`, `node:test` |

**Runtime (generate-report only):** Python 3.9+ with `engines/intelligence` venv or system `python3`.

---

## 4. CLI Command Inventory

| Command | Required flags | Optional flags | Backend |
|---------|----------------|----------------|---------|
| `customer-create` | `--name`, `--email`, `--phone` | `--api-url` (default `http://localhost:8000`) | `POST /customers` |
| `submit-kyc` | `--customer-id`, `--pan`, `--account`, `--ifsc` | `--api-url` | `POST /kyc` |
| `generate-report` | `--path` | `--output` (default `reports`), `--python` (default `python3`) | `python3 -m intelligence.cli` |

### Outbound API methods (`ApiClient`)

| Method | HTTP | Path | Request body fields |
|--------|------|------|---------------------|
| `createCustomer` | POST | `/customers` | `full_name`, `email`, `phone` |
| `submitKyc` | POST | `/kyc` | `customer_id`, `pan`, `account_number`, `ifsc` |
| `getHealth` | GET | `/health` | — |

**Authentication:** CLI sends `Content-Type: application/json` only. No `X-API-Key` header — works when API auth is disabled (default dev mode).

### Output contract

Success (stdout):

```json
{ "ok": true, "customerId": "...", "status": "...", ... }
```

Failure (stderr, exit 1):

```json
{ "ok": false, "error": "validation_error|api_error|...", "message": "...", "statusCode": 409 }
```

---

## 5. Validation Analysis

All validation runs **client-side** in `lib/validators.js` before network or subprocess calls.

| Field | Rule | Normalization | Error message |
|-------|------|---------------|---------------|
| PAN | `^[A-Z]{5}[0-9]{4}[A-Z]$` | Uppercase, trim | Invalid PAN format. Expected ABCDE1234F |
| IFSC | `^[A-Z]{4}0[A-Z0-9]{6}$` | Uppercase, trim | Invalid IFSC format |
| Account | 9–18 digits | Strip spaces | Account number must be 9-18 digits |
| Email | Basic `@` pattern | Trim | Invalid email address |
| Phone | 10–20 digits, optional `+` | Trim | Invalid phone number |
| Full name | 2–255 chars | Trim | Full name must be 2-255 characters |
| Customer ID | UUID v4 pattern | Trim | Customer ID must be a valid UUID |
| Repo path | Directory exists | `path.resolve` | Repository path does not exist |

**Commander** enforces required options at parse time (missing `--name` etc. prints help and exits).

**Verified live:**

```bash
node bin/kyc-cli.js customer-create --name "Jane Doe" --email "bad" --phone "9876543210"
# → {"ok":false,"error":"validation_error","message":"Invalid email address"}

node bin/kyc-cli.js submit-kyc --customer-id "550e8400-..." --pan "BAD" --account "123456789012" --ifsc "HDFC0001234"
# → {"ok":false,"error":"validation_error","message":"Invalid PAN format. Expected ABCDE1234F"}
```

---

## 6. Startup Verification

### Commands executed

```bash
cd clients/node-cli
node --version          # v26.3.0
npm install             # 2 packages, 0 vulnerabilities
npm run lint            # node --check — exit 0
node bin/kyc-cli.js --help
node bin/kyc-cli.js --version   # 0.1.0
```

### Startup result

| Step | Result |
|------|--------|
| `npm install` | **PASS** — commander installed |
| `node --check` lint | **PASS** — all JS files syntactically valid |
| CLI `--help` | **PASS** — 3 commands listed |
| CLI `--version` | **PASS** — `0.1.0` |

**Evidence:** `evidence/test-results/b5-run-2026-06-20-1022/cli-help.txt`, `cli-version.txt`, `execution.log`

---

## 7. Functional Verification

**API target:** `http://127.0.0.1:8101` (Docker stack per `infra/docker/.env`)

### 7.1 customer-create (success)

```bash
node bin/kyc-cli.js customer-create \
  --name "B5 Test User" \
  --email "b5-cli-1781931182@example.com" \
  --phone "9876543210" \
  --api-url http://127.0.0.1:8101
```

**Result:** `ok: true`, `status: pending`, `customerId: 2ae95ffc-d06b-4f30-8b34-e41d7ac598b0`

### 7.2 submit-kyc (success)

```bash
node bin/kyc-cli.js submit-kyc \
  --customer-id "2ae95ffc-d06b-4f30-8b34-e41d7ac598b0" \
  --pan "ABCDE1234F" --account "123456789012" --ifsc "HDFC0001234" \
  --api-url http://127.0.0.1:8101
```

**Result:** `ok: true`, `status: verified`, `panStatus: verified`, `bankStatus: verified`

### 7.3 Duplicate email (API error handling)

```bash
# Same email as 7.1
```

**Result:** `ok: false`, `error: conflict`, `statusCode: 409`, message contains "already exists"

### 7.4 generate-report (subprocess)

```bash
node bin/kyc-cli.js generate-report \
  --path "../../services/onboarding-api" \
  --output "evidence/test-results/b5-run-2026-06-20-1022/report-output"
```

**Result:** `ok: true`, `summary.framework: fastapi`, `summary.apis: 9`, reports written to output dir

**Evidence:** `customer-create.json`, `submit-kyc.json`, `duplicate-email.json`, `generate-report.json`, `api-flow.txt`

---

## 8. Test Discovery and Execution

### Framework

| Framework | Version | Config |
|-----------|---------|--------|
| Node.js built-in `node:test` | Native (Node 18+) | `package.json` scripts.test |

No Jest, Mocha, or Vitest.

### Test inventory

| File | Suite | Tests | Coverage area |
|------|-------|-------|---------------|
| `tests/validators.test.js` | validators | 9 | PAN, IFSC, account, email, phone, name, UUID |
| `tests/api-client.test.js` | ApiClient | 3 | POST success, HTTP error, network error |
| `tests/commands.test.js` | commands | 4 | Validation gate, API payload mapping |
| `tests/generate-report.test.js` | generate-report | 1 | Live Python analyzer on onboarding-api |

### Execution

```bash
cd clients/node-cli && npm test
```

**Result:**

```
ℹ tests 17
ℹ suites 4
ℹ pass 17
ℹ fail 0
ℹ duration_ms 860.060166
```

**Evidence:** `evidence/test-results/b5-run-2026-06-20-1022/pytest.txt`

---

## 9. Documentation Verification

| Section | README | Status |
|---------|--------|--------|
| Requirements (Node 18+, Python for report) | Lines 5–8 | **PASS** |
| Install (`npm install`, chmod) | Lines 10–16 | **PASS** |
| Command examples (all 3) | Lines 18–46 | **PASS** |
| Environment (`API_BASE_URL`) | Lines 48–52 | **PASS** |
| Test instructions (`npm test`) | Lines 54–60 | **PASS** |
| Architecture overview | Lines 62–67 | **PASS** |

**Gap:** README default API URL is `localhost:8000`; Docker stack uses port `8101` — documented in repo root/Makefile but not in node-cli README.

---

## 10. Code Quality Assessment

| Area | Assessment | Confidence |
|------|------------|------------|
| **Architecture** | Clear separation: bin → commands → lib; no business logic in CLI shell | High |
| **Error handling** | Typed errors (`ValidationError`, `ApiError`, `AnalyzerError`); JSON error output; exit code 1 | High |
| **Validation** | Validates all user inputs before I/O; normalizes PAN/IFSC case | High |
| **Maintainability** | Small modules, single dependency, no build step | High |
| **Testability** | `fetch` injectable in `ApiClient`; mocks in unit tests | High |
| **Security** | No secrets in repo; no shell injection (spawnSync with arg array); HTTPS not enforced | Medium |
| **Gaps** | No API key header when auth enabled; no request timeout; no retry on network failure | Noted |

### Error class hierarchy

```1:32:clients/node-cli/lib/errors.js
class CliError extends Error { ... }
class ValidationError extends CliError { ... }
class ApiError extends CliError { statusCode ... }
class AnalyzerError extends CliError { exitCode ... }
```

---

## 11. Findings and Recommendations

### Strengths

1. **Hybrid CLI** cleanly wraps REST API and Python analyzer without duplicating business rules.
2. **Client-side validation** prevents invalid API calls and gives fast feedback.
3. **Structured JSON I/O** suitable for scripting and CI pipelines.
4. **Zero test dependencies** — uses Node built-in runner.
5. **Docker image** ready for containerized operator workflows.

### Missing / incomplete

| Item | Severity | Recommendation |
|------|----------|----------------|
| No `X-API-Key` support | Medium | Add `--api-key` / `API_KEY` env when API auth enabled |
| No HTTP timeout | Low | Add `AbortSignal.timeout()` on fetch |
| README port mismatch (8000 vs 8101) | Low | Note Docker port in README |
| `getHealth` unused by CLI commands | Info | Add `health` subcommand for ops |
| No E2E test against live API in CI | Low | Optional smoke test with testcontainers |

### Bugs

None identified during this verification run.

### Production risks

| Risk | Mitigation |
|------|------------|
| API unreachable → opaque network error | Document `API_BASE_URL`; consider retry |
| Python venv not found for `generate-report` | `findPython()` falls back to `python3`; README documents requirement |
| Large repo scan may be slow | Expected; subprocess is synchronous |

---

## 12. Areas Requiring Manual Verification

| Area | Reason |
|------|--------|
| CLI with `API_KEY` set on server | Auth middleware not exercised by CLI today |
| Docker image `docker build && docker run` | Dockerfile present; not executed in this run |
| npm global install (`npm link`) | Bin mapping exists; not tested |
| Windows path handling for `generate-report` | Verified on macOS only |

---

## 13. Verification Summary

| # | Verification step | Command / action | Result |
|---|-------------------|------------------|--------|
| 1 | Install dependencies | `npm install` | PASS |
| 2 | Syntax check | `npm run lint` | PASS |
| 3 | Unit + integration tests | `npm test` | **17/17 PASS** |
| 4 | CLI help / version | `node bin/kyc-cli.js --help` | PASS |
| 5 | Validation errors | bad email, bad PAN | PASS (exit 1, JSON error) |
| 6 | Live customer-create | against `:8101` | PASS (201 pending) |
| 7 | Live submit-kyc | against `:8101` | PASS (verified) |
| 8 | API conflict handling | duplicate email | PASS (409) |
| 9 | generate-report | Python analyzer | PASS (fastapi, 9 APIs) |
| 10 | README completeness | manual review | PASS (minor port note) |

**B5 verdict: PASS** — Node.js greenfield CLI is implemented, executable, tested, documented, and functionally verified against the live onboarding API.

---

*Generated from repository source and executed commands. Evidence directory: `evidence/test-results/b5-run-2026-06-20-1022/`.*
