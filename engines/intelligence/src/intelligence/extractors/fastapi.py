from __future__ import annotations

import re
from pathlib import Path
from typing import List

from intelligence.extractors.utils import (
    find_line_matches,
    parse_pyproject_dependencies,
    parse_requirements,
    rel_path,
)
from intelligence.models import ApiItem, DependencyItem, InventoryItem, ModelItem
from intelligence.walker import read_lines

SERVICE_CLASS = re.compile(r"^class\s+(\w+Service)\s*[:\(]")
ROUTER_DEF = re.compile(r"router\s*=\s*APIRouter\s*\(([^)]*)\)")
ROUTER_PREFIX = re.compile(r'prefix\s*=\s*["\']([^"\']+)["\']')
API_DECORATOR = re.compile(
    r"@router\.(get|post|put|delete|patch)\s*\(\s*['\"]([^'\"]*)['\"]"
)
API_DECORATOR_APP = re.compile(
    r"@app\.(get|post|put|delete|patch)\s*\(\s*['\"]([^'\"]*)['\"]"
)
HANDLER_DEF = re.compile(r"^(?:async\s+)?def\s+(\w+)\s*\(")
MODEL_CLASS = re.compile(r"^class\s+(\w+)\s*\(\s*Base")
TABLENAME = re.compile(r'__tablename__\s*=\s*["\']([^"\']+)["\']')
TEST_FUNC = re.compile(r"^def\s+(test_\w+)\s*\(")


def extract_fastapi(repo_path: Path, files: List[Path]) -> dict:
    services: List[InventoryItem] = []
    controllers: List[InventoryItem] = []
    apis: List[ApiItem] = []
    models: List[ModelItem] = []
    tests: List[InventoryItem] = []

    for path in files:
        if path.suffix != ".py":
            continue
        rel = rel_path(path, repo_path)
        lines = read_lines(path)

        if "/services/" in rel.replace("\\", "/") or rel.endswith("_service.py"):
            for line_no, match in find_line_matches(lines, SERVICE_CLASS):
                services.append(InventoryItem(name=match.group(1), file=rel, line=line_no))

        if "/routers/" in rel.replace("\\", "/") or "router" in path.name:
            prefix = ""
            for line_no, match in find_line_matches(lines, ROUTER_DEF):
                prefix_match = ROUTER_PREFIX.search(match.group(1))
                prefix = prefix_match.group(1) if prefix_match else ""
                controllers.append(
                    InventoryItem(
                        name=f"{path.stem}.router",
                        file=rel,
                        line=line_no,
                        extra={"prefix": prefix},
                    )
                )

            current_prefix = prefix
            for line_no, line in enumerate(lines, start=1):
                prefix_match = ROUTER_PREFIX.search(line)
                if prefix_match:
                    current_prefix = prefix_match.group(1)

                dec = API_DECORATOR.search(line) or API_DECORATOR_APP.search(line)
                if dec:
                    method, route_path = dec.group(1).upper(), dec.group(2)
                    full_path = _join_paths(current_prefix, route_path)
                    handler = _next_handler(lines, line_no)
                    apis.append(
                        ApiItem(
                            method=method,
                            path=full_path,
                            handler=handler or "unknown",
                            file=rel,
                            line=line_no,
                        )
                    )

        if "/models/" in rel.replace("\\", "/") or rel.startswith("app/models"):
            for line_no, match in find_line_matches(lines, MODEL_CLASS):
                table = _find_tablename(lines, line_no)
                models.append(
                    ModelItem(name=match.group(1), table=table, file=rel, line=line_no)
                )

        if path.name.startswith("test_") or "/tests/" in rel.replace("\\", "/"):
            for line_no, match in find_line_matches(lines, TEST_FUNC):
                tests.append(InventoryItem(name=match.group(1), file=rel, line=line_no))

    dependencies = _fastapi_dependencies(repo_path)
    return {
        "services": services,
        "controllers": controllers,
        "apis": apis,
        "models": models,
        "tests": tests,
        "dependencies": dependencies,
    }


def _join_paths(prefix: str, route: str) -> str:
    if not prefix:
        return route or "/"
    if not route:
        return prefix
    return f"{prefix.rstrip('/')}/{route.lstrip('/')}"


def _next_handler(lines: List[str], decorator_line: int) -> str:
    for line in lines[decorator_line:]:
        match = HANDLER_DEF.match(line.strip())
        if match:
            return match.group(1)
    return ""


def _find_tablename(lines: List[str], class_line: int) -> str:
    for line in lines[class_line - 1 : class_line + 10]:
        match = TABLENAME.search(line)
        if match:
            return match.group(1)
    return ""


def _fastapi_dependencies(repo_path: Path) -> List[DependencyItem]:
    deps: List[DependencyItem] = []
    candidates = [repo_path / "pyproject.toml"]
    candidates.extend(repo_path.rglob("pyproject.toml"))
    for candidate in candidates:
        if ".venv" in candidate.parts or "node_modules" in candidate.parts:
            continue
        deps.extend(parse_pyproject_dependencies(candidate))
    deps.extend(parse_requirements(repo_path / "requirements.txt"))
    seen = set()
    unique: List[DependencyItem] = []
    for item in deps:
        key = (item.name, item.source)
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique
