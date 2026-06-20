# Flow: GET /health

**Confidence:** 47%

## Request → Database Chain

1. **controller** → `router.health_check` (`app/routers/health.py:9`) — GET /health

## Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor Client
    participant Controller
    Client->>+Controller: router.health_check [GET /health]
    Controller-->>-Client: GET /health response
```

## Uncertainties

- Service call not resolved in handler
