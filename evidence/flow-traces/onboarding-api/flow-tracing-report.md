# Flow Tracing Report

End-to-end traces: **Request → Controller → Service → Repository → Database**

**Endpoints traced:** 9
**Average confidence:** 76%

## GET /customer/{customer_id}

**Confidence:** 100%

### Flow Steps

| # | Layer | Symbol | File |
| --- | --- | --- | --- |
| 1 | controller | `router.get_customer` | `app/routers/customer_read.py:13` |
| 2 | service | `CustomerService.get_customer` | `app/services/customer_service.py:27` |
| 3 | repository | `CustomerRepository.get_by_id` | `app/repositories/customer_repository.py:32` |
| 4 | database | `table:customers` | — |

## POST /customers

**Confidence:** 92%

### Flow Steps

| # | Layer | Symbol | File |
| --- | --- | --- | --- |
| 1 | controller | `router.create_customer` | `app/routers/customers.py:11` |
| 2 | service | `CustomerService.create_customer` | `app/services/customer_service.py:16` |
| 3 | repository | `CustomerRepository.get_by_email` | `app/repositories/customer_repository.py:38` |
| 4 | database | `table:customers` | — |
| 5 | repository | `CustomerRepository.create` | `app/repositories/customer_repository.py:16` |
| 6 | database | `table:customers` | — |

### Uncertainties

- Table inferred from method name `get_by_email`

## GET /health

**Confidence:** 47%

### Flow Steps

| # | Layer | Symbol | File |
| --- | --- | --- | --- |
| 1 | controller | `router.health_check` | `app/routers/health.py:9` |

### Uncertainties

- Service call not resolved in handler

## GET /metrics

**Confidence:** 47%

### Flow Steps

| # | Layer | Symbol | File |
| --- | --- | --- | --- |
| 1 | controller | `router.metrics` | `app/routers/health.py:19` |

### Uncertainties

- Service call not resolved in handler

## POST /kyc

**Confidence:** 52%

### Flow Steps

| # | Layer | Symbol | File |
| --- | --- | --- | --- |
| 1 | controller | `router.submit_kyc` | `app/routers/kyc.py:13` |
| 2 | service | `KycService.submit_kyc` | `app/services/kyc_service.py:24` |
| 3 | repository | `CustomerRepository.get_by_id` | `app/repositories/customer_repository.py:32` |
| 4 | database | `table:customers` | — |
| 5 | repository | `KycRepository.create_submission` | `app/repositories/kyc_repository.py:18` |
| 6 | database | `table:kyc_submissions` | — |
| 7 | repository | `KycRepository.save_pan_record` | `app/repositories/kyc_repository.py:51` |
| 8 | database | `table:pan_records` | — |
| 9 | repository | `KycRepository.save_bank_record` | `app/repositories/kyc_repository.py:69` |
| 10 | database | `table:bank_records` | — |
| 11 | repository | `KycRepository.update_submission_status` | `app/repositories/kyc_repository.py:89` |
| 12 | database | `table:kyc_submissions` | — |
| 13 | repository | `CustomerRepository.update_status` | `app/repositories/customer_repository.py:42` |
| 14 | database | `table:customers` | — |

### Uncertainties

- Unknown repo attribute `_pan_service` on KycService
- Table inferred from method name `save_pan_record`
- Unknown repo attribute `_bank_service` on KycService
- Table inferred from method name `save_bank_record`
- Table inferred from method name `update_submission_status`
- Table inferred from method name `update_status`

## GET /kyc-status/{customer_id}

**Confidence:** 84%

### Flow Steps

| # | Layer | Symbol | File |
| --- | --- | --- | --- |
| 1 | controller | `router.get_kyc_status` | `app/routers/kyc.py:18` |
| 2 | service | `KycService.get_kyc_status` | `app/services/kyc_service.py:63` |
| 3 | repository | `CustomerRepository.get_by_id` | `app/repositories/customer_repository.py:32` |
| 4 | database | `table:customers` | — |
| 5 | repository | `KycRepository.get_latest_by_customer` | `app/repositories/kyc_repository.py:32` |

### Uncertainties

- Could not resolve table for KycRepository.get_latest_by_customer
- Database table unresolved for KycRepository.get_latest_by_customer

## POST /risk-score

**Confidence:** 76%

### Flow Steps

| # | Layer | Symbol | File |
| --- | --- | --- | --- |
| 1 | controller | `router.calculate_risk_score` | `app/routers/risk.py:11` |
| 2 | service | `RiskScoreService.calculate` | `app/services/risk_score_service.py:34` |
| 3 | repository | `CustomerRepository.get_by_id` | `app/repositories/customer_repository.py:32` |
| 4 | database | `table:customers` | — |
| 5 | repository | `KycRepository.get_latest_by_customer` | `app/repositories/kyc_repository.py:32` |
| 6 | repository | `DocumentRepository.save_risk_assessment` | `app/repositories/document_repository.py:15` |
| 7 | database | `table:risk_assessments` | — |

### Uncertainties

- Could not resolve table for KycRepository.get_latest_by_customer
- Database table unresolved for KycRepository.get_latest_by_customer
- Table inferred from method name `save_risk_assessment`

## POST /pan-verify

**Confidence:** 92%

### Flow Steps

| # | Layer | Symbol | File |
| --- | --- | --- | --- |
| 1 | controller | `router.verify_pan` | `app/routers/verification.py:16` |
| 2 | service | `StandaloneVerificationService.verify_pan` | `app/services/standalone_verification_service.py:20` |
| 3 | repository | `CustomerRepository.get_by_id` | `app/repositories/customer_repository.py:32` |
| 4 | database | `table:customers` | — |

### Uncertainties

- Unknown repo attribute `_pan_service` on StandaloneVerificationService

## POST /bank-verify

**Confidence:** 92%

### Flow Steps

| # | Layer | Symbol | File |
| --- | --- | --- | --- |
| 1 | controller | `router.verify_bank` | `app/routers/verification.py:21` |
| 2 | service | `StandaloneVerificationService.verify_bank` | `app/services/standalone_verification_service.py:29` |
| 3 | repository | `CustomerRepository.get_by_id` | `app/repositories/customer_repository.py:32` |
| 4 | database | `table:customers` | — |

### Uncertainties

- Unknown repo attribute `_bank_service` on StandaloneVerificationService

