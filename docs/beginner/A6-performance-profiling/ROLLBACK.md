# A6 Rollback — Rust Scan Single-Read Optimization

Use this runbook to undo the A6 performance improvement (single-read scan pipeline in `engines/rust-analyzer`).

## When to roll back

- Scan output or risk scores differ from expected after the optimization
- Memory pressure from caching file contents in the scan loop
- Need to restore pre-A6 scan behavior for comparison

## Option A — After A6 commit is on `main` (preferred)

```bash
cd "/Users/shaikdadapeer/agent development"
git log --oneline -5   # find commit: A6: performance profiling
git revert --no-edit <A6_COMMIT_SHA>
cd engines/rust-analyzer && cargo test
make test-rust test-intelligence test-e2e
git push origin main
```

## Option B — Script (revert by commit SHA)

```bash
bash scripts/performance-rollback-a6.sh <A6_COMMIT_SHA>
```

## Option C — Restore Rust files only (uncommitted / local)

```bash
git checkout origin/main -- \
  engines/rust-analyzer/src/scan.rs \
  engines/rust-analyzer/src/risk/mod.rs \
  engines/rust-analyzer/src/parser/mod.rs \
  engines/rust-analyzer/src/parser/universal.rs
cd engines/rust-analyzer && cargo test
```

## Post-rollback behavior

| Metric | Expected change |
|--------|-----------------|
| `scan_duration_ms` | Increases (~40% mean on onboarding-api, 60 files) |
| `ScanResult` JSON schema | Unchanged |
| Risk scores | Should match pre-A6 (same regex semantics) |

## Verification after rollback

```bash
cd engines/rust-analyzer
cargo test
cargo build --release
./target/release/rust-analyzer scan --path ../../services/onboarding-api
make test-rust test-e2e
```
