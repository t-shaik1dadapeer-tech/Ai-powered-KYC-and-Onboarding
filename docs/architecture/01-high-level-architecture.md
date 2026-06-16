# High-Level Architecture

## 1. System Context (C4 Level 1)

The platform serves three actor groups:

| Actor | Goal | Interface |
|-------|------|-----------|
| **Onboarding Operator** | Create customers, submit KYC, verify PAN/bank | Node.js CLI → FastAPI |
| **Engineering Analyst** | Understand unfamiliar repos (APIs, flows, tests) | CLI / agent → Intelligence Engine |
| **Platform Engineer** | Deploy, observe, verify CI/CD and containers | Docker Compose, Grafana, GitHub Actions |

```mermaid
C4Context
    title System Context — KYC & Repository Intelligence Platform

    Person(operator, "Onboarding Operator", "Submits KYC and verifies documents")
    Person(analyst, "Engineering Analyst", "Analyzes codebases for onboarding to teams")
    Person(platform, "Platform Engineer", "Operates infrastructure and CI")

    System(platform_sys, "KYC & Repo Intelligence Platform", "Onboarding API + codebase analyzer + observability")

    System_Ext(bank_api, "Bank Verification Provider", "Mock/stub in dev; external in prod")
    System_Ext(pan_api, "PAN Verification Provider", "Mock/stub in dev")
    System_Ext(github, "GitHub", "Source control and CI")

    Rel(operator, platform_sys, "CLI commands")
    Rel(analyst, platform_sys, "Analyze repo, generate reports")
    Rel(platform, platform_sys, "Deploy, monitor")
    Rel(platform_sys, bank_api, "Verify account")
    Rel(platform_sys, pan_api, "Verify PAN")
    Rel(platform, github, "CI/CD triggers")
```

---

## 2. Container View (C4 Level 2)

```mermaid
flowchart LR
    subgraph External
        USER[Users / Agents]
    end

    subgraph Docker Compose Stack
        direction TB
        NGINX[Optional Reverse Proxy]
        API[onboarding-api<br/>FastAPI :8000]
        INTEL[intelligence-orchestrator<br/>Python :8001]
        RUST[rust-analyzer<br/>CLI subprocess]
        NODE[node-cli]
        PG[(postgres :5432)]
        PROM[prometheus :9090]
        GRAF[grafana :3000]
    end

    USER --> NODE
    NODE --> API
    NODE --> INTEL
    USER --> API
    INTEL --> RUST
    API --> PG
    API --> PROM
    INTEL --> PROM
    PROM --> GRAF
```

---

## 3. Logical Architecture Layers

```mermaid
flowchart TB
    subgraph Presentation
        CLI[Node.js CLI]
        REST[FastAPI Routers]
        HEALTH[Health & Metrics Endpoints]
    end

    subgraph Application
        KYC_SVC[KYC Service]
        CUST_SVC[Customer Service]
        RISK_SVC[Risk Score Service]
        INTEL_SVC[Analysis Orchestrator]
    end

    subgraph Domain
        MODELS[SQLAlchemy Models]
        SCHEMAS[Pydantic Schemas]
        RULES[Risk Rules Engine]
    end

    subgraph Infrastructure
        REPOS[Repositories]
        EXT[External Verifiers]
        PARSER[Rust Parser FFI/CLI]
        DB[(PostgreSQL)]
        LOG[Structured Logging]
        MET[Prometheus Metrics]
    end

    CLI --> REST
    REST --> KYC_SVC
    REST --> CUST_SVC
    REST --> RISK_SVC
    KYC_SVC --> REPOS
    CUST_SVC --> REPOS
    RISK_SVC --> REPOS
    RISK_SVC --> RULES
    KYC_SVC --> EXT
    REPOS --> DB
    REST --> HEALTH
    INTEL_SVC --> PARSER
    CLI --> INTEL_SVC
    REST --> LOG
    REST --> MET
```

---

## 4. Deployment Topology

### Local Development

| Service | Port | Notes |
|---------|------|-------|
| FastAPI | 8000 | Hot reload via uvicorn |
| Intelligence API | 8001 | Optional HTTP wrapper for analyzer |
| PostgreSQL | 5432 | Persistent volume |
| Prometheus | 9090 | Scrapes `/metrics` |
| Grafana | 3000 | Pre-provisioned dashboard |

### Production Considerations (Future)

- Kubernetes with separate deployments per service
- Managed PostgreSQL (RDS/Cloud SQL)
- Secrets via vault; no credentials in compose files
- mTLS between services; API gateway for external traffic

---

## 5. Security Boundaries

```mermaid
flowchart TB
    subgraph Public
        CLI[CLI / API Gateway]
    end

    subgraph Application Trust Zone
        API[FastAPI]
        INTEL[Intelligence Orchestrator]
    end

    subgraph Data Trust Zone
        PG[(PostgreSQL)]
        EVID[evidence/ store]
    end

    CLI -->|HTTPS + API Key| API
    CLI -->|Local FS read| INTEL
    API -->|SQL + TLS| PG
    INTEL -->|Write reports| EVID
```

| Control | Implementation |
|---------|----------------|
| Input validation | Pydantic schemas on all endpoints |
| PII handling | PAN/bank masked in logs; encrypted at rest (Phase 2+) |
| Analyzer sandbox | Read-only repo access; path traversal checks |
| Secrets | Environment variables; never committed |

---

## 6. Non-Functional Requirements

| NFR | Target | Verification |
|-----|--------|--------------|
| API latency (p95) | < 200ms excluding external verifiers | Prometheus histogram |
| Analyzer throughput | > 500 files/sec (Rust) | Benchmark in `evidence/test-results/` |
| Availability | 99.9% (single-node dev: best effort) | Health checks in compose |
| Test coverage | ≥ 80% on critical paths | Coverage reports Phase 7 |
| Documentation | Every endpoint in OpenAPI + architecture docs | Manual + agent review |

---

## 7. Risk Assessment

| Risk | Mitigation |
|------|------------|
| Monolith creep in FastAPI | Enforce service/repository layers; lint import boundaries |
| Rust/Python integration complexity | Start with CLI subprocess; optional FFI later |
| False flow traces | Uncertainty report with confidence per edge |
| PII in evidence store | Redact before writing reports; `.gitignore` for sensitive runs |

---

## 8. Evaluation Mapping (Phase 1)

| Dimension | How This Document Satisfies |
|-----------|----------------------------|
| D3 | C4 diagrams, deployment table, traceability |
| D4 | Security boundaries, NFR, risk sections |
| B6 | KYC domain context defined |
| I1–I6 | Container view shows all stack components |
