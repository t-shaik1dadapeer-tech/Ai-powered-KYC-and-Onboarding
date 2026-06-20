#!/usr/bin/env bash
# Push current branch to origin — assumes setup-github-auth.sh was run once.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BRANCH="${1:-$(git -C "$ROOT" branch --show-current)}"

cd "$ROOT"

if ! git remote get-url origin >/dev/null 2>&1; then
  echo "ERROR: no origin remote. Run: make setup-github" >&2
  exit 1
fi

echo "▶ Pushing branch '$BRANCH' to origin..."
git push -u origin "$BRANCH"
echo "✅ Push complete: $(git remote get-url origin) ($BRANCH)"
