# Analysis Worktree Demo

Demonstrates parallel development on the **repository intelligence** stream without blocking observability work.

## Branch

`analysis-worktree`

## Owned scope

- `engines/intelligence/` — detectors, extractors, flow tracing
- `engines/rust-analyzer/` — high-performance scan engine
- `evidence/api-maps/`, `evidence/flow-traces/`

## Reproduce

```bash
cd "/Users/shaikdadapeer/agent development"

# Automated (creates worktree, commit, merge)
make worktree-demo

# Manual steps
git checkout -b analysis-worktree
git worktree add .worktrees/analysis analysis-worktree

cd .worktrees/analysis
# Make changes isolated to intelligence engine
echo "analysis-worktree demo" >> engines/intelligence/WORKTREE_MARKER.md
git add engines/intelligence/WORKTREE_MARKER.md
git commit -m "docs(intelligence): analysis worktree demo marker"

# Verify analyzer still works from this worktree
cd engines/intelligence
PYTHONPATH=src ../../services/onboarding-api/../.venv/bin/python -m intelligence.cli \
  ../../services/onboarding-api -o /tmp/analysis-wt 2>/dev/null || \
  PYTHONPATH=src python3 -m intelligence.cli ../../services/onboarding-api -o /tmp/analysis-wt
```

## Demo commit (automated script)

The worktree demo adds `engines/intelligence/WORKTREE_MARKER.md` documenting:

- Branch name and purpose
- Timestamp of demo run
- Isolation guarantee (no metrics/infra edits)

## Merge back to main

```bash
git checkout main
git merge --no-ff analysis-worktree -m "merge: analysis-worktree"
```

See [merge-strategy.md](merge-strategy.md) for conflict handling if observability branch touched shared files.

## Agent workflow

When an agent is assigned **intelligence** tasks:

1. Confirm `git worktree list` shows `.worktrees/analysis` on `analysis-worktree`.
2. Edit only under `engines/` and intelligence evidence paths.
3. Run `PYTHONPATH=src pytest` in `engines/intelligence/`.
4. Merge to `main` when phase gate passes; do not merge observability changes in same PR.
