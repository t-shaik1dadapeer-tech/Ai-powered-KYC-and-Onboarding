#!/usr/bin/env bash
# Roll back A6 — rust-analyzer single-read scan optimization via git revert.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

COMMIT="${1:-}"
if [[ -z "$COMMIT" ]]; then
  echo "Usage: $0 <A6_COMMIT_SHA>"
  echo "Example: $0 abc1234"
  echo ""
  echo "Find SHA: git log --oneline --grep='A6: performance profiling'"
  exit 1
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "❌ Working tree not clean. Commit or stash changes before rollback."
  exit 1
fi

echo "▶ Reverting A6 commit: $COMMIT"
git revert --no-edit "$COMMIT"

echo ""
echo "▶ Verify Rust tests"
cd engines/rust-analyzer
cargo test -q

echo ""
echo "✅ Rollback complete. Review diff, then: git push origin main"
echo "See: docs/beginner/A6-performance-profiling/ROLLBACK.md"
