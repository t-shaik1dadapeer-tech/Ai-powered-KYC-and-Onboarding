# Evaluation Criteria — Requirements (24 Tasks)

**Purpose:** Checklist for building or auditing a repo so every B/I/A/D item is provable in Cursor with one MD file + one command.

---

## The 24 Requirements (what each must prove)

### Basics B1–B6

| ID | Requirement | Must have in repo |
|----|-------------|-------------------|
| B1 | Scan repo → inventories | Intelligence/Rust engine + `evidence/api-maps/` |
| B2 | Catalog all HTTP APIs | OpenAPI JSON + `docs/api-map.md` |
| B3 | Find all tests | Test count report + `make test` |
| B4 | Layered FastAPI app | `services/onboarding-api/` routers→services→repos |
| B5 | Node CLI client | `clients/node-cli/` + npm test |
| B6 | Rust tool/binary | `engines/rust-analyzer/` + cargo test |

### Intermediate I1–I6

| ID | Requirement | Must have in repo |
|----|-------------|-------------------|
| I1 | ER diagram from models | `docs/er-diagram.md` + ORM models |
| I2 | Request→DB flow trace | Sequence `.mmd` + `docs/flow-trace.md` |
| I3 | Safe change process | Tests + CI + documented bug/fix pattern |
| I4 | 2+ languages integrated | E2E test crossing API+CLI+engines |
| I5 | Docker images/compose | Dockerfiles + `docker-compose.yml` |
| I6 | Bug found + fixed + doc | `docs/bug-investigation.md` |

### Advanced A1–A6

| ID | Requirement | Must have in repo |
|----|-------------|-------------------|
| A1 | Worktree plan documented | Merge strategy + stream ownership |
| A2 | Worktrees executed | `git worktree list` evidence |
| A3 | Polyglot mini-system | Python+Node+Rust in one repo |
| A4 | Modernization analysis | `docs/modernization-report.md` |
| A5 | Code review evidence | `docs/code-review-report.md` + CI lint |
| A6 | Performance analysis | Benchmarks and/or metrics + report |

### DevOps D1–D6

| ID | Requirement | Must have in repo |
|----|-------------|-------------------|
| D1 | Terraform IaC | `*.tf` modules (currently **missing**) |
| D2 | Docker Compose stack | `infra/docker/docker-compose.yml` |
| D3 | CI/CD pipeline | `.github/workflows/ci.yml` |
| D4 | Kubernetes manifests | `infra/kubernetes/*.yaml` |
| D5 | Reproducible dev env | Makefile + CONTRIBUTING + scripts |
| D6 | Metrics + dashboards | Prometheus + Grafana + `/metrics` |

---

## Exact Agent Response Format

Every evaluation answer **must** use this block (copy-paste template):

```
## [B1] Repo Discovery

| Field | Value |
|-------|-------|
| Status | PASS / PARTIAL / FAIL |
| Score | /10 |
| Completion | % |
| Risk | Low/Medium/High |

Evidence: `path` — proof
Missing: ...
Verify: `command`
```

---

## Fast Cursor Workflow

1. Open repo in Cursor
2. Chat: **"Evaluate B4 using docs/evaluation-index.md — exact format only"**
3. Agent loads **only** `evaluation-index.md` + `repository-inventory.md` (not full gap analysis)
4. Agent runs: `cd services/onboarding-api && PYTHONPATH=. .venv/bin/pytest -q`
5. Compare output to `docs/evaluation-matrix.md` row for B4

**Batch all 24:**  
`"Score B1–D6 from docs/evaluation-matrix.md; for any mismatch run verify command from evaluation-index.md"`

---

## MD File Size Rules (for speed)

| Rule | Why |
|------|-----|
| Start with `evaluation-index.md` (~120 lines) | Loads in seconds |
| Use `evaluation-matrix.md` for scores only | 1 table, 24 rows |
| Load `evaluation-gap-analysis.md` **one section at a time** | 426 lines total |
| Never load `evidence/**/coverage-html/**` | Thousands of files |
| Use `evidence/INDEX.md` for paths, not full tree | ~200 lines |

---

## Entry Point for Evaluators

| Role | First file |
|------|------------|
| Quick check | `docs/evaluation-index.md` |
| All scores | `docs/evaluation-matrix.md` |
| Single deep dive | `docs/evaluation-gap-analysis.md` § [ID] |
| Final verdict | `docs/final-evaluation-report.md` |
