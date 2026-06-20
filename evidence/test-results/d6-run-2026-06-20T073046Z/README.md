# D6 Observability — Evidence Bundle

**Run:** 2026-06-20T073046Z  
**Report:** `docs/beginner/D6-observability/D6_REPORT.md`

| File | Description |
|------|-------------|
| `d6-observability-verification.log` | Full transcript |
| `success-observability-verify.txt` | `make observability-verify` output |
| `success-live-stack.txt` | Compose stack + Prometheus/Grafana checks |
| `sample-logs.txt` | Structured JSON log samples |
| `metrics-snapshot.txt` | In-process traffic metrics scrape |
| `live-metrics.txt` | Live API `/metrics` after traffic |
| `prometheus-targets.json` | Prometheus targets API response |
| `kyc-platform-dashboard.json` | Grafana dashboard JSON copy |
| `kyc-platform-dashboard.svg` | Dashboard evidence SVG |

## Run order

```bash
make observability-verify
cd infra/docker && docker compose --env-file .env up -d postgres onboarding-api prometheus grafana
curl http://127.0.0.1:8101/health
curl http://127.0.0.1:8101/metrics
open http://127.0.0.1:9191/targets
open http://127.0.0.1:3003  # admin/admin
```
