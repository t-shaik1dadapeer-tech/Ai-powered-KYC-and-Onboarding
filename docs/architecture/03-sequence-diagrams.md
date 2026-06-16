# Sequence Diagrams

## 1. Customer Onboarding (Happy Path)

```mermaid
sequenceDiagram
    autonumber
    actor Op as Operator
    participant CLI as Node CLI
    participant API as FastAPI Router
    participant CS as CustomerService
    participant CR as CustomerRepository
    participant DB as PostgreSQL

    Op->>CLI: customer-create --name --email
    CLI->>CLI: Validate input
    CLI->>API: POST /customers
    API->>CS: create_customer(dto)
    CS->>CS: Business validation
    CS->>CR: insert(customer)
    CR->>DB: INSERT INTO customers
    DB-->>CR: customer_id
    CR-->>CS: Customer entity
    CS-->>API: CustomerResponse
    API-->>CLI: 201 Created
    CLI-->>Op: Customer ID + summary
```

---

## 2. KYC Submission with PAN & Bank Verification

```mermaid
sequenceDiagram
    autonumber
    actor Op as Operator
    participant CLI as Node CLI
    participant API as FastAPI
    participant KS as KycService
    participant PS as PanVerificationService
    participant BS as BankVerificationService
    participant EXT_P as PAN Provider
    participant EXT_B as Bank Provider
    participant KR as KycRepository
    participant DB as PostgreSQL

    Op->>CLI: submit-kyc --customer-id --pan --bank
    CLI->>API: POST /kyc
    API->>KS: submit_kyc(dto)
    KS->>KR: get_customer(id)
    KR->>DB: SELECT customer
    DB-->>KR: customer row

    par PAN verification
        KS->>PS: verify_pan(pan)
        PS->>EXT_P: verify(pan)
        EXT_P-->>PS: verified / rejected
    and Bank verification
        KS->>BS: verify_bank(account, ifsc)
        BS->>EXT_B: verify(account)
        EXT_B-->>BS: verified / rejected
    end

    KS->>KR: save_kyc_submission(status)
    KR->>DB: INSERT kyc_submissions
    KS-->>API: KycStatusResponse
    API-->>CLI: 200 OK
    CLI-->>Op: KYC status
```

---

## 3. Risk Score Calculation

```mermaid
sequenceDiagram
    autonumber
    participant Client as Client / CLI
    participant API as FastAPI
    participant RS as RiskScoreService
    participant KR as KycRepository
    participant CR as CustomerRepository
    participant DB as PostgreSQL
    participant MET as Prometheus

    Client->>API: POST /risk-score {customer_id}
    API->>RS: calculate(customer_id)
    RS->>CR: get_customer(id)
    RS->>KR: get_latest_kyc(id)
    CR->>DB: SELECT
    KR->>DB: SELECT
    DB-->>RS: customer + kyc data
    RS->>RS: Apply rules (verification status, geography, velocity)
    RS->>MET: Observe risk_score_histogram
    RS-->>API: RiskScoreResponse
    API-->>Client: 200 {score, band, factors}
```

---

## 4. Repository Analysis (Intelligence Engine)

```mermaid
sequenceDiagram
    autonumber
    actor Analyst as Analyst / Agent
    participant CLI as Node CLI
    participant ORCH as Python Orchestrator
    participant DET as Framework Detector
    participant RUST as Rust Analyzer
    participant EXT as Extractors
    participant GEN as Report Generators
    participant FS as evidence/

    Analyst->>CLI: generate-report --path /repo
    CLI->>ORCH: POST /analyze {path}
    ORCH->>ORCH: Validate path (no traversal)
    ORCH->>DET: detect_framework(path)
    DET-->>ORCH: fastapi | spring | node

    ORCH->>RUST: rust-analyzer scan --path
    RUST->>RUST: Walk + parse files
    RUST-->>ORCH: JSON (files, imports, symbols)

    ORCH->>EXT: extract inventories
    EXT-->>ORCH: services, controllers, apis, models, tests, deps

    ORCH->>GEN: generate all reports
    GEN->>FS: Write markdown + mermaid
    GEN-->>ORCH: ReportManifest

    ORCH-->>CLI: 200 {manifest, summary}
    CLI-->>Analyst: Report paths + summary
```

---

## 5. End-to-End Flow Trace Generation

```mermaid
sequenceDiagram
    autonumber
    participant ORCH as Flow Trace Generator
    participant API_EXT as API Extractor
    participant SVC_EXT as Service Extractor
    participant REPO_EXT as Repository Extractor
    participant RUST as Rust Graph
    participant OUT as flow-traces/

    ORCH->>API_EXT: find route handlers
    API_EXT-->>ORCH: handlers[]

    loop each handler
        ORCH->>SVC_EXT: resolve callee chain
        SVC_EXT->>RUST: query import graph
        RUST-->>SVC_EXT: call edges
        SVC_EXT-->>ORCH: service methods[]
        ORCH->>REPO_EXT: resolve repository calls
        REPO_EXT-->>ORCH: repo + model + table
    end

    ORCH->>ORCH: Build sequence diagram (mermaid)
    ORCH->>ORCH: Flag uncertain edges
    ORCH->>OUT: flow-{endpoint}.md + uncertainty.md
```

---

## 6. CI/CD Pipeline Run

```mermaid
sequenceDiagram
    autonumber
    participant GH as GitHub Push
    participant GHA as GitHub Actions
    participant LINT as Linters
    participant TEST as Test Runners
    participant DOCK as Docker Build
    participant ART as Artifact Store

    GH->>GHA: Trigger workflow
    GHA->>LINT: ruff, eslint, clippy
    LINT-->>GHA: pass/fail

    par Python tests
        GHA->>TEST: pytest + coverage
    and Node tests
        GHA->>TEST: npm test
    and Rust tests
        GHA->>TEST: cargo test
    end

    TEST-->>GHA: results
    GHA->>DOCK: docker compose build
    DOCK-->>GHA: images
    GHA->>ART: Upload evidence/ci-results/
    GHA-->>GH: Status check
```

---

## 7. Health & Metrics Scrape

```mermaid
sequenceDiagram
    participant PROM as Prometheus
    participant API as FastAPI /metrics
    participant GRAF as Grafana

    loop every 15s
        PROM->>API: GET /metrics
        API-->>PROM: prometheus text format
    end

    GRAF->>PROM: PromQL queries
    PROM-->>GRAF: time series
```

---

## 8. API Endpoint Summary (Traceability)

| Endpoint | Sequence Diagram | Primary Service |
|----------|------------------|-----------------|
| `POST /customers` | §1 Customer Onboarding | CustomerService |
| `POST /kyc` | §2 KYC Submission | KycService |
| `POST /pan-verify` | §2 (PAN branch) | PanVerificationService |
| `POST /bank-verify` | §2 (Bank branch) | BankVerificationService |
| `POST /risk-score` | §3 Risk Score | RiskScoreService |
| `GET /customer/{id}` | §1 (read variant) | CustomerService |
| `GET /kyc-status/{id}` | §2 (read variant) | KycService |
| `GET /health` | §7 | Health router |
| `GET /metrics` | §7 | Metrics middleware |

---

## 9. Evaluation Mapping

| Dimension | Coverage |
|-----------|----------|
| B4 | §5 Flow trace generation sequence |
| B6 | §1–§3 KYC domain flows |
| I1 | FastAPI sequences |
| I5 | §6 CI/CD sequence |
| I6 | §7 Metrics scrape |
| D3 | Endpoint → diagram traceability table |
