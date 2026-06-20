# Flow: GET /metrics

**Confidence:** 47%

## Request → Database Chain

1. **controller** → `router.metrics` (`app/routers/health.py:19`) — GET /metrics

## Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor Client
    participant Controller
    Client->>+Controller: router.metrics [GET /metrics]
    Controller-->>-Client: GET /metrics response
```

## Uncertainties

- Service call not resolved in handler
