# API Map

**Repository:** `/Users/shaikdadapeer/agent development/services/onboarding-api`
**Framework:** `fastapi` (confidence: 100%)
**Generated:** 2026-06-16T17:50:49.557817+00:00

## Endpoints

| Method | Path | Handler | File |
| --- | --- | --- | --- |
| GET | `/customer/{customer_id}` | `get_customer` | `app/routers/customer_read.py:13` |
| POST | `/customers` | `create_customer` | `app/routers/customers.py:11` |
| GET | `/health` | `health_check` | `app/routers/health.py:9` |
| GET | `/metrics` | `metrics` | `app/routers/health.py:19` |
| POST | `/kyc` | `submit_kyc` | `app/routers/kyc.py:13` |
| GET | `/kyc-status/{customer_id}` | `get_kyc_status` | `app/routers/kyc.py:18` |
| POST | `/risk-score` | `calculate_risk_score` | `app/routers/risk.py:11` |
| POST | `/pan-verify` | `verify_pan` | `app/routers/verification.py:16` |
| POST | `/bank-verify` | `verify_bank` | `app/routers/verification.py:21` |

## Summary

- Total endpoints: **9**
