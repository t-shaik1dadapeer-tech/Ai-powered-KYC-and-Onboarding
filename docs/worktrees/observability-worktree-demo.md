# Observability Worktree Demo

Demonstrates parallel development on the **metrics / Grafana / Prometheus** stream while analysis work continues in a separate worktree.

## Branch

`observability-worktree`

## Owned scope

- `services/onboarding-api/app/core/metrics.py`
- `infra/prometheus/`, `infra/grafana/`
- `docs/observability/`
- `scripts/observability-verify.sh`, `scripts/generate-dashboard-evidence.py`

## Reproduce

```bash
cd "/Users/shaikdadapeer/agent development"

# Automated
make worktree-demo

# Manual steps
git checkout main
git checkout -b observability-worktree
git worktree add .worktrees/observability observability-worktree

cd .worktrees/observability
echo "observability-worktree demo" >> docs/observability/WORKTREE_MARKER.md
git add docs/observability/WORKTREE_MARKER.md
git commit -m "docs(observability): observability worktree demo marker"

# Verify metrics from this worktree
bash scripts/observability-verify.sh
```

## Demo commit (automated script)

Adds `docs/observability/WORKTREE_MARKER.md` with branch metadata — no changes to intelligence engine paths.

## Merge back to main

Merge **after** `analysis-worktree` per [merge-strategy.md](merge-strategy.md):

```bash
git checkout main
git merge --no-ff observability-worktree -m "merge: observability-worktree"
make observability-verify
```

## Agent workflow

When an agent is assigned **observability** tasks:

1. Work in `.worktrees/observability` on branch `observability-worktree`.
2. Instrument metrics in `app/core/metrics.py`; update Grafana JSON in `infra/grafana/dashboards/`.
3. Run `make observability-verify` before merge.
4. Avoid editing `engines/intelligence/src/` from this worktree.

## Docker + Grafana validation

With Docker Desktop:

```bash
make docker-up
open http://localhost:3000/d/kyc-platform   # admin/admin
make observability-verify
```

Capture live screenshot to `evidence/screenshots/grafana-live.png` (optional manual step).
