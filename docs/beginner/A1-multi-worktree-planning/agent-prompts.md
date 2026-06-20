# A1 Agent Prompts — Parallel Lanes

## Lane L1 — analysis-worktree

```
You are working in worktree `.worktrees/analysis` on branch `analysis-worktree`.

SCOPE: Only edit `engines/intelligence/`, `engines/rust-analyzer/`, `evidence/api-maps/`, `evidence/flow-traces/`.

TASK: Extend repository intelligence (new extractors, flow traces, or rust scan rules).

CONSTRAINTS:
- Do NOT modify `services/onboarding-api/app/core/metrics.py` or `infra/grafana/`.
- Run: `cd engines/intelligence && PYTHONPATH=src pytest -q` and `cd engines/rust-analyzer && cargo test -q`.
- Commit message prefix: `feat(intelligence):` or `feat(rust-analyzer):`.

DELIVERABLE: Updated reports under `evidence/api-maps/` or `evidence/flow-traces/`.
```

## Lane L2 — observability-worktree

```
You are working in worktree `.worktrees/observability` on branch `observability-worktree`.

SCOPE: `infra/prometheus/`, `infra/grafana/`, `docs/observability/`, `services/onboarding-api/app/core/metrics.py`.

TASK: Add or refine Prometheus metrics and Grafana dashboards for KYC flows.

CONSTRAINTS:
- Do NOT edit `engines/intelligence/src/`.
- Run `make observability-verify` before requesting merge.
- Coordinate if adding new metric names — document in `docs/observability/metrics-catalog.md`.

DELIVERABLE: Dashboard JSON + metrics catalog update + verification evidence.
```

## Lane L3 — feature/api-migrations

```
You are working in worktree `.worktrees/api-migrations` on branch `feature/api-migrations`.

SCOPE: `services/onboarding-api/` only (alembic, models, migration tests).

TASK: Add Alembic migrations replacing `Base.metadata.create_all()` for production schema versioning.

CONSTRAINTS:
- Do not change Node CLI or infra in this lane.
- Keep routers → services → repositories layering.
- Run: `cd services/onboarding-api && PYTHONPATH=. .venv/bin/pytest -q`.

DELIVERABLE: `alembic/` directory, initial revision, README migration section.
```

## Lane L4 — feature/cli-auth

```
You are working in worktree `.worktrees/cli-auth` on branch `feature/cli-auth`.

SCOPE: `clients/node-cli/` only.

TASK: Add `--api-key` / `API_KEY` env support to ApiClient (`X-API-Key` header).

CONSTRAINTS:
- Do not modify FastAPI server code in this lane (assume API already accepts X-API-Key).
- Run `npm test` in clients/node-cli.
- Match error JSON parsing in `lib/api-client.js`.

DELIVERABLE: CLI flag, tests, README update for auth-enabled API.
```

## Lane L5 — feature/devops

```
You are working in worktree `.worktrees/devops` on branch `feature/devops`.

SCOPE: `infra/`, `.github/workflows/`, `scripts/docker-verify.sh` (no app business logic).

TASK: Wire API_KEY and DATABASE_URL via compose secrets / k8s Secret refs.

CONSTRAINTS:
- Do not change `app/services/` or `engines/`.
- Run `make docker-verify` and `make k8s-verify` after changes.

DELIVERABLE: Updated compose/k8s manifests + devops-validation evidence.
```
