from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Union

from intelligence.detectors.base import select_detector
from intelligence.extractors import extract_flow_traces, extract_inventories
from intelligence.generators.api_map import write_api_map
from intelligence.generators.er_diagram import write_er_diagram
from intelligence.generators.flow_trace import write_flow_reports
from intelligence.generators.markdown import write_inventory_reports
from intelligence.models import AnalysisResult
from intelligence.rust_bridge.cli import enrich_analysis_with_rust
from intelligence.walker import walk_repository


class RepositoryAnalyzer:
    def analyze(self, repo_path: Union[str, Path]) -> AnalysisResult:
        path = Path(repo_path).resolve()
        detection = select_detector(path)
        files = walk_repository(path)
        inventories = extract_inventories(detection.framework, path, files)
        flow_traces = extract_flow_traces(detection.framework, path, inventories, files)

        result = AnalysisResult(
            repository=str(path),
            framework=detection.framework,
            confidence=detection.confidence,
            generated_at=datetime.now(timezone.utc).isoformat(),
            inventories=inventories,
            flow_traces=flow_traces,
        )
        return enrich_analysis_with_rust(result, path)

    def analyze_and_write(
        self,
        repo_path: Union[str, Path],
        output_dir: Union[str, Path],
    ) -> AnalysisResult:
        result = self.analyze(repo_path)
        out = Path(output_dir)
        write_inventory_reports(result, out)
        write_er_diagram(result, out)
        write_api_map(result, out)
        write_flow_reports(result, out)
        manifest_path = out / "analysis-manifest.json"
        manifest_path.write_text(
            json.dumps(result.model_dump(), indent=2),
            encoding="utf-8",
        )
        return result


def analyze_repository(
    repo_path: Union[str, Path], output_dir: Optional[Union[str, Path]] = None
) -> AnalysisResult:
    analyzer = RepositoryAnalyzer()
    if output_dir:
        return analyzer.analyze_and_write(repo_path, output_dir)
    return analyzer.analyze(repo_path)
