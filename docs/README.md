# Documentation Map

Two complementary taxonomies share this repo. Use the table below to pick the right entry point.

## Quick start

| Goal | Start here |
|------|------------|
| Evaluate all 24 criteria | [`evaluation-index.md`](evaluation-index.md) |
| Per-criterion deep reports | [`beginner/README.md`](beginner/README.md) |
| Phase 0–14 verification | [`../verification/README.md`](../verification/README.md) |
| Architecture (Phase 1) | [`architecture/README.md`](architecture/README.md) |
| Evidence catalog | [`../evidence/INDEX.md`](../evidence/INDEX.md) |
| Push to GitHub (one time) | [`GITHUB_SETUP.md`](GITHUB_SETUP.md) |

## Taxonomy

### 24-criterion framework (B / I / A / D)

Used for strict agent evaluation and hiring-style scoring.

| Prefix | Dimension | Reports |
|--------|-----------|---------|
| **B1–B6** | Beginner / discovery | [`beginner/B1-*`](beginner/) … [`B6-*`](beginner/) |
| **I1–I6** | Intermediate / integration | [`beginner/I1-*`](beginner/) … [`I6-*`](beginner/) |
| **A1–A6** | Advanced / agent workflows | [`beginner/A1-*`](beginner/) … [`A6-*`](beginner/) |
| **D1–D6** | DevOps / platform | [`beginner/D1-*`](beginner/) … [`D6-*`](beginner/) |

Supporting summaries (link to beginner reports, do not duplicate):

- [`evaluation-matrix.md`](evaluation-matrix.md) — scores table
- [`evaluation-gap-analysis.md`](evaluation-gap-analysis.md) — deep gap notes
- [`final-evaluation-report.md`](final-evaluation-report.md) — final grade

### Phase 0–14 pipeline

Used for incremental build verification and CI gates.

| Phase | Docs | Verification |
|-------|------|--------------|
| 0–1 | `evaluation/`, `architecture/` | `verification/phase-0.md`, `phase-1.md` |
| 2–14 | Root summaries in `docs/*.md` | `verification/phase-*.md` |

## Evidence layout (no duplicates)

| Path | Holds |
|------|-------|
| `evidence/api-maps/` | Inventories, API map, ER (canonical) |
| `evidence/flow-traces/` | Sequence diagrams, flow docs only |
| `evidence/test-results/` | Pytest/coverage logs + per-criterion run bundles |
| `evidence/evaluation-results/` | `full-24-audit-latest.txt` (24/24 proof) |

Regenerate index: `make evidence-index`
