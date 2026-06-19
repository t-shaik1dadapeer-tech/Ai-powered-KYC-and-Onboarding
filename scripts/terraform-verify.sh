#!/usr/bin/env bash
# Terraform init, validate, apply (local provider — no cloud credentials)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TF_DIR="$ROOT/infra/terraform"
EVIDENCE="$ROOT/evidence/terraform-results"
LOG="$EVIDENCE/terraform-verify.txt"
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

mkdir -p "$EVIDENCE" "$TF_DIR/.generated"
: > "$LOG"

log() { echo "$1" | tee -a "$LOG"; }

log "Terraform Verification — $TIMESTAMP"
log "====================================="

TF_CMD="terraform"
if ! command -v terraform >/dev/null 2>&1; then
  TOOLS_TF="$ROOT/.tools/terraform"
  if [[ ! -x "$TOOLS_TF" ]]; then
    log "▶ downloading terraform binary to .tools/"
    mkdir -p "$ROOT/.tools"
    ARCH="$(uname -m)"
    case "$ARCH" in
      arm64|aarch64) TF_ARCH="arm64" ;;
      *) TF_ARCH="amd64" ;;
    esac
    OS="$(uname -s | tr '[:upper:]' '[:lower:]')"
    TF_ZIP="terraform_1.9.8_${OS}_${TF_ARCH}.zip"
    curl -fsSL "https://releases.hashicorp.com/terraform/1.9.8/${TF_ZIP}" -o "$ROOT/.tools/${TF_ZIP}"
    unzip -o -q "$ROOT/.tools/${TF_ZIP}" -d "$ROOT/.tools"
    rm -f "$ROOT/.tools/${TF_ZIP}"
    chmod +x "$TOOLS_TF"
  fi
  TF_CMD="$TOOLS_TF"
fi

cd "$TF_DIR"

log "▶ terraform init"
"$TF_CMD" init -input=false >> "$LOG" 2>&1
log "  ✅ init OK"

log "▶ terraform validate"
"$TF_CMD" validate >> "$LOG" 2>&1
log "  ✅ validate OK"

log "▶ terraform apply (local_file resources)"
"$TF_CMD" apply -auto-approve -input=false >> "$LOG" 2>&1
log "  ✅ apply OK"

log "▶ outputs"
"$TF_CMD" output -json >> "$LOG" 2>&1
"$TF_CMD" output -json > "$EVIDENCE/terraform-outputs.json"

REGISTRY="$TF_DIR/.generated/infra-registry.json"
if [[ -f "$REGISTRY" ]]; then
  log "  ✅ registry: $REGISTRY"
  cp "$REGISTRY" "$EVIDENCE/infra-registry.json"
else
  log "  ❌ missing registry output"
  exit 1
fi

log ""
log "✅ Terraform verification complete"
log "Evidence: $LOG"
