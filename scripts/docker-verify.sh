#!/usr/bin/env bash
# Build, run full stack, verify API via container (avoids host port hijacks)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_DIR="$ROOT/infra/docker"
EVIDENCE="$ROOT/evidence/docker-results"
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
LOG="$EVIDENCE/phase-8-docker-verify.txt"

mkdir -p "$EVIDENCE"
: > "$LOG"

log() { echo "$1" | tee -a "$LOG"; }

cd "$COMPOSE_DIR"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

PROM_PORT="${PROMETHEUS_HOST_PORT:-9191}"
API_PORT="${API_HOST_PORT:-8101}"
GRAFANA_BUNDLED="${BUNDLED_GRAFANA_URL:-http://127.0.0.1:3003}"
GRAFANA_EXTERNAL="${GRAFANA_URL:-http://127.0.0.1:3002}"

log "Docker Verification — $TIMESTAMP"
log "=================================="
log "API (host)        : $API_PORT"
log "Prometheus (host) : $PROM_PORT"
log "Grafana bundled   : $GRAFANA_BUNDLED  (admin/admin)"
log "Grafana external  : $GRAFANA_EXTERNAL  (optional import)"
log ""

api_curl() {
  docker compose exec -T onboarding-api curl -fsS "$@"
}

log "▶ docker compose down (clean stale stack)"
docker compose down >> "$LOG" 2>&1 || true
log ""

log "▶ docker compose build"
if docker compose build >> "$LOG" 2>&1; then
  log "  ✅ BUILD SUCCESS"
else
  log "  ❌ BUILD FAILED"
  exit 1
fi
log ""

log "▶ docker compose up -d (full stack + bundled Grafana)"
docker compose up -d >> "$LOG" 2>&1

log "▶ Waiting for services (max 180s)"
for i in $(seq 1 36); do
  if api_curl http://localhost:8000/health >/dev/null 2>&1 \
    && curl -fsS "http://127.0.0.1:${PROM_PORT}/-/healthy" >/dev/null 2>&1 \
    && curl -fsS "${GRAFANA_BUNDLED}/health" >/dev/null 2>&1; then
    log "  ✅ All services ready (${i}x5s)"
    break
  fi
  sleep 5
  if [[ $i -eq 36 ]]; then
    log "  ❌ Health check timeout"
    docker compose ps >> "$LOG" 2>&1
    exit 1
  fi
done
log ""

log "▶ API health (inside container — authoritative)"
api_curl http://localhost:8000/health | tee -a "$LOG"
echo "" | tee -a "$LOG"

log "▶ API metrics sample"
api_curl http://localhost:8000/metrics | head -5 | tee -a "$LOG"
echo "" | tee -a "$LOG"

log "▶ Create customer via KYC API"
UNIQUE_EMAIL="docker-verify-$(date +%s)@example.com"
CUSTOMER=$(api_curl -X POST http://localhost:8000/customers \
  -H "Content-Type: application/json" \
  -d "{\"full_name\":\"Docker User\",\"email\":\"${UNIQUE_EMAIL}\",\"phone\":\"9876543210\"}")
echo "$CUSTOMER" | tee -a "$LOG"
echo "" | tee -a "$LOG"

log "▶ Bundled Grafana dashboard"
log "  ✅ Open: ${GRAFANA_BUNDLED}/dashboards"
log "  Login: admin / admin"
log "  Folder: AI-Powered KYC Platform → AI-Powered KYC Platform API"
echo "${GRAFANA_BUNDLED}/d/ai-powered-kyc-platform-api" > "$ROOT/evidence/observability-results/grafana-dashboard-url.txt"

if [[ -n "${GRAFANA_API_TOKEN:-}" ]] || [[ -n "${GRAFANA_PASSWORD:-}" ]]; then
  log "▶ Optional import to external Grafana ($GRAFANA_EXTERNAL)"
  if bash "$ROOT/scripts/grafana-import-dashboard.sh" >> "$LOG" 2>&1; then
    log "  ✅ Also imported to $GRAFANA_EXTERNAL"
  else
    log "  ⚠ External import failed — use bundled Grafana at $GRAFANA_BUNDLED"
  fi
else
  log "▶ External Grafana :3002 skipped (set GRAFANA_API_TOKEN in infra/docker/.env to import)"
fi
log ""

log "▶ docker compose ps"
docker compose ps | tee -a "$LOG"
log ""

docker compose config > "$EVIDENCE/docker-compose-resolved.yml"

log "=================================="
log "✅ Docker verification complete"
log "Dashboard: ${GRAFANA_BUNDLED}/dashboards"
log "Evidence: $LOG"
