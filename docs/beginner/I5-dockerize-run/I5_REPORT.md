# I5 — Dockerize and Run Verification

**Evaluation criterion:** I5 (Dockerization)  
**Stack:** `infra/docker/docker-compose.yml`  
**Verification date:** 2026-06-20T05:38:22Z (UTC)  
**Evidence:** `evidence/test-results/i5-run-2026-06-20-1107/`  
**Machine-readable:** `docker-assets.csv`

---

## 1. Executive Summary

| Check | Result | Confidence |
|-------|--------|------------|
| Dockerfiles present | **3** (API, CLI, Rust) | High |
| docker-compose.yml | **PASS** — 6 services | High |
| `docker compose build` | **PASS** | High — executed |
| `docker compose up` | **PASS** — 4 core services healthy | High — executed |
| API health (in-container) | **PASS** | High |
| API health (host `:8101`) | **PASS** | High |
| Smoke test `POST /customers` | **PASS** — 201 in container | High |
| Prometheus / Grafana health | **PASS** | High |
| Compose HEALTHCHECK definitions | **PASS** — postgres, api, prometheus, grafana | High |
| README Docker instructions | **PASS** (`make docker-verify`) | High |
| Production gaps | Dev DB creds in compose, no restart policy on API | Noted |

**Overall I5 status: PASS (10/10)** — containerized stack builds, starts, and serves API requests.

---

## 2. Container Architecture Overview

```
Host
├── :8101  → onboarding-api:8000  (FastAPI + uvicorn)
├── :9191  → prometheus:9090
├── :3003  → grafana:3000
└── (internal) postgres:5432

Network: kyc-net (bridge)
Volume: postgres_data (persistent)
```

| Service | Image | Role |
|---------|-------|------|
| `postgres` | `postgres:16-alpine` | Database |
| `onboarding-api` | build `services/onboarding-api` | KYC REST API |
| `prometheus` | `prom/prometheus:v2.54.1` | Metrics scrape |
| `grafana` | `grafana/grafana:11.2.0` | Dashboards |
| `node-cli` | build `clients/node-cli` | tools profile |
| `rust-analyzer` | build `engines/rust-analyzer` | tools profile |

---

## 3. Docker Asset Discovery

| Asset | Path |
|-------|------|
| Compose file | `infra/docker/docker-compose.yml` |
| Env overrides | `infra/docker/.env` |
| Verify script | `scripts/docker-verify.sh` |
| API Dockerfile | `services/onboarding-api/Dockerfile` |
| CLI Dockerfile | `clients/node-cli/Dockerfile` |
| Rust Dockerfile | `engines/rust-analyzer/Dockerfile` |
| CI docker job | `.github/workflows/ci.yml` → `docker-build` |
| Evidence (runtime) | `evidence/docker-results/phase-8-docker-verify.txt` |

**CSV:** `docker-assets.csv`

---

## 4. Dockerfile Analysis

### onboarding-api (primary service)

| Item | Value | Source |
|------|-------|--------|
| Base image | `python:3.12-slim` | `Dockerfile:1` |
| Stages | Single-stage | — |
| System deps | `curl` (healthcheck) | `Dockerfile:9-10` |
| Python deps | `pip install -r requirements.txt` | `Dockerfile:12-13` |
| Copy scope | `app/` only (tests excluded via `.dockerignore`) | `Dockerfile:15`, `.dockerignore` |
| EXPOSE | `8000` | `Dockerfile:17` |
| HEALTHCHECK | `curl -fsS http://localhost:8000/health` | `Dockerfile:19-20` |
| CMD | `uvicorn app.main:app --host 0.0.0.0 --port 8000` | `Dockerfile:22` |

### node-cli

| Item | Value |
|------|-------|
| Base | `node:20-alpine` |
| ENV | `API_BASE_URL=http://onboarding-api:8000` |
| ENTRYPOINT | `node bin/kyc-cli.js` |

### rust-analyzer

| Item | Value |
|------|-------|
| Build | `rust:1-bookworm` → `cargo build --release` |
| Runtime | `debian:bookworm-slim` + binary copy |
| Pattern | Multi-stage (smaller runtime image) |

---

## 5. Build Verification

### Commands

```bash
cd infra/docker
docker compose config --quiet          # syntax validation
make docker-verify                     # full gate (build + up + smoke)
```

### Build result (executed 2026-06-20)

```
▶ docker compose build
  ✅ BUILD SUCCESS
```

**Image:** `docker-onboarding-api:latest` — **246MB**  
**Build log:** Mostly CACHED layers; `COPY app ./app` layer 6/6  
**Warnings:** None fatal

**Evidence:** `phase-8-docker-verify.txt`, `images-after.txt`

---

## 6. Container Runtime Verification

### Startup

```bash
cd infra/docker && docker compose up -d
```

**Wait result:** All services ready in **~15s** (3×5s poll)

### Container status (`docker compose ps`)

| Container | Status | Ports |
|-----------|--------|-------|
| `docker-onboarding-api-1` | **healthy** | `0.0.0.0:8101->8000/tcp` |
| `docker-postgres-1` | **healthy** | 5432 (internal) |
| `docker-prometheus-1` | **healthy** | `0.0.0.0:9191->9090/tcp` |
| `docker-grafana-1` | up (health starting → healthy) | `0.0.0.0:3003->3000/tcp` |

### Startup logs

Uvicorn: `Application startup complete` — `evidence/.../phase-8-docker-verify.txt`  
Structlog: `application_started` event on lifespan

### Environment (onboarding-api container)

| Variable | Value |
|----------|-------|
| `DATABASE_URL` | `postgresql+psycopg2://kyc:kyc@postgres:5432/kyc` |
| `LOG_LEVEL` | `INFO` |

---

## 7. Service Response Verification

### In-container (authoritative)

```bash
docker compose exec -T onboarding-api curl -fsS http://localhost:8000/health
```

**Response:**
```json
{"status":"healthy","service":"onboarding-api","version":"0.1.0"}
```

### Host port mapping

```bash
curl http://127.0.0.1:8101/health
```

**Response:** Same JSON — **PASS**

### Smoke test — create customer

```bash
docker compose exec -T onboarding-api curl -X POST http://localhost:8000/customers \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Docker User","email":"docker-verify-...@example.com","phone":"9876543210"}'
```

**Response:** `201` — customer `id`, `status: pending`, Postgres timestamps

### Metrics

`GET /metrics` returns Prometheus text including `python_gc_objects_collected_total` — **PASS**

**Evidence:** `host-curl.txt`, `phase-8-docker-verify.txt`

---

## 8. Health Check Verification

| Layer | Check | Result |
|-------|-------|--------|
| Dockerfile | `HEALTHCHECK curl /health` | Defined |
| Compose `onboarding-api` | `curl -fsS http://localhost:8000/health` | **healthy** |
| Compose `postgres` | `pg_isready -U kyc` | **healthy** |
| Compose `prometheus` | `wget .../-/healthy` | **healthy** |
| Compose `grafana` | `wget .../health` | **healthy** |
| `depends_on` | API waits for postgres healthy | Verified |
| Docker inspect | `docker-onboarding-api-1` → `healthy` | **PASS** |

**Readiness:** `depends_on: condition: service_healthy` chains postgres → api → prometheus → grafana

---

## 9. README Verification

### Root `README.md` (Docker section)

| Item | Present |
|------|---------|
| `make docker-verify` | ✅ |
| `make docker-up` / `make docker-down` | ✅ |
| Service URLs table | ✅ (notes `:8000` — host uses `:8101` via `.env`) |
| Docker Desktop prerequisite | ✅ |

### `infra/docker/.env`

Documents `API_HOST_PORT=8101`, Prometheus `9191`, Grafana `3003`

### Gap

Root README lists API at `localhost:8000`; actual Docker host port is **8101** per `infra/docker/.env`. Compose README comment at top of `.env` clarifies.

---

## 10. Production Readiness Assessment

| Area | Assessment |
|------|------------|
| Image size | API 246MB — reasonable for Python slim |
| Multi-stage | Rust yes; API single-stage (acceptable) |
| Secrets | `kyc/kyc` postgres creds in compose — **dev only** |
| `.dockerignore` | Excludes `.venv`, tests, `onboarding.db` — **good** |
| Health checks | Dockerfile + compose — **good** |
| Restart policy | Not set on services — **gap for prod** |
| Logging | structlog JSON to stdout — container-friendly |
| Non-root user | Not configured — **hardening opportunity** |
| API auth | `API_KEY` optional, empty in compose — dev mode |

---

## 11. Findings and Recommendations

### Strengths

1. Full stack compose with health-gated startup order.
2. `make docker-verify` automates build + smoke + evidence.
3. In-container curl avoids host port conflicts.
4. Unique email per verify run prevents 409 on persistent volume.
5. CI `docker-build` job mirrors compose build.

### Gaps

| Gap | Severity | Recommendation |
|-----|----------|----------------|
| README port 8000 vs 8101 | Low | Align docs with `API_HOST_PORT` |
| No `restart: unless-stopped` | Medium | Add for prod compose overlay |
| Dev DB password in plain text | High for prod | Use secrets / external RDS |
| node-cli tools profile not smoke-tested in I5 | Low | `docker compose --profile tools run node-cli ...` |
| Stack left running after verify | Info | `make docker-down` when done |

---

## 12. Areas Requiring Manual Verification

| Area | Reason |
|------|--------|
| node-cli container → API | tools profile; not in default `up` |
| rust-analyzer container scan | tools profile + volume mount |
| External Grafana import `:3002` | Skipped (no token) |
| Production K8s deploy | Separate from compose (`infra/kubernetes/`) |

---

## 13. Verification Summary

| # | Step | Command | Result |
|---|------|---------|--------|
| 1 | Compose syntax | `docker compose config --quiet` | PASS |
| 2 | Build | `docker compose build` | **SUCCESS** |
| 3 | Start stack | `docker compose up -d` | PASS |
| 4 | API health (container) | `curl localhost:8000/health` | PASS |
| 5 | API health (host) | `curl :8101/health` | PASS |
| 6 | Create customer | `POST /customers` in container | PASS |
| 7 | Prometheus | `curl :9191/-/healthy` | HTTP 200 |
| 8 | Container health | `docker inspect` | **healthy** |
| 9 | Full gate | `make docker-verify` | **COMPLETE** |

| Deliverable | Path |
|-------------|------|
| Report | `docs/beginner/I5-dockerize-run/I5_REPORT.md` |
| Asset inventory | `docs/beginner/I5-dockerize-run/docker-assets.csv` |
| Evidence | `evidence/test-results/i5-run-2026-06-20-1107/` |

**I5 verdict: PASS**

---

### Quick reference commands

```bash
make docker-verify    # build + up + health + smoke (recommended)
make docker-up        # start stack
make docker-down      # stop stack
curl http://127.0.0.1:8101/health
```

---

*All results from executed commands on 2026-06-20. Stack may remain running after verification.*
