# Parallel Development Strategy

**Evaluation:** A1 Multi Worktree Planning · A2 Parallel Worktrees  
**Implemented streams:** 2 (analysis, observability)  
**Extended plan:** 5 feature streams below

---

## Stream Overview

| Stream | Branch | Worktree path | Purpose |
|--------|--------|---------------|---------|
| **feature/api** | `feature/api` | `.worktrees/api` | FastAPI endpoints, schemas, services |
| **feature/worker** | `feature/worker` | `.worktrees/worker` | Async jobs (future — not implemented) |
| **feature/rust-engine** | `analysis-worktree` | `.worktrees/analysis` | Intelligence + Rust analyzer |
| **feature/devops** | `feature/devops` | `.worktrees/devops` | Docker, CI, K8s scaffold |
| **feature/observability** | `observability-worktree` | `.worktrees/observability` | Metrics, Grafana, Prometheus |

---

## feature/api

| Field | Detail |
|-------|--------|
| **Purpose** | KYC domain API changes |
| **Agent prompt** | "Work in `.worktrees/api` on branch `feature/api`. Edit only `services/onboarding-api/`. Run pytest before merge." |
| **Merge order** | 3rd (after rust-engine analysis tools stable) |
| **Conflict risk** | Medium — overlaps observability if both touch `metrics.py` |
| **Verification** | `cd services/onboarding-api && PYTHONPATH=. .venv/bin/pytest -q` |

---

## feature/worker

| Field | Detail |
|-------|--------|
| **Purpose** | Background KYC processing (planned — **no worker code exists**) |
| **Agent prompt** | "Scaffold Celery/ARQ worker in `workers/kyc-processor/`. Do not modify API routers without API stream approval." |
| **Merge order** | 5th (last) |
| **Conflict risk** | Low today (greenfield) |
| **Verification** | Worker unit tests + integration with Redis |

**Status:** NOT IMPLEMENTED — documented for evaluation planning only.

---

## feature/rust-engine (analysis-worktree)

| Field | Detail |
|-------|--------|
| **Purpose** | Repository intelligence + Rust scan |
| **Agent prompt** | "Analyze and extend `engines/intelligence/` and `engines/rust-analyzer/`. Output reports to `evidence/api-maps/`." |
| **Merge order** | 1st |
| **Conflict risk** | Low — isolated under `engines/` |
| **Verification** | `PYTHONPATH=src pytest`; `cargo test`; `generate-report` |

**Evidence:** `evidence/worktrees/phase-11-worktree-demo.txt`

---

## feature/devops

| Field | Detail |
|-------|--------|
| **Purpose** | Docker, CI, K8s scaffold, Terraform planning |
| **Agent prompt** | "Edit `infra/`, `.github/workflows/`, `scripts/docker-verify.sh`. Do not change application logic." |
| **Merge order** | 4th |
| **Conflict risk** | Low |
| **Verification** | `make ci-local`; `make docker-verify` |

---

## feature/observability (observability-worktree)

| Field | Detail |
|-------|--------|
| **Purpose** | Metrics, dashboards, observability docs |
| **Agent prompt** | "Extend `app/core/metrics.py`, `infra/grafana/`, `docs/observability/`. Run `make observability-verify`." |
| **Merge order** | 2nd |
| **Conflict risk** | Medium if API stream also touches metrics |
| **Verification** | `make observability-verify` |

---

## Git Worktree Commands

```bash
cd "/Users/shaikdadapeer/agent development"

# Automated demo (analysis + observability)
make worktree-demo

# Manual: create streams
git checkout main
git branch feature/api
git worktree add .worktrees/api feature/api

git branch feature/devops
git worktree add .worktrees/devops feature/devops

# List active worktrees
git worktree list

# Merge order (see docs/worktrees/merge-strategy.md)
git checkout main
git merge --no-ff analysis-worktree
git merge --no-ff observability-worktree

# Cleanup
git worktree remove .worktrees/analysis
git worktree remove .worktrees/observability
```

---

## Conflict Matrix

| Stream A | Stream B | Risk | Mitigation |
|----------|----------|------|------------|
| api | observability | **High** | Path ownership; merge observability first |
| api | devops | Low | Different dirs |
| rust-engine | api | Low | engines/ vs services/ |
| devops | observability | Medium | Both touch `infra/` — coordinate compose ports |

**Full playbook:** [docs/worktrees/merge-strategy.md](worktrees/merge-strategy.md)
