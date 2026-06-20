# I6 — Bug Diagnosis with Agent Verification

**Evaluation criterion:** I6 (Bug Diagnosis)  
**Bug ID:** BUG-001 — Integration tests hit persistent SQLite DB  
**Verification date:** 2026-06-20T05:42:30Z (UTC)  
**Evidence:** `evidence/test-results/i6-run-2026-06-20-1112/`  
**Reference:** `docs/bug-investigation.md`

---

## 1. Executive Summary

| Item | Result | Confidence |
|------|--------|------------|
| Bug selected | **BUG-001** — flaky 409 on test re-runs | High |
| Reproduced | **YES** — 201 then 409 without DB override | High — executed |
| Root cause | `TestClient(app)` used default `onboarding.db` | High — verified |
| Fix status | **In place** (`conftest.py` in-memory override) | High |
| I6 addition | Regression tests `test_bug001_regression.py` | High |
| Double pytest run | **4/4 PASS** × 2 | High |
| Full API suite | **28/28 PASS** | High |
| Platform E2E | **1/1 PASS** | High |

**Overall I6 status: PASS** — bug reproduced, root cause documented, fix verified, regression guard added.

---

## 2. Bug Description

**Symptom:** Running integration/E2E tests a second time failed with `assert 409 == 201` when creating customer `integration@example.com`.

**Impact:** CI flakiness, false failures, blocked Phase 9 gate, developer confusion when local `onboarding.db` persisted state.

**Severity:** Medium (test infrastructure, not production API logic).

---

## 3. Reproduction Steps

### Buggy path (no `get_db` override)

1. Set `DATABASE_URL=sqlite:////tmp/bug001-repro.db` (persistent file).
2. `TestClient(app)` without dependency override.
3. `POST /customers` with `email=integration@example.com` → **201**.
4. New `TestClient(app)` session, same POST → **409 Conflict**.

### Fixed path (pytest with `client` fixture)

1. `cd services/onboarding-api`
2. `PYTHONPATH=. pytest tests/test_integration.py -q`
3. Repeat immediately → still **PASS** (in-memory DB per test).

---

## 4. Reproduction Evidence

```
--- Run 1: POST /customers (no get_db override) ---
status=201 body={"id":"...","email":"integration@example.com",...}

--- Run 2: new TestClient, same email (BUG-001 symptom) ---
status=409 body={"error":{"code":"conflict","message":"Customer with email integration@example.com already exists"}}
```

**File:** `evidence/test-results/i6-run-2026-06-20-1112/repro-buggy-client.txt`

---

## 5. Root Cause Analysis

| Factor | Detail |
|--------|--------|
| **Trigger** | API tests used `TestClient(app)` without overriding `get_db` |
| **Default DB** | `sqlite:///./onboarding.db` in `app/core/config.py:13` |
| **Persistence** | Customer rows survive across test runs on disk |
| **Constraint** | `customers.email` UNIQUE (`app/models/customer.py:16`) |
| **Failure mode** | Second run → `ConflictError` → HTTP 409 |

**Failure path:**

```
test_integration.py → TestClient(app) → get_db() → SessionLocal → onboarding.db
POST /customers → CustomerRepository.create → IntegrityError on duplicate email
```

---

## 6. Source File References

| File | Role |
|------|------|
| `services/onboarding-api/app/core/config.py` | Default persistent SQLite URL |
| `services/onboarding-api/app/core/database.py` | `get_db` yields session from engine |
| `services/onboarding-api/tests/conftest.py` | **Fix:** in-memory engine + `dependency_overrides` |
| `services/onboarding-api/tests/test_integration.py` | Uses `client` fixture (fixed) |
| `tests/e2e/test_platform_e2e.py` | `api_client` fixture with same override pattern |
| `docs/bug-investigation.md` | Canonical BUG-001 write-up |

---

## 7. Minimal Fix Description

**Original fix (already merged):**

1. `conftest.py` — `sqlite:///:memory:` engine, `StaticPool`, autouse `create_all`/`drop_all`.
2. `client` fixture — override `get_db`, clear overrides after test.
3. `test_integration.py` — accept `client` fixture parameter.
4. `test_platform_e2e.py` — `api_client` fixture with identical override.

**I6 addition:**

`tests/test_bug001_regression.py` — two tests both POST `integration@example.com`; each passes only when DB resets per test (would fail on shared persistent DB).

---

## 8. Files Changed

| File | Change |
|------|--------|
| `services/onboarding-api/tests/test_bug001_regression.py` | **Added** — regression guard |
| `docs/beginner/I6-bug-diagnosis/I6_REPORT.md` | **Added** — this report |
| `evidence/test-results/i6-run-2026-06-20-1112/` | **Added** — reproduction logs |

**Note:** Core fix in `conftest.py` predates I6; I6 adds explicit regression coverage.

---

## 9. Verification Commands

```bash
# Reproduce BUG-001 symptom
cd services/onboarding-api
DATABASE_URL="sqlite:////tmp/bug001-repro.db" PYTHONPATH=. python repro_script.py  # see evidence

# Verify fix (must pass twice)
PYTHONPATH=. .venv/bin/pytest tests/test_integration.py tests/test_bug001_regression.py -q
PYTHONPATH=. .venv/bin/pytest tests/test_integration.py tests/test_bug001_regression.py -q

# Full service suite
PYTHONPATH=. .venv/bin/pytest -q

# Platform E2E
cd ../.. && PYTHONPATH=. services/onboarding-api/.venv/bin/pytest tests/e2e/test_platform_e2e.py::test_e2e_api_kyc_pipeline -q
```

---

## 10. Verification Results

| Command | Result |
|---------|--------|
| Bug reproduction script | Run1 **201**, Run2 **409** |
| pytest run 1 | **4 passed** |
| pytest run 2 | **4 passed** |
| Full `pytest -q` | **28 passed** |
| E2E `test_e2e_api_kyc_pipeline` | **1 passed** |

**Evidence:** `pytest-run1.txt`, `pytest-run2.txt`, `e2e-pytest.txt`

---

## 11. Risk Assessment

| Risk | Level | Notes |
|------|-------|-------|
| Regression if fixture removed | High | New tests would fail |
| Production impact | **None** | Test-only isolation |
| Side effects of regression file | Low | 2 simple POST tests |
| Disk `onboarding.db` in dev | Low | Dev artifact; not used by pytest |

---

## 12. Agent Suggestions vs Manual Verification

| Topic | Agent suggestion | Manual verification |
|-------|------------------|-------------------|
| Bug choice | BUG-001 from `docs/bug-investigation.md` | Reproduced 201→409 live |
| Root cause | Missing `get_db` override | Confirmed via repro script |
| New fix needed | Consider regression test | Added `test_bug001_regression.py` |
| Double-run | Should pass | **4/4** twice — verified |
| E2E | Should pass | **1/1** — verified |

---

## 13. Findings and Recommendations

1. **Never use raw `TestClient(app)`** in API tests without DB override.
2. **Follow `conftest.py` pattern** for all new router tests.
3. **`observability-verify.sh`** already uses in-memory override — good.
4. Add CI check: grep for `TestClient(app)` outside fixtures (optional).

---

## 14. Verification Summary

| Deliverable | Status |
|-------------|--------|
| Reproduction steps | ✅ Documented + executed |
| Root cause with paths | ✅ |
| Minimal fix | ✅ (conftest + regression tests) |
| Verification commands | ✅ |
| Verification results | ✅ 28/28 API tests |
| Risk assessment | ✅ |
| Agent vs manual | ✅ |

**I6 verdict: PASS**

---

*Evidence: `evidence/test-results/i6-run-2026-06-20-1112/`*
