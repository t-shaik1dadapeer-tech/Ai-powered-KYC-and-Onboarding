#!/usr/bin/env bash
# Run all platform test suites and store coverage in evidence/test-results/
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EVIDENCE="$ROOT/evidence/test-results"
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
SUMMARY="$EVIDENCE/phase-7-summary.txt"

mkdir -p "$EVIDENCE"

log() { echo "$1" | tee -a "$SUMMARY"; }

: > "$SUMMARY"
log "Platform Test Run — $TIMESTAMP"
log "========================================"
log ""

PASS=0
FAIL=0

run_suite() {
  local name="$1"
  shift
  log "▶ $name"
  if "$@" >> "$SUMMARY" 2>&1; then
    log "  ✅ PASS: $name"
    PASS=$((PASS + 1))
  else
    log "  ❌ FAIL: $name"
    FAIL=$((FAIL + 1))
  fi
  log ""
}

# --- FastAPI onboarding-api ---
run_suite "onboarding-api pytest + coverage" bash -c "
  cd '$ROOT/services/onboarding-api'
  PYTHONPATH=. .venv/bin/pytest -q --cov=app --cov-report=term-missing \
    --cov-report=xml:'$EVIDENCE/onboarding-api-coverage.xml' \
    --cov-report=html:'$EVIDENCE/onboarding-api-coverage-html'
"

# --- Intelligence engine ---
run_suite "intelligence pytest + coverage" bash -c "
  cd '$ROOT/engines/intelligence'
  PYTHONPATH=src .venv/bin/pytest -q --cov=intelligence --cov-report=term-missing \
    --cov-report=xml:'$EVIDENCE/intelligence-coverage.xml' \
    --cov-report=html:'$EVIDENCE/intelligence-coverage-html' 2>/dev/null || \
  PYTHONPATH=src .venv/bin/pytest -q
"

# --- Node CLI ---
run_suite "node-cli tests" bash -c "
  cd '$ROOT/clients/node-cli'
  npm test --silent
"

# --- Rust analyzer ---
run_suite "rust-analyzer cargo test" bash -c "
  source \"\$HOME/.cargo/env\" 2>/dev/null || true
  cd '$ROOT/engines/rust-analyzer'
  cargo test -q
"

# --- Platform E2E ---
run_suite "platform e2e tests" bash -c "
  cd '$ROOT/services/onboarding-api'
  PYTHONPATH=. .venv/bin/pip install -q pytest httpx fastapi 2>/dev/null || true
  PYTHONPATH=. .venv/bin/pytest -q '$ROOT/tests/e2e/test_platform_e2e.py'
"

log "========================================"
log "TOTAL: $PASS passed, $FAIL failed"
log ""

if [[ "$FAIL" -gt 0 ]]; then
  exit 1
fi
