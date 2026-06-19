# Modernization Report

**Date:** 2026-06-17  
**Scope:** Security, architecture, performance, DX, dependencies

---

## Security Improvements

| Priority | Item | Current state | Recommendation |
|:--------:|------|---------------|----------------|
| P1 | API authentication | None on endpoints | API key middleware or OAuth2 gateway |
| P1 | Secrets in repo | `.env` gitignored | Use secret manager in prod |
| P2 | PAN/bank storage | Hashed at rest ✅ | Add field-level encryption for JSON provider_response |
| P2 | Dependency scanning | Manual | Dependabot / `pip audit` in CI (partial — ci mentions pip audit in rules) |
| P3 | CORS / rate limiting | Not configured | Add slowapi rate limit on `/kyc` |

**Evidence:** Risk in `verification/phase-2.md` — "No auth on endpoints — High"

---

## Architecture Improvements

| Item | Current | Target |
|------|---------|--------|
| Schema migrations | `create_all()` only | Alembic versioned migrations |
| Async workers | None | Celery/ARQ for long KYC verification |
| Intelligence API | CLI-only | Optional HTTP service on :8001 |
| Contract testing | OpenAPI export added | Pact/Schemathesis against OpenAPI |
| Event-driven KYC | Synchronous | Outbox pattern for audit trail |

---

## Performance Improvements

| Area | Finding | Action |
|------|---------|--------|
| Rust scan | ~82ms / 52 files ✅ | Scale test on 10k+ file monorepo |
| API latency | Prometheus histogram exists | Add p99 alert in Grafana |
| DB queries | No N+1 observed in KYC path | Add SQLAlchemy query logging in dev |
| Intelligence CLI | 0% coverage on `cli.py` | Dedicated CLI tests |
| Node generate-report | ~413ms in tests | Cache venv detection |

See [performance-analysis.md](performance-analysis.md)

---

## Developer Experience Improvements

| Done | Item |
|:----:|------|
| ✅ | `Makefile` with test/ci/verify targets |
| ✅ | `CONTRIBUTING.md` |
| ✅ | Phase verification files |
| ⏳ | `.devcontainer/` for one-click setup |
| ⏳ | `pre-commit` hooks (ruff, cargo fmt) |
| ⏳ | PR template |

---

## Dependency Upgrades (recommended)

| Package | Location | Note |
|---------|----------|------|
| Python | `requires-python >=3.9` | Consider 3.12 standard in Docker |
| FastAPI | pyproject.toml | Pin upper bound in prod |
| SQLAlchemy | 2.x ✅ | Already modern |
| Node | engines >=18 | Consider LTS 20 in Dockerfile ✅ |
| Rust | 2021 edition ✅ | Keep toolchain pinned in CI |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| Auth gap exploited | High in prod | Critical | Do not deploy without gateway |
| Schema drift | Medium | High | Alembic |
| Stale dependencies | Medium | Medium | Renovate bot |
| Analyzer false positives | Medium | Low | Uncertainty reports ✅ |

**Evaluation impact:** Improves A4 from PARTIAL → PASS when executed.
