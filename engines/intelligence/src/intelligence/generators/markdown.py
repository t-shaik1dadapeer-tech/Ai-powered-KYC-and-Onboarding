from __future__ import annotations

from pathlib import Path
from typing import List

from intelligence.models import AnalysisResult


def inventory_markdown(title: str, items: List, columns: List[str]) -> str:
    lines = [f"# {title}", "", f"Total: **{len(items)}**", ""]
    if not items:
        lines.append("_No items found._")
        return "\n".join(lines) + "\n"

    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join(["---"] * len(columns)) + " |"
    lines.extend([header, sep])

    for item in items:
        row = []
        for col in columns:
            if col == "name":
                row.append(getattr(item, "name", ""))
            elif col == "file":
                row.append(getattr(item, "file", ""))
            elif col == "line":
                row.append(str(getattr(item, "line", "")))
            elif col == "method":
                row.append(getattr(item, "method", ""))
            elif col == "path":
                row.append(getattr(item, "path", ""))
            elif col == "handler":
                row.append(getattr(item, "handler", ""))
            elif col == "table":
                row.append(getattr(item, "table", "") or "—")
            elif col == "version":
                row.append(getattr(item, "version", "") or "—")
            elif col == "source":
                row.append(getattr(item, "source", ""))
            else:
                row.append("")
        lines.append("| " + " | ".join(row) + " |")

    return "\n".join(lines) + "\n"


def write_inventory_reports(result: AnalysisResult, output_dir: Path) -> List[str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    inv = result.inventories
    reports = {
        "service-inventory.md": inventory_markdown(
            "Service Inventory", inv.services, ["name", "file", "line"]
        ),
        "controller-inventory.md": inventory_markdown(
            "Controller Inventory", inv.controllers, ["name", "file", "line"]
        ),
        "api-inventory.md": inventory_markdown(
            "API Inventory", inv.apis, ["method", "path", "handler", "file", "line"]
        ),
        "model-inventory.md": inventory_markdown(
            "Model Inventory", inv.models, ["name", "table", "file", "line"]
        ),
        "test-inventory.md": inventory_markdown(
            "Test Inventory", inv.tests, ["name", "file", "line"]
        ),
        "dependency-inventory.md": inventory_markdown(
            "Dependency Inventory", inv.dependencies, ["name", "version", "source"]
        ),
    }
    written: List[str] = []
    for filename, content in reports.items():
        path = output_dir / filename
        path.write_text(content, encoding="utf-8")
        written.append(str(path))
    return written
