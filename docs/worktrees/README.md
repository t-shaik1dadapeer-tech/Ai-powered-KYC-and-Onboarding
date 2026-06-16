# Git Worktrees — Parallel Agent Development

This project demonstrates **A1: Worktree-based Parallel Development** — running two feature streams in isolated working directories without branch-switching overhead.

## Streams

| Worktree branch | Purpose | Typical paths |
|-----------------|---------|---------------|
| `analysis-worktree` | Repository intelligence, flow tracing, Rust analyzer | `engines/intelligence/`, `engines/rust-analyzer/` |
| `observability-worktree` | Metrics, Grafana, Prometheus | `infra/grafana/`, `docs/observability/`, `app/core/metrics.py` |

## Quick start

```bash
# Full reproducible demo (init → worktrees → commits → merge)
make worktree-demo

# Or manually
bash scripts/worktree-demo.sh
```

## Documentation

| Doc | Description |
|-----|-------------|
| [merge-strategy.md](merge-strategy.md) | Merge order, conflict resolution, cleanup |
| [analysis-worktree-demo.md](analysis-worktree-demo.md) | Analysis stream walkthrough |
| [observability-worktree-demo.md](observability-worktree-demo.md) | Observability stream walkthrough |

## Architecture alignment

Parallel streams match the roadmap (Phase 11, `docs/architecture/06-development-roadmap.md` §4):

- **Intelligence stream:** P3 → P4 → P6
- **Ops stream:** P8 → P9 → P10

Worktrees let agents (or developers) work on both simultaneously without stashing or conflicting uncommitted changes.
