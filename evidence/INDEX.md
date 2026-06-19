# Evidence Index

**Generated:** 2026-06-17T07:27:14Z  
**Command:** `make evidence-index` or `bash scripts/evidence-index.sh`

---

## Summary

| Metric | Value |
|--------|-------|
| Total artifacts | 150 |
| Top-level directories | 12 |
| Phase-linked claims | 15 phases (0–14) |

---

## Claim → Evidence Matrix

| Claim | Phase | Primary evidence | Verification |
|-------|-------|------------------|--------------|
| Evaluation taxonomy B/I/A/D | 0 | [phase-0-evaluation-matrix.md](../docs/evaluation/phase-0-evaluation-matrix.md) | [phase-0.md](../verification/phase-0.md) |
| Architecture design (8 docs, 26 Mermaid) | 1 | [docs/architecture/](../docs/architecture/) | [phase-1.md](../verification/phase-1.md) |
| 9 REST endpoints, 97%+ coverage | 2 | [phase-2-pytest.txt](test-results/phase-2-pytest.txt), [onboarding-api-coverage.xml](test-results/onboarding-api-coverage.xml) | [phase-2.md](../verification/phase-2.md) |
| Repo intelligence (9 APIs detected) | 3 | [api-maps/onboarding-api/](api-maps/onboarding-api/) | [phase-3.md](../verification/phase-3.md) |
| Flow traces + sequence diagrams | 4 | [flow-traces/onboarding-api/](flow-traces/onboarding-api/) | [phase-4.md](../verification/phase-4.md) |
| Node CLI (17 tests) | 5 | [phase-5-node-tests.txt](test-results/phase-5-node-tests.txt) | [phase-5.md](../verification/phase-5.md) |
| Rust analyzer + benchmark | 6 | [phase-6-rust-benchmark.txt](test-results/phase-6-rust-benchmark.txt) | [phase-6.md](../verification/phase-6.md) |
| 70 unified tests | 7 | [phase-7-summary.txt](test-results/phase-7-summary.txt) | [phase-7.md](../verification/phase-7.md) |
| Docker compose stack | 8 | [docker-results/phase-8-static-validation.txt](docker-results/phase-8-static-validation.txt) | [phase-8.md](../verification/phase-8.md) |
| GitHub Actions CI | 9 | [ci-results/phase-9-ci-local.txt](ci-results/phase-9-ci-local.txt) | [phase-9.md](../verification/phase-9.md) |
| KYC Prometheus metrics + dashboard | 10 | [metrics-snapshot.txt](observability-results/metrics-snapshot.txt), [kyc-platform-dashboard.svg](screenshots/kyc-platform-dashboard.svg) | [phase-10.md](../verification/phase-10.md) |
| Git worktree parallel streams | 11 | [phase-11-worktree-demo.txt](worktrees/phase-11-worktree-demo.txt) | [phase-11.md](../verification/phase-11.md) |
| Agent vs manual audit | 12 | [phase-12-audit.txt](verification/phase-12-audit.txt) | [phase-12.md](../verification/phase-12.md) |
| Evidence index (this file) | 13 | [INDEX.md](INDEX.md) | [phase-13.md](../verification/phase-13.md) |
| Final scorecard | 14 | [final-review.md](../docs/final-review.md) | [phase-14.md](../verification/phase-14.md) |

---

## By Evaluation Dimension

| Dimension | Evidence paths |
|-----------|----------------|
| **B1** Repo discovery | `api-maps/onboarding-api/service-inventory.md`, inventories |
| **B2** API mapping | `api-maps/onboarding-api/api-map.md` |
| **B3** ER diagrams | `api-maps/onboarding-api/er-diagram.mmd`, `diagrams/onboarding-api-er.mmd` |
| **B4** Flow tracing | `flow-traces/onboarding-api/sequence-diagrams/`, flow-docs |
| **B5** Test discovery | `api-maps/onboarding-api/test-inventory.md`, test-results/ |
| **B6** KYC domain | test-results/phase-2-pytest.txt, phase-7-summary.txt |
| **I1** FastAPI | onboarding-api coverage XML |
| **I2** Node CLI | phase-5-node-tests.txt |
| **I3** Rust | phase-6-rust-benchmark.txt |
| **I4** Docker | docker-results/ |
| **I5** CI/CD | ci-results/, `.github/workflows/ci.yml` |
| **I6** Observability | observability-results/, screenshots/ |
| **A1** Worktrees | worktrees/phase-11-worktree-demo.txt |
| **A2** Agent verification | verification/phase-12-audit.txt |
| **D2** Evidence store | This index |
| **D3** Architecture traceability | architecture/phase-0-1-verification.txt |
| **D4** Risk assessment | verification/phase-*.md § Risk |
| **D5** Verification commands | verification/README.md, Makefile |
| **D6** Conventions | docs/architecture/05-folder-structure.md |

---

## Directory Inventory

### `evidence/api-maps/` (12 files)

- `evidence/api-maps/.gitkeep`
- `evidence/api-maps/onboarding-api/analysis-manifest.json`
- `evidence/api-maps/onboarding-api/api-inventory.md`
- `evidence/api-maps/onboarding-api/api-map.md`
- `evidence/api-maps/onboarding-api/controller-inventory.md`
- `evidence/api-maps/onboarding-api/dependency-inventory.md`
- `evidence/api-maps/onboarding-api/er-diagram.mmd`
- `evidence/api-maps/onboarding-api/flow-tracing-report.md`
- `evidence/api-maps/onboarding-api/model-inventory.md`
- `evidence/api-maps/onboarding-api/service-inventory.md`
- `evidence/api-maps/onboarding-api/test-inventory.md`
- `evidence/api-maps/onboarding-api/uncertainty-report.md`

### `evidence/architecture/` (2 files)

- `evidence/architecture/.gitkeep`
- `evidence/architecture/phase-0-1-verification.txt`

### `evidence/ci-results/` (3 files)

- `evidence/ci-results/.gitkeep`
- `evidence/ci-results/phase-9-ci-local.txt`
- `evidence/ci-results/phase-9-workflow-validation.txt`

### `evidence/diagrams/` (2 files)

- `evidence/diagrams/.gitkeep`
- `evidence/diagrams/onboarding-api-er.mmd`

### `evidence/docker-results/` (3 files)

- `evidence/docker-results/.gitkeep`
- `evidence/docker-results/phase-8-docker-verify.txt`
- `evidence/docker-results/phase-8-static-validation.txt`

### `evidence/final-review/` (1 files)

- `evidence/final-review/phase-14-final-review.txt`

### `evidence/flow-traces/` (32 files)

- `evidence/flow-traces/.gitkeep`
- `evidence/flow-traces/onboarding-api-flows.md`
- `evidence/flow-traces/onboarding-api-uncertainty.md`
- `evidence/flow-traces/onboarding-api/analysis-manifest.json`
- `evidence/flow-traces/onboarding-api/api-inventory.md`
- `evidence/flow-traces/onboarding-api/api-map.md`
- `evidence/flow-traces/onboarding-api/controller-inventory.md`
- `evidence/flow-traces/onboarding-api/dependency-inventory.md`
- `evidence/flow-traces/onboarding-api/er-diagram.mmd`
- `evidence/flow-traces/onboarding-api/flow-docs/get-customer-customer-id.md`
- `evidence/flow-traces/onboarding-api/flow-docs/get-health.md`
- `evidence/flow-traces/onboarding-api/flow-docs/get-kyc-status-customer-id.md`
- `evidence/flow-traces/onboarding-api/flow-docs/get-metrics.md`
- `evidence/flow-traces/onboarding-api/flow-docs/post-bank-verify.md`
- `evidence/flow-traces/onboarding-api/flow-docs/post-customers.md`
- `evidence/flow-traces/onboarding-api/flow-docs/post-kyc.md`
- `evidence/flow-traces/onboarding-api/flow-docs/post-pan-verify.md`
- `evidence/flow-traces/onboarding-api/flow-docs/post-risk-score.md`
- `evidence/flow-traces/onboarding-api/flow-tracing-report.md`
- `evidence/flow-traces/onboarding-api/model-inventory.md`
- `evidence/flow-traces/onboarding-api/sequence-diagrams/get-customer-customer-id.mmd`
- `evidence/flow-traces/onboarding-api/sequence-diagrams/get-health.mmd`
- `evidence/flow-traces/onboarding-api/sequence-diagrams/get-kyc-status-customer-id.mmd`
- `evidence/flow-traces/onboarding-api/sequence-diagrams/get-metrics.mmd`
- `evidence/flow-traces/onboarding-api/sequence-diagrams/post-bank-verify.mmd`
- `evidence/flow-traces/onboarding-api/sequence-diagrams/post-customers.mmd`
- `evidence/flow-traces/onboarding-api/sequence-diagrams/post-kyc.mmd`
- `evidence/flow-traces/onboarding-api/sequence-diagrams/post-pan-verify.mmd`
- `evidence/flow-traces/onboarding-api/sequence-diagrams/post-risk-score.mmd`
- `evidence/flow-traces/onboarding-api/service-inventory.md`
- _… and 2 more_

### `evidence/observability-results/` (2 files)

- `evidence/observability-results/metrics-snapshot.txt`
- `evidence/observability-results/phase-10-observability.txt`

### `evidence/screenshots/` (2 files)

- `evidence/screenshots/.gitkeep`
- `evidence/screenshots/kyc-platform-dashboard.svg`

### `evidence/test-results/` (86 files)

- `evidence/test-results/.gitkeep`
- `evidence/test-results/intelligence-coverage-html/.gitignore`
- `evidence/test-results/intelligence-coverage-html/status.json`
- `evidence/test-results/intelligence-coverage.xml`
- `evidence/test-results/onboarding-api-coverage-html/.gitignore`
- `evidence/test-results/onboarding-api-coverage-html/status.json`
- `evidence/test-results/onboarding-api-coverage.xml`
- `evidence/test-results/phase-2-pytest.txt`
- `evidence/test-results/phase-3-pytest.txt`
- `evidence/test-results/phase-4-pytest.txt`
- `evidence/test-results/phase-5-node-tests.txt`
- `evidence/test-results/phase-6-rust-benchmark.txt`
- `evidence/test-results/phase-7-summary.txt`
- `evidence/test-results/phase-7-unified-testing.txt`
- _… and 56 more_

### `evidence/verification/` (1 files)

- `evidence/verification/phase-12-audit.txt`

### `evidence/worktrees/` (1 files)

- `evidence/worktrees/phase-11-worktree-demo.txt`

---

## Key Artifacts (quick links)

| Artifact | Path |
|----------|------|

---

## Regenerate

```bash
make evidence-index
```

Also re-run phase scripts to refresh stale artifacts:

```bash
make test                  # Phase 7
make ci-local              # Phase 9
make observability-verify  # Phase 10
make verify-phases         # Phase 12
```
