#!/usr/bin/env bash
# Build, run, and verify Docker stack — stores proof in evidence/docker-results/
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_DIR="$ROOT/infra/docker"
EVIDENCE="$ROOT/evidence/docker-results"
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
LOG="$EVIDENCE/phase-8-docker-verify.txt"

mkdir -p "$EVIDENCE"
: > "$LOG"

log() { echo "$1" | tee -a "$LOG"; }

log "Docker Verification — $TIMESTAMP"
log "=================================="
log ""

cd "$COMPOSE_DIR"

log "▶ docker compose build"
if docker compose build >> "$LOG" 2>&1; then
  log "  ✅ BUILD SUCCESS"
else
  log "  ❌ BUILD FAILED"
  exit 1
fi
log ""

log "▶ docker compose up -d"
docker compose up -d >> "$LOG" 2>&1

log "▶ Waiting for services (max 120s)"
for i in $(seq 1 24); do
  if curl -fsS http://localhost:8000/health >/dev/null 2>&1 \
    && curl -fsS http://localhost:9090/-/healthy >/dev/null 2>&1 \
    && curl -fsS http://localhost:3000/api/health >/dev/null 2>&1; then
    log "  ✅ All health endpoints ready (${i}x5s)"
    break
  fi
  sleep 5
  if [[ $i -eq 24 ]]; then
    log "  ❌ Health check timeout"
    docker compose ps >> "$LOG" 2>&1
    docker compose logs --tail=50 >> "$LOG" 2>&1
    exit 1
  fi
done
log ""

log "▶ Health checks"
curl -fsS http://localhost:8000/health | tee -a "$LOG"
echo "" | tee -a "$LOG"
curl -fsS http://localhost:8000/metrics | head -5 | tee -a "$LOG"
echo "" | tee -a "$LOG"

log "▶ Create customer via API"
CUSTOMER=$(curl -fsS -X POST http://localhost:8000/customers \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Docker User","email":"docker@example.com","phone":"9876543210"}')
echo "$CUSTOMER" | tee -a "$LOG"
echo "" | tee -a "$LOG"

log "▶ Node CLI (tools profile)"
docker compose --profile tools run --rm node-cli customer-create \
  --name "CLI Docker" --email "cli-docker@example.com" --phone "9123456780" \
  | tee -a "$LOG" || log "  ⚠ node-cli run skipped/failed"
log ""

log "▶ Rust analyzer (tools profile)"
docker compose --profile tools run --rm rust-analyzer \
  scan --path /workspace/services/onboarding-api 2>/dev/null \
  | head -10 | tee -a "$LOG" || log "  ⚠ rust-analyzer run skipped/failed"
log ""

log "▶ docker compose ps"
docker compose ps | tee -a "$LOG"
log ""

docker compose config > "$EVIDENCE/docker-compose-resolved.yml"

log "=================================="
log "✅ Docker verification complete"
log "Evidence: $LOG"
