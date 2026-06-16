from __future__ import annotations

from pathlib import Path

from intelligence.models import AnalysisResult


def generate_api_map(result: AnalysisResult) -> str:
    lines = [
        "# API Map",
        "",
        f"**Repository:** `{result.repository}`",
        f"**Framework:** `{result.framework}` (confidence: {result.confidence:.0%})",
        f"**Generated:** {result.generated_at}",
        "",
        "## Endpoints",
        "",
        "| Method | Path | Handler | File |",
        "| --- | --- | --- | --- |",
    ]
    for api in result.inventories.apis:
        lines.append(f"| {api.method} | `{api.path}` | `{api.handler}` | `{api.file}:{api.line}` |")

    if not result.inventories.apis:
        lines.append("| — | _No endpoints detected_ | — | — |")

    lines.extend(["", "## Summary", "", f"- Total endpoints: **{len(result.inventories.apis)}**"])
    return "\n".join(lines) + "\n"


def write_api_map(result: AnalysisResult, output_dir: Path) -> str:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "api-map.md"
    path.write_text(generate_api_map(result), encoding="utf-8")
    return str(path)
