from __future__ import annotations

import re
from pathlib import Path
from typing import List

from intelligence.extractors.utils import find_line_matches, parse_pom_xml, rel_path
from intelligence.models import ApiItem, InventoryItem, ModelItem
from intelligence.walker import read_lines

REST_CONTROLLER = re.compile(r"@RestController")
CONTROLLER_CLASS = re.compile(r"^public\s+class\s+(\w+)")
SERVICE_ANNOT = re.compile(r"@Service")
SERVICE_CLASS = re.compile(r"^public\s+class\s+(\w+Service)")
GET_MAPPING = re.compile(r'@GetMapping\s*(?:\(\s*(?:value\s*=\s*)?["\']([^"\']*)["\']\s*\))?')
POST_MAPPING = re.compile(r'@PostMapping\s*(?:\(\s*(?:value\s*=\s*)?["\']([^"\']*)["\']\s*\))?')
REQUEST_MAPPING = re.compile(r'@RequestMapping\s*\(\s*["\']([^"\']*)["\']')
ENTITY_CLASS = re.compile(r"@Entity")
CLASS_NAME = re.compile(r"^public\s+class\s+(\w+)")
TABLE_ANNOT = re.compile(r'@Table\s*\(\s*name\s*=\s*["\']([^"\']+)["\']')
TEST_METHOD = re.compile(r"@Test")
TEST_METHOD_NAME = re.compile(r"^\s*(?:public\s+)?void\s+(\w+)\s*\(")


def extract_spring_boot(repo_path: Path, files: List[Path]) -> dict:
    services: List[InventoryItem] = []
    controllers: List[InventoryItem] = []
    apis: List[ApiItem] = []
    models: List[ModelItem] = []
    tests: List[InventoryItem] = []

    for path in files:
        if path.suffix not in {".java", ".kt"}:
            continue
        rel = rel_path(path, repo_path)
        lines = read_lines(path)
        text = "\n".join(lines)

        if "@Service" in text:
            for line_no, match in find_line_matches(lines, SERVICE_CLASS):
                services.append(InventoryItem(name=match.group(1), file=rel, line=line_no))

        if REST_CONTROLLER.search(text):
            class_name = ""
            for line_no, match in find_line_matches(lines, CONTROLLER_CLASS):
                class_name = match.group(1)
                controllers.append(InventoryItem(name=class_name, file=rel, line=line_no))

            base_path = ""
            for _, match in find_line_matches(lines, REQUEST_MAPPING):
                base_path = match.group(1)

            for line_no, line in enumerate(lines, start=1):
                for pattern, method in ((GET_MAPPING, "GET"), (POST_MAPPING, "POST")):
                    match = pattern.search(line)
                    if match:
                        route = match.group(1) if match.lastindex and match.group(1) else ""
                        apis.append(
                            ApiItem(
                                method=method,
                                path=_join_paths(base_path, route),
                                handler=class_name or path.stem,
                                file=rel,
                                line=line_no,
                            )
                        )

        if ENTITY_CLASS.search(text):
            name = ""
            table = ""
            for line_no, match in find_line_matches(lines, CLASS_NAME):
                name = match.group(1)
            for _, match in find_line_matches(lines, TABLE_ANNOT):
                table = match.group(1)
            if name:
                models.append(ModelItem(name=name, table=table or None, file=rel, line=1))

        if path.name.endswith("Test.java") or "test" in path.parts:
            for line_no, line in enumerate(lines, start=1):
                if TEST_METHOD.search(line):
                    for next_line in lines[line_no: line_no + 3]:
                        name_match = TEST_METHOD_NAME.search(next_line)
                        if name_match:
                            tests.append(
                                InventoryItem(
                                    name=name_match.group(1), file=rel, line=line_no
                                )
                            )
                            break

    dependencies = parse_pom_xml(repo_path / "pom.xml")
    return {
        "services": services,
        "controllers": controllers,
        "apis": apis,
        "models": models,
        "tests": tests,
        "dependencies": dependencies,
    }


def _join_paths(base: str, route: str) -> str:
    if not base:
        return route or "/"
    if not route:
        return base
    return f"{base.rstrip('/')}/{route.lstrip('/')}"
