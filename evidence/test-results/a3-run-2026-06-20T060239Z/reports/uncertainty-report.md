# Uncertainty Report

Documents low-confidence edges and unresolved symbols in flow traces.

- Endpoints with uncertainties: **8** / 9
- Fully resolved (≥85%, no uncertainties): **1**

## Flagged Endpoints

### POST /customers (92%)
- Table inferred from method name `get_by_email`

### GET /health (47%)
- Service call not resolved in handler

### GET /metrics (47%)
- Service call not resolved in handler

### POST /kyc (52%)
- Unknown repo attribute `_pan_service` on KycService
- Table inferred from method name `save_pan_record`
- Unknown repo attribute `_bank_service` on KycService
- Table inferred from method name `save_bank_record`
- Table inferred from method name `update_submission_status`
- Table inferred from method name `update_status`

### GET /kyc-status/{customer_id} (84%)
- Could not resolve table for KycRepository.get_latest_by_customer
- Database table unresolved for KycRepository.get_latest_by_customer

### POST /risk-score (76%)
- Could not resolve table for KycRepository.get_latest_by_customer
- Database table unresolved for KycRepository.get_latest_by_customer
- Table inferred from method name `save_risk_assessment`

### POST /pan-verify (92%)
- Unknown repo attribute `_pan_service` on StandaloneVerificationService

### POST /bank-verify (92%)
- Unknown repo attribute `_bank_service` on StandaloneVerificationService

## Low Confidence (<70%)

- GET /health: 47%
- GET /metrics: 47%
- POST /kyc: 52%
