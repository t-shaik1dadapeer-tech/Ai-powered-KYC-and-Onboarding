from __future__ import annotations

import re
from pathlib import Path
from typing import List

from intelligence.extractors.utils import find_line_matches, parse_package_json, rel_path
from intelligence.models import ApiItem, InventoryItem, ModelItem
from intelligence.walker import read_lines

ROUTE_CALL = re.compile(
    r"(?:router|app)\.(get|post|put|delete|patch)\s*\(\s*['\"]([^'\"]+)['\"]"
)
SERVICE_EXPORT = re.compile(r"(?:class|function)\s+(\w+Service)")
SCHEMA_DEF = re.compile(r"(?:mongoose\.model|Schema)\s*\(\s*['\"](\w+)['\"]")
TEST_IT = re.compile(r"^\s*(?:it|test)\s*\(\s*['\"]([^'\"]+)['\"]")
HANDLER = re.compile(r"(?:async\s+)?function\s+(\w+)|const\s+(\w+)\s*=\s*async")


def extract_nodejs(repo_path: Path, files: List[Path]) -> dict:
    services: List[InventoryItem] = []
    controllers: List[InventoryItem] = []
    apis: List[ApiItem] = []
    models: List[ModelItem] = []
    tests: List[InventoryItem] = []

    for path in files:
        if path.suffix not in {".js", ".ts", ".mjs", ".cjs"}:
            continue
        rel = rel_path(path, repo_path)
        lines = read_lines(path)

        is_service = (
            "/services/" in rel
            or path.name.endswith("Service.js")
            or path.name.endswith("Service.ts")
        )
        if is_service:
            for line_no, match in find_line_matches(lines, SERVICE_EXPORT):
                name = match.group(1)
                if name:
                    services.append(InventoryItem(name=name, file=rel, line=line_no))

        if "/routes/" in rel or "routes" in path.name.lower():
            controllers.append(
                InventoryItem(name=path.stem, file=rel, line=1, extra={"type": "route_module"})
            )

        for line_no, match in find_line_matches(lines, ROUTE_CALL):
            method, route_path = match.group(1).upper(), match.group(2)
            apis.append(
                ApiItem(
                    method=method,
                    path=route_path,
                    handler=path.stem,
                    file=rel,
                    line=line_no,
                )
            )

        for line_no, match in find_line_matches(lines, SCHEMA_DEF):
            models.append(
                ModelItem(name=match.group(1), table=match.group(1).lower(), file=rel, line=line_no)
            )

        if ".test." in path.name or ".spec." in path.name or "/tests/" in rel:
            for line_no, match in find_line_matches(lines, TEST_IT):
                tests.append(InventoryItem(name=match.group(1), file=rel, line=line_no))

    dependencies = parse_package_json(repo_path / "package.json")
    return {
        "services": services,
        "controllers": controllers,
        "apis": apis,
        "models": models,
        "tests": tests,
        "dependencies": dependencies,
    }
