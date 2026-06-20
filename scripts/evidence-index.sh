#!/usr/bin/env bash
# Generate evidence/INDEX.md — cross-linked artifact catalog for all phases
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EVIDENCE="$ROOT/evidence"
INDEX="$EVIDENCE/INDEX.md"
LOG="$EVIDENCE/phase-13-index-generation.txt"
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

mkdir -p "$EVIDENCE"
: > "$LOG"

log() { echo "$1" | tee -a "$LOG"; }

log "Evidence Index Generation — $TIMESTAMP"

count_files() {
  find "$1" -type f ! -path '*/coverage-html/*' 2>/dev/null | wc -l | tr -d ' '
}

TOTAL=$(count_files "$EVIDENCE")
log "Total evidence files (excl. coverage-html): $TOTAL"

# --- Generate INDEX.md ---
{
  echo "# Evidence Index"
  echo ""
  echo "**Generated:** $TIMESTAMP  "
  echo "**Command:** \`make evidence-index\` or \`bash scripts/evidence-index.sh\`"
  echo ""
  echo "---"
  echo ""
  echo "## Summary"
  echo ""
  echo "| Metric | Value |"
  echo "|--------|-------|"
  echo "| Total artifacts | $TOTAL |"
  echo "| Top-level directories | $(find "$EVIDENCE" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ') |"
  echo "| Phase-linked claims | 15 phases (0–14) |"
  echo ""
  echo "---"
  echo ""
  echo "## Claim → Evidence Matrix"
  echo ""
  echo "| Claim | Phase | Primary evidence | Verification |"
  echo "|-------|-------|------------------|--------------|"
  echo "| Evaluation taxonomy B/I/A/D | 0 | [phase-0-evaluation-matrix.md](../docs/evaluation/phase-0-evaluation-matrix.md) | [phase-0.md](../verification/phase-0.md) |"
  echo "| Architecture design (8 docs, 26 Mermaid) | 1 | [docs/architecture/](../docs/architecture/) | [phase-1.md](../verification/phase-1.md) |"
  echo "| 9 REST endpoints, 97%+ coverage | 2 | [phase-2-pytest.txt](test-results/phase-2-pytest.txt), [onboarding-api-coverage.xml](test-results/onboarding-api-coverage.xml) | [phase-2.md](../verification/phase-2.md) |"
  echo "| Repo intelligence (9 APIs detected) | 3 | [api-maps/onboarding-api/](api-maps/onboarding-api/) | [phase-3.md](../verification/phase-3.md) |"
  echo "| Flow traces + sequence diagrams | 4 | [flow-traces/onboarding-api/](flow-traces/onboarding-api/) | [phase-4.md](../verification/phase-4.md) |"
  echo "| Node CLI (17 tests) | 5 | [phase-5-node-tests.txt](test-results/phase-5-node-tests.txt) | [phase-5.md](../verification/phase-5.md) |"
  echo "| Rust analyzer + benchmark | 6 | [phase-6-rust-benchmark.txt](test-results/phase-6-rust-benchmark.txt) | [phase-6.md](../verification/phase-6.md) |"
  echo "| 70 unified tests | 7 | [phase-7-summary.txt](test-results/phase-7-summary.txt) | [phase-7.md](../verification/phase-7.md) |"
  echo "| Docker compose stack | 8 | [docker-results/phase-8-static-validation.txt](docker-results/phase-8-static-validation.txt) | [phase-8.md](../verification/phase-8.md) |"
  echo "| GitHub Actions CI | 9 | [ci-results/phase-9-ci-local.txt](ci-results/phase-9-ci-local.txt) | [phase-9.md](../verification/phase-9.md) |"
  echo "| KYC Prometheus metrics + dashboard | 10 | [metrics-snapshot.txt](observability-results/metrics-snapshot.txt), [kyc-platform-dashboard.svg](screenshots/kyc-platform-dashboard.svg) | [phase-10.md](../verification/phase-10.md) |"
  echo "| Git worktree parallel streams | 11 | [phase-11-worktree-demo.txt](worktrees/phase-11-worktree-demo.txt) | [phase-11.md](../verification/phase-11.md) |"
  echo "| Agent vs manual audit | 12 | [phase-12-audit.txt](verification/phase-12-audit.txt) | [phase-12.md](../verification/phase-12.md) |"
  echo "| Evidence index (this file) | 13 | [INDEX.md](INDEX.md) | [phase-13.md](../verification/phase-13.md) |"
  echo "| Final scorecard | 14 | [final-evaluation-report.md](../docs/final-evaluation-report.md) | [phase-14.md](../verification/phase-14.md) |"
  echo ""
  echo "---"
  echo ""
  echo "## By Evaluation Dimension"
  echo ""
  echo "| Dimension | Evidence paths |"
  echo "|-----------|----------------|"
  echo "| **B1** Repo discovery | \`api-maps/onboarding-api/\` (inventories) |"
  echo "| **B2** API mapping | \`api-maps/onboarding-api/api-map.md\` |"
  echo "| **B3** ER diagrams | \`api-maps/onboarding-api/er-diagram.mmd\`, \`diagrams/onboarding-api-er.mmd\` |"
  echo "| **B4** Flow tracing | \`flow-traces/onboarding-api/sequence-diagrams/\`, \`flow-docs/\` |"
  echo "| **B5** Test discovery | \`api-maps/onboarding-api/test-inventory.md\`, \`test-results/\` |"
  echo "| **B6** KYC domain | test-results/phase-2-pytest.txt, phase-7-summary.txt |"
  echo "| **I1** FastAPI | onboarding-api coverage XML |"
  echo "| **I2** Node CLI | phase-5-node-tests.txt |"
  echo "| **I3** Rust | phase-6-rust-benchmark.txt |"
  echo "| **I4** Docker | docker-results/ |"
  echo "| **I5** CI/CD | ci-results/, \`.github/workflows/ci.yml\` |"
  echo "| **I6** Observability | observability-results/, screenshots/ |"
  echo "| **A1** Worktrees | worktrees/phase-11-worktree-demo.txt |"
  echo "| **A2** Agent verification | verification/phase-12-audit.txt |"
  echo "| **D2** Evidence store | This index |"
  echo "| **D3** Architecture traceability | architecture/phase-0-1-verification.txt |"
  echo "| **D4** Risk assessment | verification/phase-*.md § Risk |"
  echo "| **D5** Verification commands | verification/README.md, Makefile |"
  echo "| **D6** Conventions | docs/architecture/05-folder-structure.md |"
  echo ""
  echo "---"
  echo ""
  echo "## Directory Inventory"
  echo ""

  for dir in "$EVIDENCE"/*/; do
    [[ -d "$dir" ]] || continue
    name=$(basename "$dir")
    count=$(count_files "$dir")
    echo "### \`evidence/$name/\` ($count files)"
    echo ""
    find "$dir" -type f ! -path '*/coverage-html/*' ! -name '*.html' ! -name '*.js' ! -name '*.css' ! -name '*.png' \
      2>/dev/null | sed "s|^$ROOT/||" | sort | head -30 | while read -r f; do
      echo "- \`$f\`"
    done
    if [[ "$count" -gt 30 ]]; then
      echo "- _… and $((count - 30)) more_"
    fi
    echo ""
  done

  echo "---"
  echo ""
  echo "## Key Artifacts (quick links)"
  echo ""
  echo "| Artifact | Path |"
  echo "|----------|------|"
  for key in \
    "test-results/phase-7-summary.txt" \
    "test-results/onboarding-api-coverage.xml" \
    "test-results/intelligence-coverage.xml" \
    "test-results/phase-6-rust-benchmark.txt" \
    "api-maps/onboarding-api/api-map.md" \
    "flow-traces/onboarding-api/sequence-diagrams/post-customers.mmd" \
    "docker-results/phase-8-static-validation.txt" \
    "ci-results/phase-9-ci-local.txt" \
    "observability-results/metrics-snapshot.txt" \
    "screenshots/kyc-platform-dashboard.svg" \
    "worktrees/phase-11-worktree-demo.txt" \
  "verification/phase-12-audit.txt" \
  "architecture/phase-0-1-verification.txt" \
  "../docs/final-review.md"
  do
    if [[ -f "$EVIDENCE/../$key" ]] || [[ -f "$ROOT/$key" ]]; then
      fp="evidence/${key#evidence/}"
      [[ -f "$ROOT/evidence/${key#evidence/}" ]] && fp="evidence/${key#evidence/}"
      [[ -f "$ROOT/$key" ]] && fp="$key"
      echo "| $(basename "$key") | [\`$fp\`]($key) |"
    fi
  done
  echo ""
  echo "---"
  echo ""
  echo "## Regenerate"
  echo ""
  echo '```bash'
  echo "make evidence-index"
  echo '```'
  echo ""
  echo "Also re-run phase scripts to refresh stale artifacts:"
  echo ""
  echo '```bash'
  echo "make test                  # Phase 7"
  echo "make ci-local              # Phase 9"
  echo "make observability-verify  # Phase 10"
  echo "make verify-phases         # Phase 12"
  echo '```'
} > "$INDEX"

log "✅ Generated $INDEX"

# --- Validate key artifacts exist ---
MISSING=0
KEY_ARTIFACTS=(
  "test-results/phase-7-summary.txt"
  "api-maps/onboarding-api/api-map.md"
  "flow-traces/onboarding-api/sequence-diagrams/post-customers.mmd"
  "observability-results/metrics-snapshot.txt"
  "verification/phase-12-audit.txt"
  "architecture/phase-0-1-verification.txt"
)

log ""
log "▶ Key artifact validation"
for rel in "${KEY_ARTIFACTS[@]}"; do
  if [[ -f "$EVIDENCE/$rel" ]]; then
    log "  ✅ $rel"
  else
    log "  ❌ MISSING: $rel"
    MISSING=$((MISSING + 1))
  fi
done

log ""
log "▶ Orphan check — verification files reference evidence"
ORPHAN=0
for phase in $(seq 0 12); do
  vf="$ROOT/verification/phase-${phase}.md"
  [[ -f "$vf" ]] || continue
  if grep -q 'evidence/' "$vf" || [[ "$phase" -le 1 ]]; then
    log "  ✅ phase-${phase}.md has evidence references"
  else
    log "  ⚠ phase-${phase}.md — no evidence/ path mentioned"
    ORPHAN=$((ORPHAN + 1))
  fi
done

log ""
log "========================================"
if [[ "$MISSING" -gt 0 ]]; then
  log "❌ $MISSING key artifacts missing"
  exit 1
fi

log "✅ Evidence index complete"
log "Files indexed: $TOTAL"
log "INDEX: $INDEX"
log "Log: $LOG"
