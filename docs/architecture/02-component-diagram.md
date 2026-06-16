# Component Diagram

## 1. FastAPI Onboarding Service

```mermaid
flowchart TB
    subgraph onboarding-api
        direction TB

        subgraph routers["app/routers/"]
            R_CUST[customers.py]
            R_KYC[kyc.py]
            R_VERIFY[verification.py]
            R_RISK[risk.py]
            R_HEALTH[health.py]
        end

        subgraph services["app/services/"]
            S_CUST[CustomerService]
            S_KYC[KycService]
            S_PAN[PanVerificationService]
            S_BANK[BankVerificationService]
            S_RISK[RiskScoreService]
        end

        subgraph repositories["app/repositories/"]
            REPO_CUST[CustomerRepository]
            REPO_KYC[KycRepository]
            REPO_DOC[DocumentRepository]
        end

        subgraph core["app/core/"]
            CFG[config.py]
            LOG[logging.py]
            EXC[exceptions.py]
            MET[metrics.py]
        end

        subgraph models["app/models/"]
            M_CUST[Customer]
            M_KYC[KycSubmission]
            M_PAN[PanRecord]
            M_BANK[BankRecord]
            M_RISK[RiskAssessment]
        end

        subgraph schemas["app/schemas/"]
            SCH_REQ[Request DTOs]
            SCH_RES[Response DTOs]
        end

        R_CUST --> S_CUST
        R_KYC --> S_KYC
        R_VERIFY --> S_PAN
        R_VERIFY --> S_BANK
        R_RISK --> S_RISK
        R_HEALTH --> MET

        S_CUST --> REPO_CUST
        S_KYC --> REPO_KYC
        S_KYC --> S_PAN
        S_KYC --> S_BANK
        S_RISK --> REPO_CUST
        S_RISK --> REPO_KYC

        REPO_CUST --> M_CUST
        REPO_KYC --> M_KYC
        S_PAN --> REPO_DOC
        S_BANK --> REPO_DOC

        routers --> schemas
        services --> schemas
    end

    DB[(PostgreSQL)]
    EXT_PAN[Pan Provider]
    EXT_BANK[Bank Provider]

    repositories --> DB
    S_PAN --> EXT_PAN
    S_BANK --> EXT_BANK
```

### Component Responsibilities

| Component | Responsibility | Depends On |
|-----------|----------------|------------|
| `routers/*` | HTTP binding, status codes, OpenAPI tags | services, schemas |
| `services/*` | Business rules, orchestration, transaction boundaries | repositories, external verifiers |
| `repositories/*` | CRUD, queries, persistence mapping | models, SQLAlchemy session |
| `models/*` | ORM entities, relationships | SQLAlchemy |
| `schemas/*` | Request/response validation | Pydantic |
| `core/config` | Settings from env (pydantic-settings) | — |
| `core/logging` | JSON structured logs (structlog) | — |
| `core/metrics` | Prometheus counters/histograms | prometheus_client |
| `core/exceptions` | Domain errors → HTTP mapping | — |

---

## 2. Repository Intelligence Engine

```mermaid
flowchart TB
    subgraph intelligence-engine
        direction TB

        CLI_ENTRY[analyze CLI / HTTP trigger]

        subgraph detectors["detectors/"]
            D_SPRING[SpringBootDetector]
            D_FAST[FastAPIDetector]
            D_NODE[NodeJSDetector]
        end

        subgraph extractors["extractors/"]
            E_SVC[ServiceExtractor]
            E_CTRL[ControllerExtractor]
            E_API[ApiExtractor]
            E_MODEL[ModelExtractor]
            E_TEST[TestExtractor]
            E_DEP[DependencyExtractor]
        end

        subgraph generators["generators/"]
            G_MD[MarkdownReportGenerator]
            G_ER[ErDiagramGenerator]
            G_API[ApiMapGenerator]
            G_FLOW[FlowTraceGenerator]
        end

        subgraph rust_bridge["rust_bridge/"]
            RB_CLI[RustAnalyzerCli]
            RB_PARSE[ParseResultAdapter]
        end

        CLI_ENTRY --> detectors
        detectors --> extractors
        extractors --> RB_CLI
        RB_CLI --> RB_PARSE
        RB_PARSE --> extractors
        extractors --> generators
        generators --> OUT[evidence/ + reports/]
    end

    REPO_PATH[Target Repository] --> CLI_ENTRY
```

### Detector Strategy

| Framework | Detection Signals | Extractors Used |
|-----------|-------------------|-----------------|
| **Spring Boot** | `@RestController`, `@Service`, `@Repository`, `pom.xml`/`build.gradle` | Controller, Service, Model (JPA), Test (JUnit) |
| **FastAPI** | `@router`, `APIRouter`, `services/`, `models/` | API, Service, Model, Test (pytest) |
| **Node.js** | `express.Router`, `routes/`, `package.json` | API, Service, Test (jest/vitest) |

---

## 3. Rust Analysis Engine

```mermaid
flowchart LR
    subgraph rust-analyzer
        MAIN[main.rs CLI]
        WALK[FileWalker]
        PARSE[LanguageParser]
        GRAPH[DependencyGraph]
        RISK[RiskCalculator]
        OUT_JSON[JSON Output]
    end

    MAIN --> WALK
    WALK --> PARSE
    PARSE --> GRAPH
    GRAPH --> RISK
    RISK --> OUT_JSON
```

| Module | Purpose |
|--------|---------|
| `file_walker` | Ignore `.git`, `node_modules`; respect `.analyzerignore` |
| `language_parser` | Tree-sitter / regex hybrid per language |
| `dependency_graph` | Import/require edges between files |
| `risk_calculator` | Heuristic score from complexity, test ratio, secrets patterns |

---

## 4. Node.js CLI Client

```mermaid
flowchart TB
    subgraph node-cli
        BIN[bin/kyc-cli.js]
        CMD_CREATE[commands/customer-create]
        CMD_KYC[commands/submit-kyc]
        CMD_REPORT[commands/generate-report]
        API_CLIENT[lib/api-client]
        ANALYZER_CLIENT[lib/analyzer-client]
        VALID[lib/validators]
    end

    BIN --> CMD_CREATE
    BIN --> CMD_KYC
    BIN --> CMD_REPORT
    CMD_CREATE --> API_CLIENT
    CMD_KYC --> API_CLIENT
    CMD_REPORT --> ANALYZER_CLIENT
    CMD_CREATE --> VALID
    CMD_KYC --> VALID
```

---

## 5. Observability Components

```mermaid
flowchart LR
    API[FastAPI /metrics] --> PROM[Prometheus]
    INTEL[Intelligence /metrics] --> PROM
    PROM --> GRAF[Grafana Dashboards]
    API --> LOGS[JSON Logs stdout]
    LOGS --> COLLECT[Future: Loki/ELK]
```

| Metric | Type | Labels |
|--------|------|--------|
| `http_requests_total` | Counter | method, path, status |
| `http_request_duration_seconds` | Histogram | method, path |
| `kyc_submissions_total` | Counter | status |
| `risk_score_histogram` | Histogram | band (low/medium/high) |
| `analyzer_runs_total` | Counter | framework, status |
| `analyzer_duration_seconds` | Histogram | framework |

---

## 6. Cross-Component Dependencies

```mermaid
flowchart TB
    NODE[node-cli] --> API[onboarding-api]
    NODE --> INTEL[intelligence-engine]
    INTEL --> RUST[rust-analyzer]
    CI[GitHub Actions] --> API
    CI --> INTEL
    CI --> RUST
    CI --> NODE
    AGENT[AI Agent] --> INTEL
    AGENT --> EVID[evidence/]
```

---

## 7. Evaluation Mapping

| Dimension | Coverage |
|-----------|----------|
| B1–B5 | Intelligence engine component breakdown |
| B6 | FastAPI KYC component model |
| I1–I3 | Per-service component diagrams |
| I6 | Observability component metrics |
| D3 | Component → responsibility traceability |
| D6 | Layered architecture conventions |
