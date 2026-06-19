# B3 — Test Discovery & Execution Report

**Evaluation criterion:** B3 (Test Discovery)  
**Repository:** AI-Powered KYC & Onboarding Repository Intelligence Platform  
**Execution date:** 2026-06-19T07:32:05Z (UTC)  
**Evidence directory:** `evidence/test-results/b3-run-2026-06-19-1302/`

---

## Executive Summary

| Metric | Value |
|--------|------:|
| **Test suites executed** | **5** |
| **Total tests discovered** | **73** |
| **Tests passed** | **73** |
| **Tests failed** | **0** |
| **Tests skipped / cancelled** | **0** |
| **Errors blocking execution** | **0** |
| **Warnings (non-fatal)** | **1** (npm `devdir` config notice) |

All five platform test suites completed successfully. The repository uses **pytest** (Python), **Node.js built-in test runner** (`node --test`), and **cargo test** (Rust). No test classes are defined — Python and Rust use function-based tests; Node uses `describe`/`it` blocks.

**Unified runner:** `make test` → **5/5 suites PASS** (see `evidence/test-results/phase-7-summary.txt`).

**onboarding-api coverage:** **98%** line coverage (656 statements, 15 missed).

---

## Test Framework Details

### Python — pytest

| Component | Configuration | Location |
|-----------|---------------|----------|
| **onboarding-api** | `[tool.pytest.ini_options]` — `testpaths = ["tests"]`, `asyncio_mode = "auto"` | `services/onboarding-api/pyproject.toml:33-35` |
| **intelligence engine** | `[tool.pytest.ini_options]` — `testpaths = ["tests"]`, `pythonpath = ["src"]` | `engines/intelligence/pyproject.toml:26-28` |
| **platform E2E** | `[tool.pytest.ini_options]` — `testpaths = ["tests/e2e"]` | `pyproject.toml:11-13` (repo root) |
| **Fixtures** | In-memory SQLite, `TestClient`, dependency overrides | `services/onboarding-api/tests/conftest.py` |
| **Plugins (onboarding-api venv)** | `pytest-asyncio`, `pytest-cov`, `anyio` | Observed at runtime |
| **Coverage** | `--cov=app` / `--cov=intelligence` via `scripts/run-all-tests.sh` | `scripts/run-all-tests.sh` |

**Dev dependencies:** `pytest>=8.2.0`, `pytest-asyncio>=0.23.0`, `httpx`, `ruff` (onboarding-api); `pytest>=8.2.0` (intelligence).

### Node.js — native test runner

| Field | Value |
|-------|-------|
| **Runner** | `node --test` (Node ≥18) |
| **Script** | `"test": "node --test tests/*.test.js"` |
| **Config file** | `clients/node-cli/package.json:9-10` |
| **Pattern** | `describe()` / `it()` in `clients/node-cli/tests/*.test.js` |

### Rust — cargo test

| Field | Value |
|-------|-------|
| **Framework** | Built-in `#[test]` + integration tests |
| **Config** | `engines/rust-analyzer/Cargo.toml` |
| **Unit tests** | Inline `#[cfg(test)]` modules in `src/` |
| **Integration tests** | `engines/rust-analyzer/tests/integration_test.rs` |
| **Bench (not in test count)** | `benches/scan_benchmark.rs` (criterion, separate from `cargo test`) |

### CI integration

GitHub Actions workflow `.github/workflows/ci.yml` runs each suite in parallel jobs:

- `test-onboarding-api` — `PYTHONPATH=. pytest -q --cov=app ...`
- `test-intelligence` — `PYTHONPATH=src pytest -q --cov=intelligence ...`
- `test-node-cli` — `npm ci && npm test`
- `test-rust-analyzer` — `cargo test -q`
- `test-e2e` — `pytest -q ../../tests/e2e/test_platform_e2e.py`

### Unified local runner

| Command | Description |
|---------|-------------|
| `make test` | Runs all 5 suites via `scripts/run-all-tests.sh` |
| `make test-api` | onboarding-api only |
| `make test-intelligence` | intelligence only |
| `make test-node` | node-cli only |
| `make test-rust` | rust-analyzer only |
| `make test-e2e` | platform E2E only |

---

## Test File Inventory

### Suite 1 — onboarding-api (pytest) — 24 tests

| File | Test functions | Count |
|------|----------------|------:|
| `services/onboarding-api/tests/test_auth.py` | `test_health_public_without_key`, `test_protected_route_requires_key` | 2 |
| `services/onboarding-api/tests/test_customers.py` | `test_create_customer`, `test_create_customer_duplicate_email`, `test_create_customer_invalid_email`, `test_get_customer`, `test_get_customer_not_found` | 5 |
| `services/onboarding-api/tests/test_health.py` | `test_health`, `test_metrics` | 2 |
| `services/onboarding-api/tests/test_integration.py` | `test_full_kyc_onboarding_flow`, `test_health_and_metrics_available` | 2 |
| `services/onboarding-api/tests/test_kyc.py` | `test_submit_kyc_success`, `test_submit_kyc_invalid_pan`, `test_submit_kyc_rejected_pan`, `test_get_kyc_status`, `test_get_kyc_status_not_found` | 5 |
| `services/onboarding-api/tests/test_metrics.py` | `test_kyc_flow_exposes_domain_metrics` | 1 |
| `services/onboarding-api/tests/test_risk.py` | `test_risk_score_without_kyc`, `test_risk_score_after_kyc`, `test_risk_score_customer_not_found` | 3 |
| `services/onboarding-api/tests/test_verification.py` | `test_pan_verify_success`, `test_pan_verify_invalid_format`, `test_bank_verify_success`, `test_bank_verify_invalid_account` | 4 |
| **Support** | `services/onboarding-api/tests/conftest.py` (fixtures, not tests) | — |

**Test classes:** None (function-based pytest).

---

### Suite 2 — intelligence engine (pytest) — 18 tests

| File | Test functions | Count |
|------|----------------|------:|
| `engines/intelligence/tests/test_analyzer.py` | 4 tests | 4 |
| `engines/intelligence/tests/test_detectors.py` | 4 tests | 4 |
| `engines/intelligence/tests/test_flow_tracing.py` | 6 tests | 6 |
| `engines/intelligence/tests/test_generators.py` | 2 tests | 2 |
| `engines/intelligence/tests/test_rust_bridge.py` | 2 tests | 2 |

**Test classes:** None.

---

### Suite 3 — node-cli (node --test) — 17 tests

| File | describe blocks | it() tests | Count |
|------|-----------------|------------|------:|
| `clients/node-cli/tests/api-client.test.js` | ApiClient | 3 | 3 |
| `clients/node-cli/tests/commands.test.js` | commands | 4 | 4 |
| `clients/node-cli/tests/generate-report.test.js` | generate-report command | 1 | 1 |
| `clients/node-cli/tests/validators.test.js` | validators | 9 | 9 |

**Not executed by `npm test`:** `engines/intelligence/tests/fixtures/node/tests/users.test.js` — fixture sample only, not part of platform test runner.

---

### Suite 4 — rust-analyzer (cargo test) — 10 tests

| Location | Test name | Type |
|----------|-----------|------|
| `src/file_walker.rs` | `rejects_missing_path`, `skips_node_modules` | Unit |
| `src/graph/mod.rs` | `builds_edges_between_files` | Unit |
| `src/parser/python.rs` | `extracts_python_imports_and_classes` | Unit |
| `src/parser/universal.rs` | `parses_javascript_requires` | Unit |
| `src/risk/mod.rs` | `band_mapping`, `low_test_ratio_increases_score` | Unit |
| `src/scan.rs` | `scans_temp_repo` | Unit |
| `tests/integration_test.rs` | `cli_rejects_invalid_path`, `cli_scan_onboarding_api` | Integration |

**Unit tests:** 8 | **Integration tests:** 2 | **Doc tests:** 0

---

### Suite 5 — platform E2E (pytest) — 4 tests

| File | Test functions | Count |
|------|----------------|------:|
| `tests/e2e/test_platform_e2e.py` | `test_e2e_api_kyc_pipeline`, `test_e2e_intelligence_analyzes_onboarding_api`, `test_e2e_rust_scan_onboarding_api`, `test_e2e_node_cli_validators` | 4 |

Cross-stack tests: FastAPI in-process, intelligence analyzer, Rust CLI scan, Node validators.

---

### Grand total

| Suite | Framework | Tests |
|-------|-----------|------:|
| onboarding-api | pytest | 24 |
| intelligence | pytest | 18 |
| node-cli | node --test | 17 |
| rust-analyzer | cargo test | 10 |
| platform E2E | pytest | 4 |
| **Total** | | **73** |

---

## Execution Commands

### Recommended — all suites

```bash
# From repository root
make test
```

Equivalent manual commands:

```bash
# 1. onboarding-api (24 tests, with coverage)
cd services/onboarding-api
PYTHONPATH=. .venv/bin/pytest -v --cov=app --cov-report=term-missing

# 2. intelligence (18 tests)
cd engines/intelligence
PYTHONPATH=src .venv/bin/pytest -v

# 3. node-cli (17 tests)
cd clients/node-cli
npm test

# 4. rust-analyzer (10 tests)
cd engines/rust-analyzer
cargo test

# 5. platform E2E (4 tests)
cd services/onboarding-api
PYTHONPATH=. .venv/bin/pytest -v ../../tests/e2e/test_platform_e2e.py
```

### Discovery-only (collect without running)

```bash
cd services/onboarding-api && PYTHONPATH=. .venv/bin/pytest --collect-only -q
cd engines/intelligence && PYTHONPATH=src .venv/bin/pytest --collect-only -q
cd services/onboarding-api && PYTHONPATH=. .venv/bin/pytest --collect-only -q ../../tests/e2e/
# Node/Rust: no separate collect; use npm test / cargo test -- --list (optional)
```

---

## Actual Command Results

**Run timestamp:** 2026-06-19T07:32:05Z  
**Raw logs:** `evidence/test-results/b3-run-2026-06-19-1302/`

### Suite 1 — onboarding-api

```
24 tests collected in 0.01s
...
============================== 24 passed in 0.69s ==============================
TOTAL ... 656 statements, 15 missed — 98% coverage
EXIT:0
```

### Suite 2 — intelligence

```
18 tests collected in 0.15s
...
============================== 18 passed in 1.22s ==============================
EXIT:0
```

### Suite 3 — node-cli

```
ℹ tests 17
ℹ suites 4
ℹ pass 17
ℹ fail 0
ℹ skipped 0
ℹ duration_ms 607.945208
EXIT:0
```

**Warning (non-fatal):**
```
npm warn Unknown env config "devdir". This will stop working in the next major version of npm.
```
This is an npm configuration notice in the local environment; it did not affect test execution.

### Suite 4 — rust-analyzer

```
running 8 tests ... test result: ok. 8 passed; 0 failed
running 2 tests ... test result: ok. 2 passed; 0 failed  (integration_test.rs)
Doc-tests: 0 tests
EXIT:0
```

### Suite 5 — platform E2E

```
4 tests collected in 0.25s
...
============================== 4 passed in 1.18s ===============================
EXIT:0
```

### Unified runner — `make test`

```
Platform Test Run — 2026-06-19T07:33:xxZ
  ✅ PASS: onboarding-api pytest + coverage
  ✅ PASS: intelligence pytest + coverage
  ✅ PASS: node-cli tests
  ✅ PASS: rust-analyzer cargo test
  ✅ PASS: platform e2e tests
TOTAL: 5 passed, 0 failed
```

---

## Failure Analysis

**Failures:** None.

All 73 tests passed on the execution date above. No root-cause analysis required for test failures.

**Observations (informational, not failures):**

| Item | Severity | Notes |
|------|----------|-------|
| npm `devdir` warning | Low | Environment-specific npm config; tests still pass |
| onboarding-api 98% coverage | Info | 15 uncovered lines in exceptions, models, repositories, schemas — not test gaps causing failures |
| Fixture test file not in CI | Info | `engines/intelligence/tests/fixtures/node/tests/users.test.js` is sample data for analyzer detection, not run by `make test` |
| E2E overlap | Info | E2E tests exercise overlapping components (API, intelligence, Rust, Node) but are distinct test cases counted separately |

---

## Verification Summary

| Check | Command | Expected | Actual |
|-------|---------|----------|--------|
| B3 verify (evaluation index) | `make test` | All suites pass | ✅ 5/5 suites, 73/73 tests |
| onboarding-api count | `pytest --collect-only -q` | 24 | ✅ 24 |
| intelligence count | `pytest --collect-only -q` | 18 | ✅ 18 |
| node-cli count | `npm test` | 17 pass | ✅ 17 pass |
| rust count | `cargo test` | 10 pass | ✅ 10 pass |
| E2E count | `pytest --collect-only -q tests/e2e/` | 4 | ✅ 4 |
| Evidence artifacts | `evidence/test-results/b3-run-2026-06-19-1302/` | Logs present | ✅ 10 log files |

### B3 criterion status

| Field | Value |
|-------|-------|
| **Status** | **PASS** |
| **Score** | 9/10 |
| **Completion** | 100% (discovery + execution verified) |
| **Risk** | Low |
| **Evidence** | This report + `evidence/test-results/b3-run-2026-06-19-1302/` + `evidence/test-results/phase-7-summary.txt` |
| **Missing** | Rust coverage in CI (`cargo-llvm-cov` optional) |
| **Verify** | `make test` |

---

## Related Artifacts

| Path | Purpose |
|------|---------|
| `scripts/run-all-tests.sh` | Unified 5-suite runner |
| `Makefile` | `make test`, per-suite targets |
| `.github/workflows/ci.yml` | Remote CI test jobs |
| `evidence/test-results/onboarding-api-coverage.xml` | Coverage XML (updated by `make test`) |
| `evidence/test-results/intelligence-coverage.xml` | Coverage XML |
| `evidence/test-results/phase-7-summary.txt` | Latest unified run summary |
