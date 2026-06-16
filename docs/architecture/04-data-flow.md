# Data Flow Diagram

## 1. Level 0 — Context Data Flow

```mermaid
flowchart LR
    OP[Operator] -->|customer JSON| CLI[Node CLI]
    AN[Analyst] -->|repo path| CLI
    CLI -->|REST JSON| API[FastAPI]
    CLI -->|analyze request| INTEL[Intelligence Engine]
    API -->|SQL| DB[(PostgreSQL)]
    API -->|verify| EXT[External Verifiers]
    INTEL -->|scan| RUST[Rust Engine]
    RUST -->|parse JSON| INTEL
    INTEL -->|reports| EVID[evidence/]
    API -->|metrics| PROM[Prometheus]
    INTEL -->|metrics| PROM
```

---

## 2. KYC Data Flow (Detailed)

```mermaid
flowchart TB
    subgraph Input
        IN_CUST[CustomerCreateRequest]
        IN_KYC[KycSubmitRequest]
        IN_PAN[PanVerifyRequest]
        IN_BANK[BankVerifyRequest]
    end

    subgraph Validation
        PYD[Pydantic Validators]
    end

    subgraph Processing
        SVC[Domain Services]
        RULES[Risk Rules]
    end

    subgraph Persistence
        ORM[SQLAlchemy Models]
        PG[(PostgreSQL Tables)]
    end

    subgraph Output
        OUT_CUST[CustomerResponse]
        OUT_KYC[KycStatusResponse]
        OUT_RISK[RiskScoreResponse]
    end

    IN_CUST --> PYD --> SVC --> ORM --> PG
    IN_KYC --> PYD --> SVC
    IN_PAN --> PYD --> SVC
    IN_BANK --> PYD --> SVC
    SVC --> RULES
    SVC --> OUT_CUST
    SVC --> OUT_KYC
    RULES --> OUT_RISK
    ORM --> OUT_CUST
    ORM --> OUT_KYC
```

---

## 3. Entity-Relationship Model (Planned)

```mermaid
erDiagram
    CUSTOMER ||--o{ KYC_SUBMISSION : has
    CUSTOMER ||--o{ RISK_ASSESSMENT : receives
    KYC_SUBMISSION ||--o| PAN_RECORD : includes
    KYC_SUBMISSION ||--o| BANK_RECORD : includes

    CUSTOMER {
        uuid id PK
        string full_name
        string email UK
        string phone
        string status
        datetime created_at
        datetime updated_at
    }

    KYC_SUBMISSION {
        uuid id PK
        uuid customer_id FK
        string status
        string rejection_reason
        datetime submitted_at
        datetime verified_at
    }

    PAN_RECORD {
        uuid id PK
        uuid kyc_submission_id FK
        string pan_hash
        string verification_status
        json provider_response
    }

    BANK_RECORD {
        uuid id PK
        uuid kyc_submission_id FK
        string account_hash
        string ifsc
        string verification_status
        json provider_response
    }

    RISK_ASSESSMENT {
        uuid id PK
        uuid customer_id FK
        int score
        string band
        json factors
        datetime calculated_at
    }
```

> **Note:** PAN and bank account numbers stored as hashes only; raw values never persisted (Phase 2 implementation).

---

## 4. Repository Intelligence Data Flow

```mermaid
flowchart TB
    subgraph Input
        PATH[Repository Path]
        IGNORE[.analyzerignore]
    end

    subgraph Rust Pipeline
        WALK[File Index]
        PARSE[AST / Regex Parse]
        GRAPH[Import Graph JSON]
    end

    subgraph Python Pipeline
        DETECT[Framework Detection]
        EXTRACT[Symbol Extraction]
        MERGE[Merged Inventory Model]
    end

    subgraph Outputs
        INV_SVC[service-inventory.md]
        INV_CTRL[controller-inventory.md]
        INV_API[api-inventory.md]
        INV_MODEL[model-inventory.md]
        INV_TEST[test-inventory.md]
        INV_DEP[dependency-inventory.md]
        ER[er-diagram.mmd]
        API_MAP[api-map.md]
        FLOW[flow-trace-*.md]
        UNCERT[uncertainty-report.md]
    end

    PATH --> WALK
    IGNORE --> WALK
    WALK --> PARSE --> GRAPH
    GRAPH --> EXTRACT
    PATH --> DETECT --> EXTRACT
    EXTRACT --> MERGE
    MERGE --> INV_SVC
    MERGE --> INV_CTRL
    MERGE --> INV_API
    MERGE --> INV_MODEL
    MERGE --> INV_TEST
    MERGE --> INV_DEP
    MERGE --> ER
    MERGE --> API_MAP
    MERGE --> FLOW
    MERGE --> UNCERT
```

---

## 5. Inventory JSON Schema (Analyzer Contract)

```json
{
  "repository": "/absolute/path",
  "framework": "fastapi | spring_boot | node_express",
  "confidence": 0.92,
  "generated_at": "2026-06-16T12:00:00Z",
  "inventories": {
    "services": [{ "name": "CustomerService", "file": "app/services/customer_service.py", "line": 12 }],
    "controllers": [{ "name": "customers.router", "file": "app/routers/customers.py", "line": 8 }],
    "apis": [{ "method": "POST", "path": "/customers", "handler": "create_customer", "file": "...", "line": 24 }],
    "models": [{ "name": "Customer", "table": "customers", "file": "...", "line": 6 }],
    "tests": [{ "name": "test_create_customer", "file": "tests/test_customers.py", "line": 10 }],
    "dependencies": [{ "name": "fastapi", "version": "0.111.0", "source": "pyproject.toml" }]
  },
  "flow_traces": [{
    "endpoint": "POST /customers",
    "chain": ["router.create_customer", "CustomerService.create", "CustomerRepository.insert", "customers"],
    "confidence": 0.88,
    "uncertainties": ["Dynamic dispatch in middleware not traced"]
  }]
}
```

---

## 6. Evidence Store Data Flow

```mermaid
flowchart LR
    subgraph Producers
        TESTS[Test Runners]
        DOCKER[Docker Builds]
        CI[GitHub Actions]
        ANAL[Analyzer]
        AGENT[Agent Runs]
    end

    subgraph evidence/
        ARCH[architecture/]
        DIAG[diagrams/]
        FLOW[flow-traces/]
        API[api-maps/]
        TR[test-results/]
        DR[docker-results/]
        CR[ci-results/]
        SS[screenshots/]
    end

    subgraph verification/
        VP[phase-*.md]
    end

    ANAL --> DIAG
    ANAL --> FLOW
    ANAL --> API
    TESTS --> TR
    DOCKER --> DR
    CI --> CR
    AGENT --> VP
    ARCH --> ARCH
```

---

## 7. Log & Metric Data Flow

| Stage | Data | Format | Destination |
|-------|------|--------|-------------|
| Request ingress | `request_id`, `method`, `path` | JSON (structlog) | stdout → collector |
| KYC event | `customer_id`, `kyc_status` (no PII) | JSON | stdout |
| Error | `exception`, `stack`, `request_id` | JSON | stdout |
| Metric increment | `http_requests_total` | Prometheus | `/metrics` endpoint |
| Scrape | all metrics | text exposition | Prometheus TSDB |
| Dashboard | PromQL results | panels | Grafana JSON |

---

## 8. Data Classification

| Data Type | Sensitivity | Storage | Retention |
|-----------|-------------|---------|-----------|
| Customer PII | High | PostgreSQL (encrypted) | Policy-driven |
| PAN/Bank raw input | High | Transient only; hashed at rest | Not stored raw |
| Analyzer reports | Low | `evidence/` git | Version controlled |
| Metrics | Low | Prometheus TSDB | 15 days (dev) |
| CI artifacts | Low | GitHub Actions | 90 days |

---

## 9. Risk Assessment

| Risk | Data Impact | Mitigation |
|------|-------------|------------|
| PII in logs | Compliance violation | structlog processors redact fields |
| Path traversal in analyzer | Read arbitrary FS | Canonicalize paths; allowlist roots |
| Stale ER diagram | Wrong architecture view | Regenerate on CI; timestamp on reports |
| Large repo OOM in Rust | Crash | File batching; max file size limit |

---

## 10. Evaluation Mapping

| Dimension | Coverage |
|-----------|----------|
| B2 | API map output flow |
| B3 | ER diagram in §3 |
| B4 | Flow trace pipeline §4 |
| B5 | Test inventory in schema §5 |
| D2 | Evidence store layout §6 |
| D3 | JSON schema contract §5 |
