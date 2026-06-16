# Flow: POST /kyc

**Confidence:** 52%

## Request → Database Chain

1. **controller** → `router.submit_kyc` (`app/routers/kyc.py:13`) — POST /kyc
2. **service** → `KycService.submit_kyc` (`app/services/kyc_service.py:24`)
3. **repository** → `CustomerRepository.get_by_id` (`app/repositories/customer_repository.py:32`)
4. **database** → `table:customers` — SELECT
5. **repository** → `KycRepository.create_submission` (`app/repositories/kyc_repository.py:18`)
6. **database** → `table:kyc_submissions` — INSERT/UPDATE
7. **repository** → `KycRepository.save_pan_record` (`app/repositories/kyc_repository.py:51`)
8. **database** → `table:pan_records` — INSERT/UPDATE
9. **repository** → `KycRepository.save_bank_record` (`app/repositories/kyc_repository.py:69`)
10. **database** → `table:bank_records` — INSERT/UPDATE
11. **repository** → `KycRepository.update_submission_status` (`app/repositories/kyc_repository.py:89`)
12. **database** → `table:kyc_submissions` — UPDATE
13. **repository** → `CustomerRepository.update_status` (`app/repositories/customer_repository.py:42`)
14. **database** → `table:customers` — UPDATE

## Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor Client
    participant Controller
    participant Service
    participant Repository
    participant Database
    Client->>+Controller: router.submit_kyc [POST /kyc]
    Controller->>+Service: KycService.submit_kyc
    Service->>+Repository: CustomerRepository.get_by_id
    Repository->>+Database: table:customers [SELECT]
    Database->>+Repository: KycRepository.create_submission
    Repository->>+Database: table:kyc_submissions [INSERT/UPDATE]
    Database->>+Repository: KycRepository.save_pan_record
    Repository->>+Database: table:pan_records [INSERT/UPDATE]
    Database->>+Repository: KycRepository.save_bank_record
    Repository->>+Database: table:bank_records [INSERT/UPDATE]
    Database->>+Repository: KycRepository.update_submission_status
    Repository->>+Database: table:kyc_submissions [UPDATE]
    Database->>+Repository: CustomerRepository.update_status
    Repository->>+Database: table:customers [UPDATE]
    Database-->>-Client: POST /kyc response
```

## Uncertainties

- Unknown repo attribute `_pan_service` on KycService
- Table inferred from method name `save_pan_record`
- Unknown repo attribute `_bank_service` on KycService
- Table inferred from method name `save_bank_record`
- Table inferred from method name `update_submission_status`
- Table inferred from method name `update_status`
