from pathlib import Path

from intelligence.analyzer import RepositoryAnalyzer
from intelligence.models import FlowStep
from intelligence.tracing.index import CodeIndex
from intelligence.tracing.sequence import build_sequence_diagram
from intelligence.walker import walk_repository

ONBOARDING_API = Path(__file__).resolve().parents[3] / "services" / "onboarding-api"
FIXTURES_SPRING = Path(__file__).parent / "fixtures" / "spring"


def test_code_index_builds_service_repo_map():
    files = walk_repository(ONBOARDING_API)
    index = CodeIndex(ONBOARDING_API, files)
    assert "CustomerService" in index.services
    assert index.services["CustomerService"].repo_attrs.get("repo") == "CustomerRepository"
    assert index.model_tables.get("Customer") == "customers"


def test_trace_post_customers_full_chain():
    result = RepositoryAnalyzer().analyze(ONBOARDING_API)
    trace = next(t for t in result.flow_traces if t.endpoint == "POST /customers")
    layers = [s.layer for s in trace.steps]
    assert layers[0] == "controller"
    assert layers[1] == "service"
    assert "repository" in layers
    assert "database" in layers
    assert trace.steps[1].symbol == "CustomerService.create_customer"
    assert any(s.symbol == "CustomerRepository.create" for s in trace.steps)
    assert any(s.symbol == "table:customers" for s in trace.steps)
    assert trace.confidence >= 0.85
    assert trace.sequence_diagram is not None
    assert "sequenceDiagram" in trace.sequence_diagram


def test_trace_post_kyc_multi_repository():
    result = RepositoryAnalyzer().analyze(ONBOARDING_API)
    trace = next(t for t in result.flow_traces if t.endpoint == "POST /kyc")
    repo_steps = [s.symbol for s in trace.steps if s.layer == "repository"]
    assert "CustomerRepository.get_by_id" in repo_steps
    assert "KycRepository.create_submission" in repo_steps
    db_tables = [s.symbol for s in trace.steps if s.layer == "database"]
    assert any("kyc_submissions" in t for t in db_tables)


def test_sequence_diagram_generation():
    steps = [
        FlowStep(layer="controller", symbol="router.create"),
        FlowStep(layer="service", symbol="CustomerService.create"),
        FlowStep(layer="repository", symbol="CustomerRepository.create"),
        FlowStep(layer="database", symbol="table:customers", operation="INSERT"),
    ]
    diagram = build_sequence_diagram("POST /customers", steps)
    assert "Client->>+Controller" in diagram
    assert "Database" in diagram


def test_flow_reports_include_sequence_and_docs(tmp_path):
    output = tmp_path / "flows"
    result = RepositoryAnalyzer().analyze_and_write(ONBOARDING_API, output)
    assert (output / "sequence-diagrams").is_dir()
    assert (output / "flow-docs").is_dir()
    assert len(list((output / "sequence-diagrams").glob("*.mmd"))) == len(result.flow_traces)
    assert (output / "flow-tracing-report.md").read_text().count("Flow Steps") >= 1


def test_spring_flow_tracer():
    files = walk_repository(FIXTURES_SPRING)
    from intelligence.extractors.spring_boot import extract_spring_boot
    from intelligence.tracing.fastapi_tracer import SpringFlowTracer

    inventories = extract_spring_boot(FIXTURES_SPRING, files)
    from intelligence.models import Inventories

    inv = Inventories(**inventories)
    traces = SpringFlowTracer(FIXTURES_SPRING, files, inv).trace_all()
    assert traces
    assert any("Service" in s.symbol for t in traces for s in t.steps if s.layer == "service")
