# I3 — Small Safe Change in Unfamiliar Repository

**Evaluation criterion:** I3 (Safe Change)  
**Change:** Email lowercase normalization on customer creation  
**Scope:** `services/onboarding-api/` — validation layer only  
**Verification date:** 2026-06-20T05:27:00Z (UTC)  
**Evidence:** `evidence/test-results/i3-run-2026-06-20-1057/`  
**Machine-readable:** `files-changed.csv`, `change.diff` (in evidence)

---

## 1. Executive Summary

| Item | Result | Confidence |
|------|--------|------------|
| Change type | Validation improvement | High |
| Files modified | **2** (schema + tests) | High |
| Lines changed | **+30** (5 production, 25 test) | High |
| Architectural impact | **None** — router/service/repo unchanged | High |
| Tests added | **2** new cases | High |
| `pytest tests/test_customers.py` | **7/7 PASS** | High — executed |
| Full onboarding-api suite | **26/26 PASS** | High — executed |
| Overall I3 status | **PASS** | High |

---

## 2. Repository Analysis

### Structure (relevant to change)

```
services/onboarding-api/
├── app/
│   ├── routers/customers.py      # POST /customers entry
│   ├── services/customer_service.py
│   ├── repositories/customer_repository.py  # unique on email
│   └── schemas/customer.py       # ← change target (Pydantic)
└── tests/test_customers.py       # ← test updates
```

### Candidate areas considered

| Candidate | Scope | Risk | Selected? |
|-----------|-------|------|-----------|
| Email lowercase normalization | 1 validator | Low | **Yes** |
| Remove redundant `get_by_id` in `KycService` | 1 line refactor | Low | No — no user-visible fix |
| Health DB connectivity probe | Router + DB | Medium | No — broader ops change |
| KYC single transaction | Service + repos | High | No — too large for I3 |

### Safe-change process in repo

- `docs/safe-change.md` — gate before PRs
- `make safe-change-check` — full monorepo validation
- `CONTRIBUTING.md` — layer rules (`routers → services → repositories`)

---

## 3. Selected Change Description

### Problem

`CustomerCreate` accepted emails as provided. SQLite `UNIQUE` on `email` is **case-sensitive**, so `jane@example.com` and `JANE@EXAMPLE.COM` could register as different customers — inconsistent with typical email identity rules and duplicate-detection expectations.

### Solution

Add a Pydantic `field_validator` on `email` in `CustomerCreate` to `strip().lower()` before persistence.

### Why safe

- Single field, single file in production code
- Follows existing `strip_name` validator pattern
- No API contract change (still accepts any valid email string)
- Backed by new regression tests
- Existing duplicate-email test still passes

---

## 4. Files Changed

| File | Type |
|------|------|
| `services/onboarding-api/app/schemas/customer.py` | Production |
| `services/onboarding-api/tests/test_customers.py` | Test |

---

## 5. Diff Summary

```
 services/onboarding-api/app/schemas/customer.py |  5 +++++
 services/onboarding-api/tests/test_customers.py | 25 +++++++++++++++++++++++++
 2 files changed, 30 insertions(+)
```

**Production change:**

```python
@field_validator("email")
@classmethod
def normalize_email(cls, value: str) -> str:
    return value.strip().lower()
```

---

## 6. Why These Files Were Modified

| File | Reason |
|------|--------|
| `app/schemas/customer.py` | Validation boundary for `POST /customers` — normalizes input before `CustomerService` / `CustomerRepository` |
| `tests/test_customers.py` | Prove lowercase storage and 409 on case-variant duplicate |

**Not modified:** `customer_repository.py`, `customer_service.py`, `routers/customers.py` — already pass normalized email through unchanged.

---

## 7. Test Updates

| Test | Purpose |
|------|---------|
| `test_create_customer_normalizes_email_case` | `Case.User@Example.COM` → stored as `case.user@example.com` |
| `test_create_customer_duplicate_email_different_case` | `JANE@EXAMPLE.COM` conflicts with fixture `jane@example.com` → 409 |

Existing tests (`test_create_customer`, `test_create_customer_duplicate_email`, etc.) unchanged and passing.

---

## 8. Test Execution Commands

```bash
# Targeted
cd services/onboarding-api
PYTHONPATH=. .venv/bin/pytest tests/test_customers.py -v

# Full service regression
PYTHONPATH=. .venv/bin/pytest -q

# Optional monorepo gate (per docs/safe-change.md)
make safe-change-check
```

---

## 9. Actual Test Results

### `tests/test_customers.py` (executed 2026-06-20)

```
tests/test_customers.py::test_create_customer PASSED
tests/test_customers.py::test_create_customer_duplicate_email PASSED
tests/test_customers.py::test_create_customer_normalizes_email_case PASSED
tests/test_customers.py::test_create_customer_duplicate_email_different_case PASSED
tests/test_customers.py::test_create_customer_invalid_email PASSED
tests/test_customers.py::test_get_customer PASSED
tests/test_customers.py::test_get_customer_not_found PASSED

7 passed in 0.20s
```

### Full onboarding-api suite

```
26 passed in 0.92s
```

**Evidence:** `evidence/test-results/i3-run-2026-06-20-1057/pytest-customers.txt`, `pytest-all.txt`, `change.diff`

---

## 10. Risk Assessment

| Risk type | Level | Notes |
|-----------|-------|-------|
| Functional | **Low** | Only affects email casing on create |
| Regression | **Low** | 26/26 service tests pass |
| Deployment | **Low** | No migration; existing rows unchanged |
| Data migration | **None required** | Old mixed-case emails remain as stored |
| Testing confidence | **High** | 2 new tests + full suite green |

**Residual risk:** Pre-existing customers with uppercase emails are not retroactively normalized. Out of scope for this minimal change.

---

## 11. Agent Suggestions vs Manual Verification

| Topic | Initial agent suggestion | After code review / verification |
|-------|--------------------------|----------------------------------|
| Change choice | Email normalization **or** remove redundant `get_by_id` in KycService | **Selected email normalization** — user-visible data integrity fix |
| Layer | Schema validator vs repository | **Schema** — matches `strip_name` pattern; single entry point |
| Test strategy | One normalization test | **Two tests** — normalization + case-variant 409 |
| Side effects | Assumed unique constraint catches case dupes | **Verified** — test proves 409 with `JANE@EXAMPLE.COM` vs `jane@example.com` |
| Full suite | Assumed pass | **Verified** — 26/26 executed |

---

## 12. Findings and Recommendations

### Outcome

Small, focused validation fix with clear tests and no layer violations.

### Follow-ups (not in this change)

1. Backfill script for existing mixed-case emails (if production data exists)
2. Apply same normalization to any future email-bearing schemas
3. Run `make safe-change-check` before merge to main

---

## 13. Verification Summary

| Step | Result |
|------|--------|
| Identified safe candidate | Email normalization |
| Minimal diff (2 files) | ✅ |
| Tests added | 2 |
| `pytest tests/test_customers.py` | **7/7 PASS** |
| `pytest -q` (onboarding-api) | **26/26 PASS** |
| Layer rules respected | ✅ (schemas only) |
| Evidence captured | ✅ |

**I3 verdict: PASS**

---

*Change diff on disk (uncommitted until user requests commit). Evidence: `evidence/test-results/i3-run-2026-06-20-1057/`*
