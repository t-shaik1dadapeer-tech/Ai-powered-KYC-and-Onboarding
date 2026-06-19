# Bug Investigation — BUG-001: Integration Tests Hit Persistent SQLite DB

**ID:** BUG-001  
**Severity:** Medium (test flakiness / false failures)  
**Status:** Fixed  
**Discovered:** Phase 9 CI local run (2026-06-16)  
**Evidence:** `evidence/ci-results/phase-9-ci-local.txt` (initial failure), `verification/phase-9.md`

---

## Summary

Integration and E2E tests created a module-level `TestClient(app)` without overriding the database dependency. Tests wrote to persistent `onboarding.db` on disk instead of an isolated in-memory database. Re-runs returned **409 Conflict** for duplicate emails.

---

## Reproduction Steps

1. Run onboarding-api tests once with `test_integration.py` using raw `TestClient(app)`:
   ```python
   client = TestClient(app)  # no fixture
   ```
2. POST customer with `email="integration@example.com"` → 201
3. Re-run tests without deleting `services/onboarding-api/onboarding.db`
4. Same POST → **409 Conflict** (email unique constraint)

**Observed output:**
```
FAILED tests/test_integration.py::test_full_kyc_onboarding_flow - assert 409 == 201
FAILED test_platform_e2e.py::test_e2e_api_kyc_pipeline - assert 409 == 201
```

---

## Root Cause

| Factor | Detail |
|--------|--------|
| **Primary** | `test_integration.py` bypassed `conftest.py` `client` fixture that overrides `get_db` with in-memory SQLite |
| **Secondary** | E2E `api_client` fixture in `tests/e2e/test_platform_e2e.py` had same issue |
| **File** | `services/onboarding-api/tests/test_integration.py` (original) |
| **File** | `tests/e2e/test_platform_e2e.py` (original fixture) |
| **DB** | Default `DATABASE_URL=sqlite:///./onboarding.db` in `app/core/config.py:13` |

---

## Affected Files

- `services/onboarding-api/tests/test_integration.py` — fixed to use `client` fixture
- `tests/e2e/test_platform_e2e.py` — fixed with in-memory DB override in `api_client` fixture
- `services/onboarding-api/tests/conftest.py` — reference implementation (correct pattern)

---

## Minimal Fix

**test_integration.py** — inject fixture:
```python
def test_full_kyc_onboarding_flow(client):  # was: no fixture
    create_resp = client.post("/customers", json={...})
```

**test_platform_e2e.py** — override `get_db` in fixture (see current file lines 23–48).

---

## Verification Steps

**Regression tests (BUG-001):**
- `services/onboarding-api/tests/test_integration.py::test_full_kyc_onboarding_flow` — uses `client` fixture with in-memory DB
- `tests/e2e/test_platform_e2e.py::test_e2e_api_kyc_pipeline` — uses `api_client` fixture with DB override

```bash
# Must pass twice in a row (proves no disk pollution)
cd services/onboarding-api
PYTHONPATH=. .venv/bin/pytest tests/test_integration.py -q
PYTHONPATH=. .venv/bin/pytest tests/test_integration.py -q

PYTHONPATH=. .venv/bin/pytest ../../tests/e2e/test_platform_e2e.py -q
make ci-local   # 9/9 stages
```

**Result:** ✅ All pass on repeated runs (`evidence/ci-results/phase-9-ci-local.txt`)

---

## Lessons (I6 / Safe Change)

1. **Always use DB override fixtures** for API tests — never module-level `TestClient(app)` against default DB
2. **CI must be deterministic** — flaky 409s blocked Phase 9 gate
3. **Document pattern** in `docs/safe-change.md` and run `make safe-change-check` before PRs

---

## Related

- Uncertainty reports (analyzer): not the same as software defects — see `uncertainty-report.md`
- Issue template: `.github/ISSUE_TEMPLATE/bug_report.md`
