#!/usr/bin/env bash
# Lightweight load test — in-process FastAPI via httpx (no server required)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EVIDENCE="$ROOT/evidence/performance"
LOG="$EVIDENCE/load-test.txt"
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

mkdir -p "$EVIDENCE"
: > "$LOG"

log() { echo "$1" | tee -a "$LOG"; }

log "Load Test — $TIMESTAMP"
log "======================"

cd "$ROOT/services/onboarding-api"

PYTHONPATH=. .venv/bin/python3 - <<'PY' | tee -a "$LOG"
import asyncio
import time
from httpx import ASGITransport, AsyncClient
from app.main import app

REQUESTS = 200
CONCURRENCY = 20
THRESHOLD_MS = 500  # p95 must be under 500ms in-process

async def worker(client, sem, results):
    async with sem:
        t0 = time.perf_counter()
        r = await client.get("/health")
        elapsed = (time.perf_counter() - t0) * 1000
        results.append((r.status_code, elapsed))

async def main():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        sem = asyncio.Semaphore(CONCURRENCY)
        results = []
        t0 = time.perf_counter()
        await asyncio.gather(*[worker(client, sem, results) for _ in range(REQUESTS)])
        total = time.perf_counter() - t0

    latencies = sorted(e for _, e in results)
    p50 = latencies[len(latencies) // 2]
    p95 = latencies[int(len(latencies) * 0.95)]
    errors = sum(1 for s, _ in results if s != 200)
    rps = REQUESTS / total

    print(f"requests={REQUESTS} concurrency={CONCURRENCY}")
    print(f"duration_s={total:.3f} rps={rps:.1f}")
    print(f"p50_ms={p50:.2f} p95_ms={p95:.2f} errors={errors}")

    assert errors == 0, f"{errors} non-200 responses"
    assert p95 < THRESHOLD_MS, f"p95 {p95:.1f}ms exceeds {THRESHOLD_MS}ms"
    print("PASS")

asyncio.run(main())
PY

log ""
log "✅ Load test complete"
log "Evidence: $LOG"
