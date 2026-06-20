#!/usr/bin/env bash
# Bootstrap local dev environment — single command for fresh clone (D5)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Bootstrap — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "================================"

cd "$ROOT/services/onboarding-api"
python3 -m venv .venv
.venv/bin/pip install -q --upgrade pip
.venv/bin/pip install -q -r requirements.txt pytest pytest-cov pytest-asyncio httpx ruff
echo "  ✅ onboarding-api"

cd "$ROOT/engines/intelligence"
python3 -m venv .venv
.venv/bin/pip install -q --upgrade pip
.venv/bin/pip install -q -e ".[dev]" pytest-cov
echo "  ✅ intelligence"

cd "$ROOT/clients/node-cli"
npm install --silent
echo "  ✅ node-cli"

cd "$ROOT/engines/rust-analyzer"
# shellcheck disable=SC1091
source "$HOME/.cargo/env" 2>/dev/null || true
cargo build --release -q
echo "  ✅ rust-analyzer"

echo ""
echo "✅ Bootstrap complete — run: make test"
