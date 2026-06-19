#!/usr/bin/env bash
# Safe-change gate — run before every PR (lint → test → infra validate)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EVIDENCE="$ROOT/evidence/safe-change"
LOG="$EVIDENCE/safe-change-check.txt"
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

mkdir -p "$EVIDENCE"
: > "$LOG"

log() { echo "$1" | tee -a "$LOG"; }

log "Safe Change Check — $TIMESTAMP"
log "=============================="

cd "$ROOT"

log "▶ 1/5 ci-local (lint + tests + build)"
make ci-local >> "$LOG" 2>&1
log "  ✅ ci-local passed"

log "▶ 2/5 terraform validate"
bash scripts/terraform-verify.sh >> "$LOG" 2>&1
log "  ✅ terraform passed"

log "▶ 3/5 kubernetes dry-run"
bash scripts/k8s-verify.sh >> "$LOG" 2>&1
log "  ✅ k8s passed"

log "▶ 4/5 docker compose config"
if command -v docker >/dev/null 2>&1; then
  docker compose -f infra/docker/docker-compose.yml config --quiet >> "$LOG" 2>&1
  log "  ✅ docker compose config valid"
else
  log "  ⚠ docker not available — skipped (compose file present)"
fi

log "▶ 5/5 load test (in-process)"
bash scripts/load-test.sh >> "$LOG" 2>&1
log "  ✅ load test passed"

log ""
log "✅ Safe change check complete — safe to open PR"
log "Evidence: $LOG"
