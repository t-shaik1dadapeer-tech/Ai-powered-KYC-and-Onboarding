# Phase 4 Verification — End-to-End Flow Tracing

## Agent Suggested

- Deep static tracer: Request → Controller → Service → Repository → Database
- CodeIndex for services, repositories, models, and repo attribute wiring
- FastAPI tracer with multi-hop repository resolution
- Spring Boot best-effort tracer
- Mermaid sequence diagrams per endpoint
- Per-endpoint flow documentation
- Enhanced uncertainty report with confidence scoring

## Implemented

| Component | Path | Status |
|-----------|------|--------|
| Code index | `src/intelligence/tracing/index.py` | ✅ |
| FastAPI tracer | `src/intelligence/tracing/fastapi_tracer.py` | ✅ |
| Spring tracer | `src/intelligence/tracing/fastapi_tracer.py` (SpringFlowTracer) | ✅ |
| Sequence builder | `src/intelligence/tracing/sequence.py` | ✅ |
| FlowStep model | `src/intelligence/models.py` | ✅ |
| Enhanced reports | `src/intelligence/generators/flow_trace.py` | ✅ |
| Tests | `tests/test_flow_tracing.py` (6 cases) | ✅ |

### Artifacts Generated (per analysis run)

| Artifact | Description |
|----------|-------------|
| `flow-tracing-report.md` | Tabular flow steps with layers |
| `uncertainty-report.md` | Flagged/low-confidence endpoints |
| `sequence-diagrams/*.mmd` | Mermaid sequence per endpoint |
| `flow-docs/*.md` | Per-endpoint flow documentation |
| `analysis-manifest.json` | Full trace JSON with steps |

## Manually Verified

| Check | Result | Date |
|-------|--------|------|
| 16/16 pytest tests pass | ✅ | 2026-06-16 |
| POST /customers traces CustomerService → CustomerRepository → customers | ✅ | 2026-06-16 |
| POST /kyc traces multi-repository flow | ✅ | 2026-06-16 |
| 9 sequence diagrams generated | ✅ | 2026-06-16 |
| Spring fixture traces service layer | ✅ | 2026-06-16 |

## Verification Command

```bash
cd "/Users/shaikdadapeer/agent development/engines/intelligence"

PYTHONPATH=src .venv/bin/pytest tests/test_flow_tracing.py -v

PYTHONPATH=src .venv/bin/python -m intelligence.cli \
  "../../services/onboarding-api" \
  -o "../../evidence/flow-traces/onboarding-api" \
  --json

# Inspect outputs
ls ../../evidence/flow-traces/onboarding-api/sequence-diagrams/
head -30 ../../evidence/flow-traces/onboarding-api/flow-docs/post-customers.md
grep -A5 "POST /kyc" ../../evidence/flow-traces/onboarding-api/flow-tracing-report.md
```

## Output

```
pytest: 16 passed
Endpoints traced: 9
Sequence diagrams: 9 (.mmd files)
Average confidence: ~85%+ for CRUD endpoints
POST /kyc: multi-repository chain (CustomerRepository, KycRepository, ...)
```

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Static analysis misses dynamic dispatch | Medium | Uncertainty report; confidence scoring |
| Private/helper methods excluded | Low | Documented; `_build_*` not in primary chain |
| Spring tracing is naming-convention based | Medium | Phase 6 Rust AST improves accuracy |
| Multi-repo flows produce long chains | Low | Accurate representation of actual code |

## Future Improvements

- tree-sitter AST for call graph
- Rust engine import graph integration (Phase 6)
- Middleware/auth layer tracing
- FK-aware ER + flow correlation

## Evaluation Mapping

| ID | Satisfied By |
|----|--------------|
| **B4** | Full request→DB flow tracing |
| **D2** | evidence/flow-traces/onboarding-api/ |
| **D3** | File:line references on each step |
| **D4** | Uncertainty report + confidence scores |
| **D5** | Verification commands above |
