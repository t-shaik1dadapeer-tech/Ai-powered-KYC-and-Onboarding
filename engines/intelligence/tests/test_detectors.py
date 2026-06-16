from pathlib import Path

from intelligence.detectors.base import select_detector
from intelligence.detectors.nodejs import NodeJSDetector
from intelligence.detectors.spring_boot import SpringBootDetector
from intelligence.walker import walk_repository

FIXTURES = Path(__file__).parent / "fixtures"
ONBOARDING_API = Path(__file__).resolve().parents[3] / "services" / "onboarding-api"


def test_detect_fastapi_onboarding():
    result = select_detector(ONBOARDING_API)
    assert result.framework == "fastapi"
    assert result.confidence >= 0.5


def test_detect_spring_fixture():
    spring_path = FIXTURES / "spring"
    result = SpringBootDetector().detect(spring_path, walk_repository(spring_path))
    assert result.framework == "spring_boot"
    assert result.confidence >= 0.4


def test_detect_node_fixture():
    node_path = FIXTURES / "node"
    result = NodeJSDetector().detect(node_path, walk_repository(node_path))
    assert result.framework == "node_express"
    assert result.confidence >= 0.4


def test_walk_skips_node_modules(tmp_path):
    repo = tmp_path / "repo"
    (repo / "node_modules" / "pkg").mkdir(parents=True)
    (repo / "node_modules" / "pkg" / "index.js").write_text("module.exports = {}")
    (repo / "app.py").write_text("print('ok')")
    files = walk_repository(repo)
    rel_paths = [f.relative_to(repo).as_posix() for f in files]
    assert rel_paths == ["app.py"]
