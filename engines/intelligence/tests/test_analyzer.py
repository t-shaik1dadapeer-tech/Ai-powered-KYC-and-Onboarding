from pathlib import Path

from intelligence.analyzer import RepositoryAnalyzer
from intelligence.extractors.nodejs import extract_nodejs
from intelligence.extractors.spring_boot import extract_spring_boot
from intelligence.walker import walk_repository

FIXTURES = Path(__file__).parent / "fixtures"
ONBOARDING_API = Path(__file__).resolve().parents[3] / "services" / "onboarding-api"


def test_analyze_onboarding_api():
    result = RepositoryAnalyzer().analyze(ONBOARDING_API)
    assert result.framework == "fastapi"
    assert len(result.inventories.services) >= 4
    assert len(result.inventories.apis) >= 7
    assert len(result.inventories.models) >= 3
    assert len(result.inventories.tests) >= 5
    assert len(result.flow_traces) >= 5


def test_analyze_writes_reports(tmp_path):
    output = tmp_path / "reports"
    result = RepositoryAnalyzer().analyze_and_write(ONBOARDING_API, output)
    assert (output / "api-map.md").exists()
    assert (output / "er-diagram.mmd").exists()
    assert (output / "service-inventory.md").exists()
    assert (output / "flow-tracing-report.md").exists()
    assert (output / "analysis-manifest.json").exists()
    assert result.inventories.apis


def test_spring_extraction():
    spring_path = FIXTURES / "spring"
    data = extract_spring_boot(spring_path, walk_repository(spring_path))
    assert any(s.name == "UserService" for s in data["services"])
    assert any(c.name == "UserController" for c in data["controllers"])
    assert len(data["apis"]) >= 2
    assert any(m.name == "User" for m in data["models"])


def test_node_extraction():
    node_path = FIXTURES / "node"
    data = extract_nodejs(node_path, walk_repository(node_path))
    assert len(data["apis"]) >= 2
    assert any(d.name == "express" for d in data["dependencies"])
