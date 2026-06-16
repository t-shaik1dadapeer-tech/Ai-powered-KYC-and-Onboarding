# Metrics Catalog — Onboarding API

Prometheus endpoint: `GET /metrics`  
Scrape config: `infra/prometheus/prometheus.yml` → `onboarding-api:8000`

## HTTP (middleware)

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `http_requests_total` | Counter | method, path, status | Every HTTP request (except `/metrics`) |
| `http_request_duration_seconds` | Histogram | method, path | Request latency buckets |

## Customer onboarding

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `customers_created_total` | Counter | status | New customers (`pending` at creation) |

## KYC pipeline

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `kyc_submissions_total` | Counter | status | KYC outcomes: `verified`, `rejected` |
| `kyc_submissions_active` | Gauge | — | Incremented on each successful KYC (verified proxy) |
| `pan_verifications_total` | Counter | status | PAN checks via KYC flow or `/pan-verify` |
| `bank_verifications_total` | Counter | status | Bank checks via KYC flow or `/bank-verify` |

## Risk scoring

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `risk_assessments_total` | Counter | band | Risk calculations by band (`low`, `medium`, `high`) |
| `risk_score_histogram` | Histogram | band | Observed score values (0–100) |

## Instrumentation locations

| Module | Metrics emitted |
|--------|-----------------|
| `app/main.py` | HTTP counters/histogram (middleware) |
| `app/services/customer_service.py` | `customers_created_total` |
| `app/services/kyc_service.py` | KYC + PAN + bank + active gauge |
| `app/services/standalone_verification_service.py` | PAN + bank counters |
| `app/services/risk_score_service.py` | `risk_assessments_total`, `risk_score_histogram` |

## Grafana dashboard

Dashboard JSON: `infra/grafana/dashboards/kyc-platform.json`  
Panels: request rate, errors, latency, customer creation, KYC, verifications, risk bands, score distribution.

## Example queries

```promql
# KYC success rate (5m window)
sum(rate(kyc_submissions_total{status="verified"}[5m]))
/ sum(rate(kyc_submissions_total[5m]))

# Risk assessments by band
sum(rate(risk_assessments_total[5m])) by (band)

# p95 API latency
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))
```
