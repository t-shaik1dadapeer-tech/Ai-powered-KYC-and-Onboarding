# Flow: POST /pan-verify

**Confidence:** 92%

## Request → Database Chain

1. **controller** → `router.verify_pan` (`app/routers/verification.py:16`) — POST /pan-verify
2. **service** → `StandaloneVerificationService.verify_pan` (`app/services/standalone_verification_service.py:20`)
3. **repository** → `CustomerRepository.get_by_id` (`app/repositories/customer_repository.py:32`)
4. **database** → `table:customers` — SELECT

## Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor Client
    participant Controller
    participant Service
    participant Repository
    participant Database
    Client->>+Controller: router.verify_pan [POST /pan-verify]
    Controller->>+Service: StandaloneVerificationService.verify_pan
    Service->>+Repository: CustomerRepository.get_by_id
    Repository->>+Database: table:customers [SELECT]
    Database-->>-Client: POST /pan-verify response
```

## Uncertainties

- Unknown repo attribute `_pan_service` on StandaloneVerificationService
