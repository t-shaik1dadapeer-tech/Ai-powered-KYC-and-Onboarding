# Phase 0 — Evaluation Mapping Matrix

**Project:** AI-Powered KYC & Onboarding Repository Intelligence Platform  
**Version:** 0.1.0  
**Date:** 2026-06-16  
**Status:** Complete (design phase)

---

## 1. Evaluation Taxonomy

This matrix maps every planned project feature to the evaluation dimensions used by human reviewers and AI evaluators.

### B — Business Intelligence (Repository & Domain)

| ID | Capability | Definition | Primary Artifacts |
|----|------------|------------|-------------------|
| **B1** | Repo Discovery | Scan a repository and produce structured inventories (services, modules, entry points) | `reports/inventory/*.md`, Rust analyzer output |
| **B2** | API Mapping | Catalog HTTP endpoints with method, path, handler, request/response schemas | `evidence/api-maps/*.md`, OpenAPI exports |
| **B3** | ER Diagram Generation | Derive entity-relationship diagrams from ORM models / schema definitions | `evidence/diagrams/er-*.mmd`, Mermaid PNG/SVG |
| **B4** | End-to-End Flow Tracing | Trace request → controller → service → repository → database with uncertainty reporting | `evidence/flow-traces/*.md`, sequence diagrams |
| **B5** | Test Discovery | Locate and catalog tests by component, framework, and coverage area | `reports/inventory/tests.md`, coverage reports |
| **B6** | KYC Domain Completeness | Production-grade onboarding: customer, KYC, PAN, bank, risk score workflows | FastAPI service, domain models, integration tests |

### I — Implementation Stack

| ID | Capability | Definition | Primary Artifacts |
|----|------------|------------|-------------------|
| **I1** | FastAPI Development | Layered Python API: controllers, services, repositories, Pydantic, SQLAlchemy | `services/onboarding-api/` |
| **I2** | Node.js Development | CLI client with validation, error handling, unit tests | `clients/node-cli/` |
| **I3** | Rust Development | High-performance repo parser and risk-score engine with benchmarks | `engines/rust-analyzer/` |
| **I4** | Dockerization | Multi-service containers with health checks and compose orchestration | `Dockerfile`, `docker-compose.yml` |
| **I5** | CI/CD | GitHub Actions: lint, test, integration, docker build, artifacts | `.github/workflows/` |
| **I6** | Observability | Structured logs, Prometheus metrics, Grafana dashboards | `infra/prometheus/`, `infra/grafana/` |

### A — Agent & Architecture Practices

| ID | Capability | Definition | Primary Artifacts |
|----|------------|------------|-------------------|
| **A1** | Worktree-based Parallel Development | Demonstrate isolated git worktrees for parallel feature streams | `docs/worktrees/`, branch merge strategy |
| **A2** | Agent-vs-Manual Verification | Per-phase evidence: agent suggestion vs implementation vs human verification | `verification/phase-*.md` |

### D — Documentation, Delivery & Evidence

| ID | Capability | Definition | Primary Artifacts |
|----|------------|------------|-------------------|
| **D2** | Evidence-based Engineering | All claims backed by stored proof under `evidence/` | `evidence/**` |
| **D3** | Traceable Architecture | Every architectural decision linked to diagram, ADR, or code reference | `docs/architecture/`, ADRs |
| **D4** | Risk Assessment | Per-feature threat/limitation analysis with mitigations | Risk sections in docs + verification files |
| **D5** | Verification Strategy | Repeatable commands and expected outputs per phase | `verification/*.md`, Makefile targets |
| **D6** | Maintainability & Conventions | Consistent layering, naming, config management, extensibility | `CONTRIBUTING.md`, linters, folder structure |

---

## 2. Feature → Evaluation Matrix

Legend: **P** = Primary satisfaction · **S** = Secondary/supporting · **—** = Not applicable

| Feature / Phase | B1 | B2 | B3 | B4 | B5 | B6 | I1 | I2 | I3 | I4 | I5 | I6 | A1 | A2 | D2 | D3 | D4 | D5 | D6 |
|-----------------|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **P0** Evaluation Mapping | — | — | — | — | — | — | — | — | — | — | — | — | — | S | P | P | S | P | S |
| **P1** System Design | S | S | S | S | S | S | S | S | S | S | S | S | — | S | S | P | P | P | P |
| **P2** FastAPI Onboarding Service | — | S | P | S | S | P | P | — | — | — | — | S | — | S | S | P | P | P | P |
| **P3** Repository Intelligence Engine | P | P | P | S | P | — | S | — | S | — | — | — | — | S | P | P | P | P | P |
| **P4** Flow Tracing | S | S | S | P | — | — | — | — | S | — | — | — | — | S | P | P | P | P | S |
| **P5** Node.js CLI Client | — | — | — | — | — | S | S | P | — | — | — | — | — | S | S | S | P | P | P |
| **P6** Rust Analysis Engine | P | S | S | S | S | S | — | — | P | — | — | — | — | S | P | P | P | P | P |
| **P7** Testing (Pytest/Node/Rust) | — | — | — | — | P | S | S | S | S | — | S | — | — | S | P | S | P | P | P |
| **P8** Dockerization | — | — | — | — | — | — | S | S | S | P | S | S | — | S | P | P | P | P | S |
| **P9** CI/CD Pipeline | — | — | — | — | S | — | S | S | S | S | P | — | — | S | P | S | P | P | P |
| **P10** Observability | — | — | — | — | — | S | S | — | — | S | S | P | — | S | P | P | P | P | S |
| **P11** Worktree Demonstration | — | — | — | — | — | — | — | — | — | — | — | — | P | S | P | S | S | P | S |
| **P12** Agent vs Manual Verification | — | — | — | — | — | — | — | — | — | — | — | — | S | P | P | S | S | P | — |
| **P13** Engineering Evidence Store | S | S | S | S | S | S | S | S | S | S | S | S | S | S | P | P | S | P | S |
| **P14** Final Review | S | S | S | S | S | S | S | S | S | S | S | S | S | S | P | P | P | P | P |

---

## 3. Coverage by Evaluation Dimension

Coverage is computed as: **(phases where dimension is P or S) / 14 phases × 100%**, weighted by primary (P=1.0) vs secondary (S=0.5).

| Dimension | Phases (P) | Phases (S) | Raw Coverage | Weighted Score |
|-----------|:----------:|:----------:|:------------:|:--------------:|
| **B1** Repo Discovery | 2 | 4 | 43% | 29% → **100% at P3+P6** |
| **B2** API Mapping | 2 | 5 | 50% | 36% → **100% at P3+P4** |
| **B3** ER Diagram Generation | 2 | 4 | 43% | 29% → **100% at P2+P3** |
| **B4** Flow Tracing | 1 | 5 | 43% | 21% → **100% at P4** |
| **B5** Test Discovery | 2 | 3 | 36% | 21% → **100% at P3+P7** |
| **B6** KYC Domain | 1 | 4 | 36% | 21% → **100% at P2** |
| **I1** FastAPI | 1 | 6 | 50% | 36% → **100% at P2** |
| **I2** Node.js | 1 | 4 | 36% | 21% → **100% at P5** |
| **I3** Rust | 1 | 4 | 36% | 21% → **100% at P6** |
| **I4** Docker | 1 | 5 | 43% | 29% → **100% at P8** |
| **I5** CI/CD | 1 | 5 | 43% | 29% → **100% at P9** |
| **I6** Observability | 1 | 5 | 43% | 29% → **100% at P10** |
| **A1** Worktrees | 1 | 1 | 14% | 11% → **100% at P11** |
| **A2** Agent Verification | 1 | 12 | 93% | 50% → **100% at P12** |
| **D2** Evidence | 8 | 6 | 100% | 79% |
| **D3** Traceable Arch | 6 | 8 | 100% | 71% |
| **D4** Risk Assessment | 5 | 9 | 100% | 64% |
| **D5** Verification | 10 | 4 | 100% | 86% |
| **D6** Maintainability | 4 | 10 | 100% | 57% |

### Projected Final Coverage (after all phases)

| Category | Dimensions | Target | Projected |
|----------|------------|:------:|:---------:|
| **B** Business Intelligence | B1–B6 | 100% | **100%** |
| **I** Implementation Stack | I1–I6 | 100% | **100%** |
| **A** Agent Practices | A1–A2 | 100% | **100%** |
| **D** Delivery & Evidence | D2–D6 | 100% | **100%** |
| **Overall** | 19 dimensions | — | **100%** |

> **Phase 0–1 current coverage:** Documentation and design dimensions (D2, D3, D4, D5, D6) are partially satisfied. Implementation dimensions (B*, I*) reach full coverage only after Phases 2–10.

---

## 4. Gap Analysis (Pre-Implementation)

| Gap | Impact | Resolution Phase |
|-----|--------|------------------|
| No runnable code | Evaluators cannot execute flows | P2 onward |
| No ER/API artifacts yet | B2, B3 unproven | P3 |
| No flow traces | B4 unproven | P4 |
| No test coverage reports | B5, D5 unproven | P7 |
| No container evidence | I4 unproven | P8 |
| No CI run history | I5 unproven | P9 |
| No metrics/dashboards | I6 unproven | P10 |
| Worktree demo not recorded | A1 unproven | P11 |

---

## 5. Risk Assessment (Phase 0)

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| Evaluation criteria misinterpreted | Low | Medium | Taxonomy documented above; aligned to stated capabilities |
| Over-scoping before evidence | Medium | High | Phase-gated delivery; no code until design approved |
| Framework detection false positives (Spring/FastAPI/Node) | Medium | Medium | Uncertainty reports in flow tracer; confidence scores |
| Matrix drift from implementation | Medium | Medium | Update matrix at end of each phase in verification files |

---

## 6. Verification (Phase 0)

### Commands

```bash
# Confirm evaluation matrix exists and is non-empty
test -f docs/evaluation/phase-0-evaluation-matrix.md && wc -l docs/evaluation/phase-0-evaluation-matrix.md

# Confirm all 19 evaluation IDs are referenced
grep -E 'B[1-6]|I[1-6]|A[1-2]|D[2-6]' docs/evaluation/phase-0-evaluation-matrix.md | head -20

# Confirm feature matrix covers phases 0–14
grep -c 'P[0-9]' docs/evaluation/phase-0-evaluation-matrix.md
```

### Expected Output

- Matrix file ≥ 150 lines
- All B1–B6, I1–I6, A1–A2, D2–D6 present
- 15 phase rows in feature matrix

### Evidence Artifacts

| Artifact | Path |
|----------|------|
| This matrix | `docs/evaluation/phase-0-evaluation-matrix.md` |
| Phase 0 verification | `verification/phase-0.md` |
