#!/usr/bin/env bash
# Validate all verification/phase-{0..14}.md files exist with required sections
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EVIDENCE="$ROOT/evidence/verification"
LOG="$EVIDENCE/phase-12-audit.txt"
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

REQUIRED_SECTIONS=(
  "Agent Suggested"
  "Implemented"
  "Risk Assessment"
)

mkdir -p "$EVIDENCE"
: > "$LOG"

log() { echo "$1" | tee -a "$LOG"; }

log "Phase Verification Audit — $TIMESTAMP"
log "========================================"
log ""

PASS=0
FAIL=0
MISSING=0

for phase in $(seq 0 14); do
  FILE="$ROOT/verification/phase-${phase}.md"
  log "▶ Phase $phase: phase-${phase}.md"

  if [[ ! -f "$FILE" ]]; then
    log "  ❌ MISSING file"
    MISSING=$((MISSING + 1))
    FAIL=$((FAIL + 1))
    log ""
    continue
  fi

  SECTION_OK=true
  for section in "${REQUIRED_SECTIONS[@]}"; do
    if grep -q "## ${section}" "$FILE" || grep -q "## ${section}" "$FILE"; then
      :
    elif grep -qi "${section}" "$FILE"; then
      :
    else
      log "  ⚠ missing section: ${section}"
      SECTION_OK=false
    fi
  done

  # Check Agent Suggested and Implemented explicitly
  for section in "Agent Suggested" "Implemented"; do
    if ! grep -q "## ${section}" "$FILE"; then
      log "  ❌ required section missing: ${section}"
      SECTION_OK=false
    fi
  done

  # Risk Assessment — required for phase 12 gate (phases 13-14 have it in planned form)
  if ! grep -q "## Risk Assessment" "$FILE"; then
    log "  ❌ required section missing: Risk Assessment"
    SECTION_OK=false
  fi

  LINES=$(wc -l < "$FILE" | tr -d ' ')
  if [[ "$SECTION_OK" == true && "$LINES" -ge 20 ]]; then
    log "  ✅ OK ($LINES lines, required sections present)"
    PASS=$((PASS + 1))
  else
    log "  ❌ FAIL ($LINES lines)"
    FAIL=$((FAIL + 1))
  fi
  log ""
done

log "▶ Master audit document"
if [[ -f "$ROOT/docs/verification/agent-vs-manual-audit.md" ]]; then
  log "  ✅ docs/verification/agent-vs-manual-audit.md"
  PASS=$((PASS + 1))
else
  log "  ❌ MISSING agent-vs-manual-audit.md"
  FAIL=$((FAIL + 1))
fi

log ""
log "▶ Verification index"
if [[ -f "$ROOT/verification/README.md" ]]; then
  log "  ✅ verification/README.md"
else
  log "  ❌ MISSING verification/README.md"
  FAIL=$((FAIL + 1))
fi

log ""
log "========================================"
log "Phases checked: 15"
log "Phase files pass: $((PASS - 2)) / 15"  # subtract index + audit doc from pass count
log "Missing files: $MISSING"
log "Failures: $FAIL"

if [[ "$FAIL" -gt 0 ]]; then
  log ""
  log "❌ Audit FAILED"
  exit 1
fi

log ""
log "✅ All 15 verification files populated"
log "Evidence: $LOG"
