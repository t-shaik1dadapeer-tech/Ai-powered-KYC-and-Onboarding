# Code Review Report

**Date:** 2026-06-17  
**Reviewer role:** Agent Code Review (A5)  
**Scope:** `services/onboarding-api/`, `engines/`, `clients/node-cli/`, CI config

---

## Summary

| Severity | Count |
|----------|:-----:|
| Critical | 1 |
| High | 2 |
| Medium | 4 |
| Low | 3 |

**Overall quality:** Good for evaluation monorepo — clear layering, strong test coverage, consistent patterns.

---

## Critical

### CR-001: No API authentication

- **Files:** All routers in `app/routers/`
- **Issue:** Any client can call KYC endpoints without credentials
- **Recommendation:** Add API key dependency or document dev-only scope prominently
- **Evidence:** `verification/phase-2.md` risk table

---

## High

### HI-001: No database migrations

- **Files:** `app/main.py` (`create_all`), no `alembic/`
- **Issue:** Schema changes require manual handling; prod unsafe
- **Recommendation:** Initialize Alembic; version initial schema

### HI-002: Intelligence CLI untested directly

- **Files:** `engines/intelligence/src/intelligence/cli.py` — 0% coverage
- **Issue:** CLI failures only caught via subprocess E2E
- **Recommendation:** Add `tests/test_cli.py` with argparse mocks

---

## Medium

### ME-001: Mock verifiers hardcoded

- **Files:** `pan_verification_service.py`, `bank_verification_service.py`
- **Issue:** Always succeed in mock mode — no failure path testing for provider errors
- **Recommendation:** Configurable failure injection for tests

### ME-002: Metrics path cardinality

- **Files:** `app/main.py` MetricsMiddleware
- **Issue:** `path` label uses raw URL path — UUID paths could increase cardinality in prod
- **Recommendation:** Route template normalization (FastAPI route name)

### ME-003: Duplicate analysis outputs

- **Files:** `evidence/api-maps/` and `evidence/flow-traces/` overlap
- **Issue:** Storage duplication
- **Recommendation:** Single output dir with symlinks or INDEX-only references

### ME-004: Git worktree markers in main

- **Files:** `WORKTREE_MARKER.md` in intelligence and observability dirs
- **Issue:** Demo artifacts merged to main
- **Recommendation:** Acceptable for evaluation; remove before production fork

---

## Low

### LO-001: Python 3.9 compat typing

- Uses `Optional[]` instead of `|` — fine for 3.9 host

### LO-002: Missing PR template

- Add `.github/pull_request_template.md`

### LO-003: Release workflow missing

- Architecture references `release-artifacts.yml` — not created

---

## Positive Findings

| Area | Evidence |
|------|----------|
| Layer separation | Routers don't import repositories directly |
| PII handling | PAN/account hashed — `hash_sensitive()` |
| Test isolation fix | BUG-001 fixed with in-memory fixtures |
| CI breadth | Ruff + pytest + cargo + node + docker build |
| Documentation | 15 verification files + evidence INDEX |

---

## Automated Review Evidence

```bash
make ci-local    # lint stage: ruff, cargo clippy, node --check
make test        # 70 tests
```

**CI config:** `.github/workflows/ci.yml` job `lint`

---

## Recommendation

Approve for **coding-agent proficiency evaluation** with documented production gaps. Block production deployment until CR-001 and HI-001 addressed.
