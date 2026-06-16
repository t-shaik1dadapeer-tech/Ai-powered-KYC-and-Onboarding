from __future__ import annotations

from pathlib import Path
from typing import List

from intelligence.models import AnalysisResult, ModelItem


def generate_er_diagram(models: List[ModelItem]) -> str:
    lines = ["erDiagram"]
    if not models:
        lines.append("    PLACEHOLDER {")
        lines.append("        string note")
        lines.append('        string "No models detected"')
        lines.append("    }")
        return "\n".join(lines) + "\n"

    for model in models:
        table = model.table or model.name.lower()
        lines.append(f"    {table.upper()} {{")
        lines.append("        uuid id PK")
        lines.append("        string name")
        lines.append("        datetime created_at")
        lines.append("    }")

    if len(models) >= 2:
        parent = (models[0].table or models[0].name).upper()
        child = (models[1].table or models[1].name).upper()
        lines.append(f"    {parent} ||--o{{ {child} : has")

    return "\n".join(lines) + "\n"


def write_er_diagram(result: AnalysisResult, output_dir: Path) -> str:
    output_dir.mkdir(parents=True, exist_ok=True)
    content = generate_er_diagram(result.inventories.models)
    path = output_dir / "er-diagram.mmd"
    path.write_text(content, encoding="utf-8")
    return str(path)
