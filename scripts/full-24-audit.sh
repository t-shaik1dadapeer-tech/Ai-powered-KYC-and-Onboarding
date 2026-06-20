#!/usr/bin/env bash
# Run all 24 evaluation criteria verify commands from docs/evaluation-index.md
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AUDIT="${ROOT}/evidence/evaluation-results/full-24-audit-$(date +%Y-%m-%d-%H%M).txt"
mkdir -p "${ROOT}/evidence/evaluation-results"

PASS=0
FAIL=0

log() { echo "$@" | tee -a "$AUDIT"; }

run_check() {
  local id="$1" name="$2" cmd="$3"
  log "--- ${id} ${name} ---"
  log "CMD: ${cmd}"
  if (cd "${ROOT}" && eval "${cmd}") >>"$AUDIT" 2>&1; then
    log "RESULT: PASS"
    PASS=$((PASS + 1))
  else
    log "RESULT: FAIL"
    FAIL=$((FAIL + 1))
  fi
  log ""
}

: >"$AUDIT"
log "=== Full 24-Criterion Audit ==="
log "Started: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
log "Root: ${ROOT}"
log ""

run_check "B1" "Repo Discovery" \
  "cd engines/intelligence && PYTHONPATH=src .venv/bin/pytest tests/test_analyzer.py -q"
run_check "B2" "API Mapping" \
  "test -f docs/api/openapi.json && jq '.paths | keys | length' docs/api/openapi.json"
run_check "B3" "Test Discovery" "make test"
run_check "B4" "FastAPI Greenfield" \
  "cd services/onboarding-api && PYTHONPATH=. .venv/bin/pytest -q"
run_check "B5" "Node.js Greenfield" "cd clients/node-cli && npm test --silent"
run_check "B6" "Rust Greenfield" "cd engines/rust-analyzer && cargo test -q"
run_check "I1" "ER Diagram" "grep ForeignKey services/onboarding-api/app/models/*.py"
run_check "I2" "E2E Flow Trace" \
  "test \$(ls evidence/flow-traces/onboarding-api/sequence-diagrams/*.mmd 2>/dev/null | wc -l | tr -d ' ') -ge 1"
run_check "I3" "Safe Change" "make safe-change-check"
run_check "I4" "Polyglot Service Pair" \
  "cd services/onboarding-api && PYTHONPATH=. .venv/bin/pytest ../../tests/e2e/test_platform_e2e.py -q"
run_check "I5" "Dockerization" "make docker-verify"
run_check "I6" "Bug Diagnosis" "grep BUG-001 docs/bug-investigation.md"
run_check "A1" "Multi Worktree Planning" "test -f docs/worktrees/merge-strategy.md"
run_check "A2" "Parallel Worktrees" "make worktree-demo"
run_check "A3" "Polyglot Mini-System" "make test"
run_check "A4" "Repository Modernization" "test -f .github/dependabot.yml"
run_check "A5" "Agent Code Review" "make ci-local"
run_check "A6" "Performance Profiling" "make load-test"
run_check "D1" "Terraform" "make terraform-verify"
run_check "D2" "Docker Compose" \
  "docker compose -f infra/docker/docker-compose.yml config >/dev/null"
run_check "D3" "CI/CD" "make ci-local"
run_check "D4" "Kubernetes" "make k8s-verify"
run_check "D5" "Reproducible Environment" "make test"
run_check "D6" "Observability" "make observability-verify"

log "=== SUMMARY ==="
log "PASS: ${PASS} / 24"
log "FAIL: ${FAIL} / 24"
log "Finished: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
log "Report: ${AUDIT}"

LATEST="${ROOT}/evidence/evaluation-results/full-24-audit-latest.txt"
cp "$AUDIT" "$LATEST"
log "Latest: ${LATEST}"

if [[ "${FAIL}" -gt 0 ]]; then
  exit 1
fi
