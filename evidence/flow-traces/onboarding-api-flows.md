# Flow Tracing Report

## GET /customer/{customer_id}

**Confidence:** 75%

### Chain

1. `router.get_customer`
2. `CustomerService.execute`
3. `CustomerService.get_customer`
4. `customers`

### Uncertainties

- Repository call inferred from handler name

## POST /customers

**Confidence:** 75%

### Chain

1. `router.create_customer`
2. `CustomerService.execute`
3. `CustomerService.create_customer`
4. `customers`

### Uncertainties

- Repository call inferred from handler name

## GET /health

**Confidence:** 60%

### Chain

1. `router.health_check`

### Uncertainties

- Service call not resolved statically
- Database table not inferred

## GET /metrics

**Confidence:** 60%

### Chain

1. `router.metrics`

### Uncertainties

- Service call not resolved statically
- Database table not inferred

## POST /kyc

**Confidence:** 75%

### Chain

1. `router.submit_kyc`
2. `KycService.execute`
3. `KycService.submit_kyc`
4. `kyc_submissions`

### Uncertainties

- Repository call inferred from handler name

## GET /kyc-status/{customer_id}

**Confidence:** 75%

### Chain

1. `router.get_kyc_status`
2. `KycService.execute`
3. `KycService.get_kyc_status`
4. `kyc_submissions`

### Uncertainties

- Repository call inferred from handler name

## POST /risk-score

**Confidence:** 75%

### Chain

1. `router.calculate_risk_score`
2. `RiskScoreService.execute`
3. `RiskScoreService.calculate`
4. `risk_assessments`

### Uncertainties

- Repository call inferred from handler name

## POST /pan-verify

**Confidence:** 75%

### Chain

1. `router.verify_pan`
2. `StandaloneVerificationService.execute`
3. `StandaloneVerificationService.verify`
4. `pan_records`

### Uncertainties

- Repository call inferred from handler name

## POST /bank-verify

**Confidence:** 75%

### Chain

1. `router.verify_bank`
2. `StandaloneVerificationService.execute`
3. `StandaloneVerificationService.verify`
4. `bank_records`

### Uncertainties

- Repository call inferred from handler name

