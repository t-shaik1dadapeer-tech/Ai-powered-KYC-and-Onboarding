# Grafana Configuration

| Path | Used by | Purpose |
|------|---------|---------|
| `provisioning/` | `infra/docker/docker-compose.yml` | **Canonical** Docker stack — datasource UID `kyc-prometheus`, dashboard folder |
| `dashboards/` | Docker volume mount | Dashboard JSON (`kyc-platform.json`) |
| `d6-integration/` | `scripts/grafana-provision-port3002.sh` | D6 host-side verify — Prometheus at `host.docker.internal:9191` |

For normal development use Docker Compose provisioning only. Use `d6-integration/` when running the D6 observability verification script against a host Prometheus instance.
