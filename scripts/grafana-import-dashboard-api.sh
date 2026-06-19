#!/usr/bin/env bash
# API-based Grafana dashboard import (when token/password works)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT/infra/docker/.env"
DASHBOARD_JSON="$ROOT/infra/grafana/dashboards/kyc-platform.json"
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

GRAFANA_URL="${GRAFANA_URL:-http://127.0.0.1:3002}"
GRAFANA_USER="${GRAFANA_USER:-admin}"
GRAFANA_PASSWORD="${GRAFANA_PASSWORD:-}"
GRAFANA_API_TOKEN="${GRAFANA_API_TOKEN:-}"
PROMETHEUS_URL="${PROMETHEUS_URL:-http://host.docker.internal:9191}"
DS_UID="kyc-prometheus"
FOLDER_TITLE="AI-Powered KYC Platform"

log "Grafana API import — $TIMESTAMP"
log "Grafana: $GRAFANA_URL"
log ""

grafana_curl() {
  if [[ -n "$GRAFANA_API_TOKEN" ]]; then
    curl -fsS -H "Authorization: Bearer $GRAFANA_API_TOKEN" "$@"
  else
    curl -fsS -u "${GRAFANA_USER}:${GRAFANA_PASSWORD}" "$@"
  fi
}

log "▶ Check Grafana auth"
if ! grafana_curl "$GRAFANA_URL/api/user" >> "$LOG" 2>&1; then
  log "❌ Grafana auth failed"
  exit 1
fi
log "  ✅ Authenticated"

FOLDER_UID=$(grafana_curl "$GRAFANA_URL/api/folders" | python3 -c "
import json, sys
title = sys.argv[1]
for f in json.load(sys.stdin):
    if f.get('title') == title:
        print(f['uid'])
        break
" "$FOLDER_TITLE" 2>/dev/null || true)

if [[ -z "${FOLDER_UID:-}" ]]; then
  FOLDER_UID=$(grafana_curl -X POST "$GRAFANA_URL/api/folders" \
    -H "Content-Type: application/json" \
    -d "{\"title\":\"$FOLDER_TITLE\"}" | python3 -c "import json,sys; print(json.load(sys.stdin)['uid'])")
fi

DS_PAYLOAD=$(cat <<EOF
{"name":"KYC Platform Prometheus","type":"prometheus","access":"proxy","url":"$PROMETHEUS_URL","uid":"$DS_UID","isDefault":false,"jsonData":{"httpMethod":"POST"}}
EOF
)

EXISTING_DS_ID=$(grafana_curl "$GRAFANA_URL/api/datasources/uid/$DS_UID" 2>/dev/null \
  | python3 -c "import json,sys; print(json.load(sys.stdin).get('id',''))" 2>/dev/null || true)

if [[ -n "${EXISTING_DS_ID:-}" ]]; then
  grafana_curl -X PUT "$GRAFANA_URL/api/datasources/$EXISTING_DS_ID" \
    -H "Content-Type: application/json" -d "$DS_PAYLOAD" >> "$LOG" 2>&1
else
  grafana_curl -X POST "$GRAFANA_URL/api/datasources" \
    -H "Content-Type: application/json" -d "$DS_PAYLOAD" >> "$LOG" 2>&1
fi

IMPORT_BODY=$(python3 - "$DASHBOARD_JSON" "$DS_UID" "$FOLDER_UID" <<'PY'
import json, sys
path, ds_uid, folder_uid = sys.argv[1:4]
dash = json.load(open(path))
for panel in dash.get("panels", []):
    if "datasource" in panel:
        panel["datasource"] = {"type": "prometheus", "uid": ds_uid}
    for target in panel.get("targets", []):
        if "datasource" in target:
            target["datasource"] = {"type": "prometheus", "uid": ds_uid}
print(json.dumps({"dashboard": dash, "folderUid": folder_uid, "overwrite": True}))
PY
)

RESULT=$(grafana_curl -X POST "$GRAFANA_URL/api/dashboards/db" \
  -H "Content-Type: application/json" -d "$IMPORT_BODY")
DASH_URL=$(echo "$RESULT" | python3 -c "import json,sys; print(json.load(sys.stdin).get('url',''))")
echo "${GRAFANA_URL}${DASH_URL}" > "$EVIDENCE/grafana-dashboard-url.txt"
log "✅ Imported: ${GRAFANA_URL}${DASH_URL}"
