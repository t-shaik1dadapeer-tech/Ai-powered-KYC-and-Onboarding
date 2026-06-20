# Flow: GET /customer/{customer_id}

**Confidence:** 100%

## Request → Database Chain

1. **controller** → `router.get_customer` (`app/routers/customer_read.py:13`) — GET /customer/{customer_id}
2. **service** → `CustomerService.get_customer` (`app/services/customer_service.py:29`)
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
    Client->>+Controller: router.get_customer [GET /customer/{customer_id}]
    Controller->>+Service: CustomerService.get_customer
    Service->>+Repository: CustomerRepository.get_by_id
    Repository->>+Database: table:customers [SELECT]
    Database-->>-Client: GET /customer/{customer_id} response
```

