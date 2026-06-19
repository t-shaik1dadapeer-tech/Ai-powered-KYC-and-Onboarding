# Evidence Store

All engineering claims in this project are backed by artifacts under `evidence/`.

## Quick links

| Resource | Path |
|----------|------|
| **Full index** | [INDEX.md](INDEX.md) — auto-generated catalog |
| Regenerate | `make evidence-index` |
| Verification | [verification/README.md](../verification/README.md) |
| Claim matrix | [docs/verification/agent-vs-manual-audit.md](../docs/verification/agent-vs-manual-audit.md) |

## Directory structure

```
evidence/
├── INDEX.md                 ← master catalog (Phase 13)
├── architecture/            ← Phase 0–1 design proof
├── api-maps/                ← Phase 3 analyzer output
├── flow-traces/             ← Phase 4 sequence + flow docs
├── diagrams/                ← ER / architecture exports
├── test-results/            ← Phases 2–7 pytest/cargo/node logs + coverage
├── docker-results/          ← Phase 8 compose validation
├── ci-results/              ← Phase 9 local CI logs
├── observability-results/   ← Phase 10 metrics snapshots
├── screenshots/             ← Phase 10 dashboard SVG
├── worktrees/               ← Phase 11 git worktree demo
└── verification/            ← Phase 12 audit output
```

## Conventions

- Phase verify scripts write timestamped logs to the matching subdirectory.
- Coverage HTML is generated locally; XML summaries are the canonical CI artifacts.
- Re-run `make evidence-index` after adding or refreshing phase evidence.
