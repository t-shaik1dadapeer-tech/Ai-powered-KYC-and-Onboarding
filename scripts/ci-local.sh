#!/usr/bin/env bash
# Local CI simulation — mirrors .github/workflows/ci.yml without Docker daemon requirement
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EVIDENCE="$ROOT/evidence/ci-results"
LOG="$EVIDENCE/phase-9-ci-local.txt"
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

mkdir -p "$EVIDENCE"
: > "$LOG"

log() { echo "$1" | tee -a "$LOG"; }

log "Local CI Run — $TIMESTAMP"
log "========================="
log ""

PASS=0
FAIL=0

run_step() {
  local name="$1"
  shift
  log "▶ $name"
  if "$@" >> "$LOG" 2>&1; then
    log "  ✅ PASS: $name"
    PASS=$((PASS + 1))
  else
    log "  ❌ FAIL: $name"
    FAIL=$((FAIL + 1))
  fi
  log ""
}

# --- Lint ---
run_step "ruff onboarding-api" bash -c "
  cd '$ROOT/services/onboarding-api'
  .venv/bin/ruff check app tests
"

run_step "ruff intelligence" bash -c "
  cd '$ROOT/engines/intelligence'
  .venv/bin/ruff check src tests
"

run_step "node lint" bash -c "
  cd '$ROOT/clients/node-cli'
  npm run lint
"

run_step "rust fmt + clippy" bash -c "
  source \"\$HOME/.cargo/env\" 2>/dev/null || true
  cd '$ROOT/engines/rust-analyzer'
  cargo fmt --check
  cargo clippy --all-targets -- -D warnings
"

# --- Tests ---
run_step "onboarding-api pytest" bash -c "
  cd '$ROOT/services/onboarding-api'
  PYTHONPATH=. .venv/bin/pytest -q --cov=app --cov-report=term-missing
"

run_step "intelligence pytest" bash -c "
  cd '$ROOT/engines/intelligence'
  PYTHONPATH=src .venv/bin/pytest -q
"

run_step "node-cli tests" bash -c "
  cd '$ROOT/clients/node-cli'
  npm test --silent
"

run_step "rust-analyzer cargo test" bash -c "
  source \"\$HOME/.cargo/env\" 2>/dev/null || true
  cd '$ROOT/engines/rust-analyzer'
  cargo test -q
  cargo build --release -q
"

run_step "platform e2e" bash -c "
  cd '$ROOT/services/onboarding-api'
  PYTHONPATH=. .venv/bin/pytest -q '$ROOT/tests/e2e/test_platform_e2e.py'
"

# --- Docker (optional) ---
if command -v docker >/dev/null 2>&1; then
  run_step "docker compose build" bash -c "
    cd '$ROOT/infra/docker'
    docker compose build
  "
else
  log "▶ docker compose build"
  log "  ⏭ SKIP: docker not installed"
  log ""
fi

log "========================="
log "TOTAL: $PASS passed, $FAIL failed"
log ""

if [[ "$FAIL" -gt 0 ]]; then
  exit 1
fi

log "✅ Local CI complete — evidence: $LOG"
