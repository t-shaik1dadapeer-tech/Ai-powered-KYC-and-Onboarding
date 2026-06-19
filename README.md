# AI-Powered KYC & Onboarding Repository Intelligence Platform

A production-grade, phase-gated monorepo demonstrating advanced coding-agent workflows across **KYC onboarding** and **repository intelligence** (discovery, API mapping, ER diagrams, flow tracing).

## Status

| Phase | Name | Status |
|-------|------|--------|
| **0** | Evaluation Mapping | ✅ Complete |
| **1** | System Design | ✅ Complete |
| **2** | FastAPI Service | ✅ Complete |
| **3** | Repository Intelligence Engine | ✅ Complete |
| **4** | End-to-End Flow Tracing | ✅ Complete |
| **5** | Node.js CLI Client | ✅ Complete |
| **6** | Rust Analysis Engine | ✅ Complete |
| **7** | Unified Testing | ✅ Complete |
| **8** | Dockerization | ✅ Complete |
| **9** | CI/CD | ✅ Complete |
| **10** | Observability | ✅ Complete |
| **11** | Worktree Demonstration | ✅ Complete |
| **12** | Agent vs Manual Verification | ✅ Complete |
| **13** | Engineering Evidence | ✅ Complete |
| **14** | Final Review | ✅ Complete |

## Quick Links

- [Evaluation Matrix (Phase 0)](docs/evaluation/phase-0-evaluation-matrix.md)
- [Architecture Docs (Phase 1)](docs/architecture/README.md)
- [Technology Rationale](docs/architecture/07-technology-rationale.md)
- [Development Roadmap](docs/architecture/06-development-roadmap.md)

## Verification

```bash
# Run all test suites + coverage
make test

# Phase 0–1 docs check
bash -c 'test -f docs/evaluation/phase-0-evaluation-matrix.md && echo "Phase 0 OK"'
bash -c 'ls docs/architecture/*.md | wc -l'  # Expected: 8
```

See `verification/` for per-phase checklists. Test results: `evidence/test-results/phase-7-summary.txt`.

## Docker (Phase 8)

```bash
# Requires Docker Desktop
make docker-verify    # build, up, health checks, smoke tests
make docker-up        # start API + Postgres + Prometheus + Grafana
make docker-down      # stop all services
```

| Service | URL |
|---------|-----|
| Onboarding API | http://localhost:8000 |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 (admin/admin) |

## CI/CD (Phase 9)

```bash
make ci-local    # simulate GitHub Actions locally
```

Workflow: [`.github/workflows/ci.yml`](.github/workflows/ci.yml) — lint → parallel tests → E2E → docker build → artifacts.

Failure replay guide: [`docs/ci/failure-examples.md`](docs/ci/failure-examples.md)

## Observability (Phase 10)

```bash
make observability-verify   # metrics snapshot + dashboard SVG evidence
```

Metrics catalog: [`docs/observability/metrics-catalog.md`](docs/observability/metrics-catalog.md)  
Grafana dashboard: `infra/grafana/dashboards/kyc-platform.json`  
Evidence: `evidence/screenshots/kyc-platform-dashboard.svg`

## Worktrees (Phase 11)

```bash
make worktree-demo   # git init, parallel worktrees, merge demo
```

Docs: [`docs/worktrees/README.md`](docs/worktrees/README.md)

## Verification Audit (Phase 12)

```bash
make verify-phases   # validate all 15 verification/phase-*.md files
```

Master audit: [`docs/verification/agent-vs-manual-audit.md`](docs/verification/agent-vs-manual-audit.md)  
Index: [`verification/README.md`](verification/README.md)

## Evidence Store (Phase 13)

```bash
make evidence-index   # regenerate evidence/INDEX.md
```

Catalog: [`evidence/INDEX.md`](evidence/INDEX.md) — claim → artifact matrix for all phases

## Final Review (Phase 14)

**Overall score: 89%** across 19 evaluation dimensions (B/I/A/D).

```bash
make final-review
```

Scorecard: [`docs/final-review.md`](docs/final-review.md)

## Evaluation Re-Audit (Strict B/I/A/D Framework)

**Start here for Cursor agent checks:** [`docs/evaluation-index.md`](docs/evaluation-index.md) (fast, 24 criteria)  
**Requirements checklist:** [`docs/evaluation-requirements.md`](docs/evaluation-requirements.md)

| Report | Path | When to load |
|--------|------|--------------|
| **Quick index (use first)** | [`evaluation-index.md`](docs/evaluation-index.md) | Any single criterion |
| Scores (24 rows) | [`evaluation-matrix.md`](docs/evaluation-matrix.md) | All scores at once |
| Gap analysis (deep) | [`evaluation-gap-analysis.md`](docs/evaluation-gap-analysis.md) | One ID deep audit |
| Final evaluation | [`final-evaluation-report.md`](docs/final-evaluation-report.md) | Final grade |

**Overall strict score: 77/100 (B+)** — see final evaluation for hiring verdict.

## License

TBD — internal demonstration project.
