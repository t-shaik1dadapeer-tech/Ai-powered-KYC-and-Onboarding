from pathlib import Path

import pytest

from intelligence.analyzer import RepositoryAnalyzer
from intelligence.rust_bridge.cli import find_rust_analyzer_binary, run_rust_scan

ONBOARDING_API = Path(__file__).resolve().parents[3] / "services" / "onboarding-api"


@pytest.mark.skipif(find_rust_analyzer_binary() is None, reason="rust-analyzer not built")
def test_rust_scan_onboarding_api():
    data = run_rust_scan(ONBOARDING_API)
    assert data["file_count"] > 0
    assert "risk" in data
    assert data["risk"]["score"] <= 100


@pytest.mark.skipif(find_rust_analyzer_binary() is None, reason="rust-analyzer not built")
def test_analyzer_enriched_with_rust_scan():
    result = RepositoryAnalyzer().analyze(ONBOARDING_API)
    assert result.rust_scan is not None
    assert result.rust_scan.get("file_count", 0) > 0
