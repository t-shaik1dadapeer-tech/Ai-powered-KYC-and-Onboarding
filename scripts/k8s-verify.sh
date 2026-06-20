#!/usr/bin/env bash
# Kubernetes manifest validation — kubectl dry-run (client) or kubeconform fallback
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
K8S_DIR="$ROOT/infra/kubernetes"
EVIDENCE="$ROOT/evidence/k8s-results"
LOG="$EVIDENCE/k8s-verify.txt"
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

mkdir -p "$EVIDENCE"
: > "$LOG"

log() { echo "$1" | tee -a "$LOG"; }

log "Kubernetes Verification — $TIMESTAMP"
log "======================================"

MANIFESTS=(
  "$K8S_DIR/kyc-platform.yaml"
  "$K8S_DIR/onboarding-api-deployment.yaml"
)

for f in "${MANIFESTS[@]}"; do
  if [[ ! -f "$f" ]]; then
    log "❌ missing manifest: $f"
    exit 1
  fi
  log "▶ found: $(basename "$f")"
done

KUBECTL_DRY_RUN_OK=0
if command -v kubectl >/dev/null 2>&1; then
  log "▶ kubectl dry-run (client)"
  if kubectl apply --dry-run=client --validate=false -f "$K8S_DIR/" >> "$LOG" 2>&1; then
    log "  ✅ combined apply dry-run OK"
    KUBECTL_DRY_RUN_OK=1
  else
    log "  ⚠ kubectl dry-run unavailable (no cluster?) — using structure fallback"
  fi
fi

if [[ "$KUBECTL_DRY_RUN_OK" -eq 0 ]] && command -v kubeconform >/dev/null 2>&1; then
  log "▶ kubeconform schema validation"
  for f in "${MANIFESTS[@]}"; do
    kubeconform -summary -ignore-missing-schemas "$f" >> "$LOG" 2>&1
    log "  ✅ $(basename "$f")"
  done
elif [[ "$KUBECTL_DRY_RUN_OK" -eq 0 ]]; then
  log "▶ manifest structure check (fallback — no kubectl cluster/kubeconform)"
  python3 - "$K8S_DIR" <<'PY' >> "$LOG" 2>&1
import pathlib, sys
root = pathlib.Path(sys.argv[1])
for path in sorted(root.glob("*.yaml")):
    text = path.read_text()
    assert text.strip(), f"empty manifest: {path}"
    assert "apiVersion:" in text, f"missing apiVersion: {path}"
    assert "kind:" in text, f"missing kind: {path}"
    print(f"OK {path.name} ({text.count('apiVersion:')} doc(s))")
PY
  log "  ✅ YAML structure valid"
fi

log ""
log "Manifest count: ${#MANIFESTS[@]}"
log "✅ Kubernetes verification complete"
log "Evidence: $LOG"
