# API Map — Onboarding Service

**OpenAPI:** [`docs/api/openapi.json`](api/openapi.json) (exported 2026-06-17, 9 paths)  
**Source routers:** `services/onboarding-api/app/routers/`

---

## Endpoint Inventory

### POST `/customers`

| Field | Value |
|-------|-------|
| **Router handler** | `create_customer` → `app/routers/customers.py` |
| **Service** | `CustomerService.create_customer` → `app/services/customer_service.py` |
| **Repository** | `CustomerRepository.create` → `app/repositories/customer_repository.py` |
| **Request model** | `CustomerCreate` → `app/schemas/customer.py` |
| **Response model** | `CustomerResponse` (201) |
| **Dependencies** | `get_db` session |
| **Metrics** | `customers_created_total{status}` |
| **Errors** | 409 Conflict (duplicate email) |

---

### GET `/customer/{customer_id}`

| Field | Value |
|-------|-------|
| **Handler** | `get_customer` → `app/routers/customer_read.py` |
| **Service** | `CustomerService.get_customer` |
| **Repository** | `CustomerRepository.get_by_id` |
| **Response** | `CustomerResponse` (200) / 404 |

---

### POST `/kyc`

| Field | Value |
|-------|-------|
| **Handler** | `submit_kyc` → `app/routers/kyc.py` |
| **Service** | `KycService.submit_kyc` → `app/services/kyc_service.py` |
| **Repositories** | `CustomerRepository`, `KycRepository` |
| **External** | `PanVerificationService`, `BankVerificationService` (mock) |
| **Request** | `KycSubmitRequest` → `app/schemas/kyc.py` |
| **Response** | `KycStatusResponse` (201) |
| **Metrics** | `kyc_submissions_total`, `pan_verifications_total`, `bank_verifications_total` |
| **Side effects** | Creates `KycSubmission`, `PanRecord`, `BankRecord`; updates customer status |

---

### GET `/kyc-status/{customer_id}`

| Field | Value |
|-------|-------|
| **Handler** | `get_kyc_status` → `app/routers/kyc.py` |
| **Service** | `KycService.get_kyc_status` |
| **Repository** | `KycRepository.get_latest_by_customer` |
| **Response** | `KycStatusResponse` |

---

### POST `/pan-verify`

| Field | Value |
|-------|-------|
| **Handler** | `verify_pan` → `app/routers/verification.py` |
| **Service** | `StandaloneVerificationService.verify_pan` |
| **Request** | `PanVerifyRequest` → `app/schemas/verification.py` |
| **Response** | `PanVerifyResponse` |
| **Metrics** | `pan_verifications_total` |

---

### POST `/bank-verify`

| Field | Value |
|-------|-------|
| **Handler** | `verify_bank` → `app/routers/verification.py` |
| **Service** | `StandaloneVerificationService.verify_bank` |
| **Request** | `BankVerifyRequest` |
| **Response** | `BankVerifyResponse` |
| **Metrics** | `bank_verifications_total` |

---

### POST `/risk-score`

| Field | Value |
|-------|-------|
| **Handler** | `calculate_risk_score` → `app/routers/risk.py` |
| **Service** | `RiskScoreService.calculate` → `app/services/risk_score_service.py` |
| **Repository** | `DocumentRepository.save_risk_assessment` |
| **Request** | `RiskScoreRequest` → `app/schemas/risk.py` |
| **Response** | `RiskScoreResponse` |
| **Metrics** | `risk_assessments_total`, `risk_score_histogram` |

---

### GET `/health`

| Field | Value |
|-------|-------|
| **Handler** | `health_check` → `app/routers/health.py` |
| **Response** | `{status, service, version}` |

---

### GET `/metrics`

| Field | Value |
|-------|-------|
| **Handler** | `metrics` → `app/routers/health.py` |
| **Output** | Prometheus text format |
| **Instruments** | `app/core/metrics.py` |

---

## Dependency Graph (simplified)

```
HTTP → Router → Service → Repository → SQLAlchemy Model → SQLite/Postgres
                    ↘ Mock verifiers (PAN/Bank)
```

**Analyzer-generated map:** `evidence/api-maps/onboarding-api/api-map.md`

## Verification

```bash
bash scripts/export-openapi.sh
curl -s http://localhost:8000/openapi.json | python3 -m json.tool | head
```
