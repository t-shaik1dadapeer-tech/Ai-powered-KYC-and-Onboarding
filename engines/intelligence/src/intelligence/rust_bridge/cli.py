"""Bridge to the Rust repository analyzer subprocess."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

from intelligence.models import AnalysisResult


class RustAnalyzerError(Exception):
    pass


def _rust_project_root() -> Path:
    return Path(__file__).resolve().parents[4] / "rust-analyzer"


def find_rust_analyzer_binary() -> Optional[Path]:
    root = _rust_project_root()
    for sub in ("release", "debug"):
        candidate = root / "target" / sub / "rust-analyzer"
        if candidate.is_file():
            return candidate
    return None


def run_rust_scan(repo_path: Path) -> Dict[str, Any]:
    binary = find_rust_analyzer_binary()
    if binary is None:
        raise RustAnalyzerError(
            "rust-analyzer binary not found. Run: cd engines/rust-analyzer && cargo build --release"
        )

    result = subprocess.run(
        [str(binary), "scan", "--path", str(repo_path.resolve())],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise RustAnalyzerError(result.stderr or result.stdout or "rust-analyzer failed")

    return json.loads(result.stdout)


def enrich_analysis_with_rust(result: AnalysisResult, repo_path: Path) -> AnalysisResult:
    try:
        rust_data = run_rust_scan(repo_path)
    except RustAnalyzerError:
        return result

    result.rust_scan = {
        "file_count": rust_data.get("file_count"),
        "graph_edges": len(rust_data.get("graph_edges", [])),
        "risk": rust_data.get("risk"),
        "scan_duration_ms": rust_data.get("scan_duration_ms"),
    }
    return result
