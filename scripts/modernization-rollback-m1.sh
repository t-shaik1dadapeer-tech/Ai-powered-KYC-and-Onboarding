#!/usr/bin/env bash
# Roll back A4 M1 — Node CLI X-API-Key support via git revert.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

COMMIT="${1:-}"
if [[ -z "$COMMIT" ]]; then
  echo "Usage: $0 <A4_COMMIT_SHA>"
  echo "Example: $0 abc1234"
  echo ""
  echo "Find SHA: git log --oneline --grep='A4: repository modernization'"
  exit 1
fi

echo "▶ Reverting A4 M1 commit: $COMMIT"
git revert --no-edit "$COMMIT"

echo ""
echo "▶ Verify Node tests"
cd clients/node-cli
npm test --silent

echo ""
echo "✅ Rollback complete. Review diff, then: git push origin main"
echo "See: docs/beginner/A4-repository-modernization/ROLLBACK.md"
