# Evaluation Index — 24 Criteria Quick Reference

**Use this file first.** Load time: ~2 min read. Do not load `evaluation-gap-analysis.md` unless auditing one criterion in depth.

**Framework:** B1–B6 · I1–I6 · A1–A6 · D1–D6 (24 items)

---

## How to Ask Cursor Agent

Copy one of these prompts:

```
Evaluate criterion B4 using docs/evaluation-index.md.
Use exact response format. Cite file paths only from this repo.
```

```
Score all 24 items using docs/evaluation-index.md + docs/evaluation-matrix.md.
Output table: ID | Status | Score | Evidence path
```

```
Compare docs/evaluation-matrix.md scores against live repo for D1 only.
Status must be PASS | PARTIAL | FAIL.
```

---

## Mandatory Response Format (every criterion)

When agent evaluates **any** ID (e.g. B3, I2, D4), output **exactly**:

```markdown
## [ID] [Name]

| Field | Value |
|-------|-------|
| Status | PASS / PARTIAL / FAIL |
| Score | 0–10 |
| Completion | 0–100% |
| Risk | Low / Medium / High |

**Evidence:** `path/to/file` — one-line proof

**Missing:** bullet list or "None"

**Verify:** `single shell command`
```

---

## 24 Criteria — Definition · Primary Doc · Verify Command

| ID | Name | Primary doc (load this) | Key evidence path | Verify |
|----|------|-------------------------|-------------------|--------|
| **B1** | Repo Discovery | `repository-inventory.md` | `engines/intelligence/`, `evidence/api-maps/` | `PYTHONPATH=src pytest engines/intelligence/tests/test_analyzer.py -q` |
| **B2** | API Mapping | `api-map.md` | `docs/api/openapi.json` | `test -f docs/api/openapi.json && jq '.paths \| keys \| length' docs/api/openapi.json` |
| **B3** | Test Discovery | `evaluation-matrix.md` § B3 | `evidence/test-results/phase-7-summary.txt` | `make test` |
| **B4** | FastAPI Greenfield | `repository-inventory.md` § FastAPI | `services/onboarding-api/app/` | `cd services/onboarding-api && PYTHONPATH=. .venv/bin/pytest -q` |
| **B5** | Node.js Greenfield | `repository-inventory.md` § Node | `clients/node-cli/` | `cd clients/node-cli && npm test` |
| **B6** | Rust Greenfield | `performance-analysis.md` § Rust | `engines/rust-analyzer/` | `cd engines/rust-analyzer && cargo test -q` |
| **I1** | ER Diagram | `er-diagram.md` | `app/models/*.py` | `grep ForeignKey services/onboarding-api/app/models/*.py` |
| **I2** | E2E Flow Trace | `flow-trace.md` | `evidence/flow-traces/onboarding-api/sequence-diagrams/` | `ls evidence/flow-traces/onboarding-api/sequence-diagrams/*.mmd \| wc -l` |
| **I3** | Safe Change | `docs/safe-change.md` | `scripts/safe-change-check.sh`, `CONTRIBUTING.md` | `make safe-change-check` |
| **I4** | Polyglot Service Pair | `architecture.md` | `tests/e2e/test_platform_e2e.py` | `PYTHONPATH=. .venv/bin/pytest tests/e2e/test_platform_e2e.py -q` |
| **I5** | Dockerization | `devops-validation.md` § Docker | `infra/docker/docker-compose.yml` | `make docker-verify` or `docker compose -f infra/docker/docker-compose.yml config` |
| **I6** | Bug Diagnosis | `bug-investigation.md` | `docs/bug-investigation.md`, `tests/test_integration.py` | `grep BUG-001 docs/bug-investigation.md` |
| **A1** | Multi Worktree Planning | `parallel-development.md` | `docs/worktrees/merge-strategy.md` | `test -f docs/worktrees/merge-strategy.md` |
| **A2** | Parallel Worktrees | `parallel-development.md` | `evidence/worktrees/phase-11-worktree-demo.txt` | `make worktree-demo` |
| **A3** | Polyglot Mini-System | `architecture.md` | full monorepo tree | `make test` (5 suites) |
| **A4** | Repository Modernization | `modernization-report.md` | `.github/dependabot.yml`, `app/core/auth.py` | `test -f .github/dependabot.yml` |
| **A5** | Agent Code Review | `code-review-report.md` | `.github/pull_request_template.md`, CI | `make ci-local` |
| **A6** | Performance Profiling | `performance-analysis.md` | `evidence/performance/load-test.txt` | `make load-test` |
| **D1** | Terraform | `infra/terraform/README.md` | `infra/terraform/*.tf`, `evidence/terraform-results/` | `make terraform-verify` |
| **D2** | Docker Compose | `devops-validation.md` § Compose | `infra/docker/docker-compose.yml` | `docker compose -f infra/docker/docker-compose.yml config` |
| **D3** | CI/CD | `devops-validation.md` § CI/CD | `.github/workflows/ci.yml` (infra-validate job) | `make ci-local` |
| **D4** | Kubernetes | `devops-validation.md` § Kubernetes | `infra/kubernetes/kyc-platform.yaml` | `make k8s-verify` |
| **D5** | Reproducible Environment | `CONTRIBUTING.md` | `Makefile`, `scripts/` | `make test` |
| **D6** | Observability | `devops-validation.md` § Prometheus | `app/core/metrics.py`, `infra/grafana/` | `make observability-verify` |

---

## Which File to Load (speed guide)

| Need | Load | Avoid (slow) |
|------|------|----------------|
| **One criterion** (e.g. B2) | `evaluation-index.md` + row's Primary doc | `evaluation-gap-analysis.md` |
| **All 24 scores** | `evaluation-matrix.md` (~70 lines) | `final-evaluation-report.md` |
| **Deep audit one ID** | `evaluation-gap-analysis.md` § that ID | entire gap file for all IDs |
| **Final grade / hiring** | `final-evaluation-report.md` | — |
| **Evidence paths only** | `../evidence/INDEX.md` | coverage HTML dirs |
| **Agent vs manual** | `verification-report.md` | all `verification/phase-*.md` |

---

## Category Score Weights

| Group | IDs | Current score (see matrix) |
|-------|-----|----------------------------|
| Basics | B1–B6 | 88% |
| Intermediate | I1–I6 | 83% |
| Advanced | A1–A6 | 85% |
| DevOps | D1–D6 | 82% |
| **Overall** | 24 | **85%** (live verify: **24/24 PASS**) |

Full scores: `docs/evaluation-matrix.md`  
Live audit: `make full-24-audit` → `evidence/evaluation-results/full-24-audit-*.txt`

---

## Requirements Checklist (all 24 must be auditable)

- [x] Each ID has **Status** PASS | PARTIAL | FAIL
- [x] Each ID has **Score** 0–10 in `evaluation-matrix.md`
- [x] Each ID has **≥1 evidence file path** (not prose-only)
- [x] Each ID has **verify command** (above table)
- [x] Deep detail optional in `evaluation-gap-analysis.md`
- [x] Live check: agent runs verify command, not assumptions

---

## Cursor Rule (optional paste in chat)

> You are a strict evaluator. Use only `docs/evaluation-index.md` for the criterion list and `docs/evaluation-matrix.md` for scores. For the requested ID(s), output the **Mandatory Response Format** exactly. Cite repo file paths. Run verify commands when possible. Do not load files over 300 lines unless user asks for deep audit.

---

## File Map

```
docs/evaluation-index.md     ← YOU ARE HERE (start)
docs/evaluation-matrix.md    ← scores table (24 rows)
docs/evaluation-gap-analysis.md  ← deep audit (426 lines — one ID at a time)
docs/final-evaluation-report.md ← final grade + hiring verdict
docs/[topic].md              ← per-criterion detail (see table above)
evidence/INDEX.md            ← artifact paths
verification/phase-*.md      ← phase delivery proof (15 files)
```
