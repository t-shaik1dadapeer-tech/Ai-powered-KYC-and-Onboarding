#!/usr/bin/env bash
# Phase 14 final review validation — confirms scorecard prerequisites
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EVIDENCE="$ROOT/evidence/final-review"
LOG="$EVIDENCE/phase-14-final-review.txt"
REVIEW="$ROOT/docs/final-review.md"
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

mkdir -p "$EVIDENCE"
: > "$LOG"

log() { echo "$1" | tee -a "$LOG"; }

log "Final Review Validation — $TIMESTAMP"
log "======================================"
log ""

PASS=0
FAIL=0

check() {
  local name="$1"
  shift
  log "▶ $name"
  if "$@" >> "$LOG" 2>&1; then
    log "  ✅ PASS"
    PASS=$((PASS + 1))
  else
    log "  ❌ FAIL"
    FAIL=$((FAIL + 1))
  fi
  log ""
}

log "▶ Final review document"
if [[ -f "$REVIEW" ]]; then
  LINES=$(wc -l < "$REVIEW" | tr -d ' ')
  log "  ✅ docs/final-review.md ($LINES lines)"
  PASS=$((PASS + 1))
else
  log "  ❌ MISSING docs/final-review.md"
  FAIL=$((FAIL + 1))
fi
log ""

check "Verification files (15 phases)" bash "$ROOT/scripts/verify-all-phases.sh"
check "Evidence index" bash "$ROOT/scripts/evidence-index.sh"

log "▶ Scorecard sections in final-review.md"
for section in "Dimension Scorecard" "Gap Analysis" "Phase Completion Matrix" "Comparison to Phase 0"; do
  if grep -q "$section" "$REVIEW"; then
    log "  ✅ $section"
  else
    log "  ❌ missing: $section"
    FAIL=$((FAIL + 1))
  fi
done
log ""

log "▶ Dimension coverage in scorecard"
for id in B1 B2 B3 B4 B5 B6 I1 I2 I3 I4 I5 I6 A1 A2 D2 D3 D4 D5 D6; do
  if grep -q "$id" "$REVIEW"; then
    :
  else
    log "  ❌ missing dimension: $id"
    FAIL=$((FAIL + 1))
  fi
done
log "  ✅ All 19 evaluation IDs referenced"
log ""

log "======================================"
log "Checks passed: $PASS"
log "Failures: $FAIL"

if [[ "$FAIL" -gt 0 ]]; then
  log "❌ Final review validation FAILED"
  exit 1
fi

log "✅ Final review validation COMPLETE"
log "Scorecard: $REVIEW"
log "Log: $LOG"
