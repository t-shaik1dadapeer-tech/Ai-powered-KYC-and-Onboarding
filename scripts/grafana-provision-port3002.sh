#!/usr/bin/env bash
# Provision KYC dashboard into D6 folder on Grafana :3002 (d6-grafana) — no API token needed
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT/infra/docker/.env"
EVIDENCE="$ROOT/evidence/observability-results"
LOG="$EVIDENCE/grafana-import.txt"
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

mkdir -p "$EVIDENCE"
: > "$LOG"

log() { echo "$1" | tee -a "$LOG"; }

if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ENV_FILE"
  set +a
fi

D6_DASHBOARDS="${D6_GRAFANA_DASHBOARDS:-$HOME/Evil-Ai/devops/D6-observability/monitoring/grafana/dashboards}"
D6_PROVISIONING="${D6_GRAFANA_PROVISIONING:-$HOME/Evil-Ai/devops/D6-observability/monitoring/grafana/provisioning}"
GRAFANA_URL="${GRAFANA_URL:-http://127.0.0.1:3002}"
D6_CONTAINER="${D6_GRAFANA_CONTAINER:-d6-grafana}"
KYC_DASH_SRC="$ROOT/infra/grafana/dashboards/kyc-platform.json"
# Same folder as api-observability.json → both appear under D6
KYC_DASH_DEST="$D6_DASHBOARDS/ai-powered-kyc-platform-api.json"

log "Grafana :3002 D6 folder provision — $TIMESTAMP"
log ""

if [[ ! -d "$D6_DASHBOARDS" ]]; then
  log "❌ D6 dashboards path not found: $D6_DASHBOARDS"
  exit 1
fi

log "▶ Copy KYC dashboard into D6 folder (alongside API Observability)"
python3 - "$KYC_DASH_SRC" "$KYC_DASH_DEST" <<'PY'
import json, sys
src, dest = sys.argv[1:3]
dash = json.load(open(src))
for panel in dash.get("panels", []):
    panel["datasource"] = {"type": "prometheus", "uid": "kyc-prometheus"}
    for t in panel.get("targets", []):
        t["datasource"] = {"type": "prometheus", "uid": "kyc-prometheus"}
dash["tags"] = ["d6", "kyc-platform", "onboarding-api", "ai-powered"]
dash["title"] = "AI-Powered KYC Platform API"
dash["uid"] = "ai-powered-kyc-platform-api"
json.dump(dash, open(dest, "w"), indent=2)
print(f"OK {dest}")
PY
log "  ✅ $KYC_DASH_DEST"

log "▶ Remove separate KYC folder provider (keep only D6 folder)"
rm -f "$D6_PROVISIONING/dashboards/kyc-provider.yml"
rm -rf "$D6_DASHBOARDS/kyc"
log "  ✅ Removed empty AI-Powered KYC Platform folder config"

log "▶ Install KYC Prometheus datasource (separate from D6 prometheus)"
mkdir -p "$D6_PROVISIONING/datasources"
cp "$ROOT/infra/grafana/d6-integration/datasources/kyc-prometheus.yml" \
  "$D6_PROVISIONING/datasources/kyc-prometheus.yml"
log "  ✅ kyc-prometheus → http://host.docker.internal:9191"

log "▶ Restart $D6_CONTAINER"
docker restart "$D6_CONTAINER" >> "$LOG" 2>&1
sleep 8

DASH_URL="${GRAFANA_URL}/d/ai-powered-kyc-platform-api/ai-powered-kyc-platform-api"
echo "$DASH_URL" > "$EVIDENCE/grafana-dashboard-url.txt"

log ""
log "✅ D6 folder now has TWO different dashboards:"
log "   • API Observability        → D6 Prometheus (d6 stack)"
log "   • AI-Powered KYC Platform API → KYC Prometheus (port 9191)"
log ""
log "   Open: ${GRAFANA_URL}/dashboards → folder D6"
log "   Direct: $DASH_URL"
