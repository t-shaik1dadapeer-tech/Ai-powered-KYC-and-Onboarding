#!/usr/bin/env bash
# Import KYC dashboard — tries API token first, then file provision for Grafana :3002 (d6-grafana)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT/infra/docker/.env"

if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ENV_FILE"
  set +a
fi

GRAFANA_API_TOKEN="${GRAFANA_API_TOKEN:-}"
GRAFANA_PASSWORD="${GRAFANA_PASSWORD:-}"
GRAFANA_URL="${GRAFANA_URL:-http://127.0.0.1:3002}"

# Prefer file provision for :3002 (d6-grafana — admin password often changed)
if [[ "${GRAFANA_IMPORT_MODE:-auto}" == "file" ]] || [[ -z "$GRAFANA_API_TOKEN" && -z "$GRAFANA_PASSWORD" ]]; then
  exec bash "$ROOT/scripts/grafana-provision-port3002.sh"
fi

# Try API import when token/password provided
if [[ -n "$GRAFANA_API_TOKEN" ]]; then
  if curl -fsS -H "Authorization: Bearer $GRAFANA_API_TOKEN" "$GRAFANA_URL/api/user" >/dev/null 2>&1; then
    exec bash "$ROOT/scripts/grafana-import-dashboard-api.sh"
  fi
fi

if [[ -n "$GRAFANA_PASSWORD" ]]; then
  if curl -fsS -u "${GRAFANA_USER:-admin}:${GRAFANA_PASSWORD}" "$GRAFANA_URL/api/user" >/dev/null 2>&1; then
    exec bash "$ROOT/scripts/grafana-import-dashboard-api.sh"
  fi
fi

echo "⚠ API auth failed for $GRAFANA_URL — using file provision for d6-grafana (:3002)"
exec bash "$ROOT/scripts/grafana-provision-port3002.sh"
