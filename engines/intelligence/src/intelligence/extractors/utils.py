from __future__ import annotations

import re
from pathlib import Path
from typing import Iterator, List, Match, Tuple

from intelligence.models import DependencyItem


def rel_path(path: Path, repo_path: Path) -> str:
    return path.resolve().relative_to(repo_path.resolve()).as_posix()


def find_line_matches(lines: List[str], pattern: re.Pattern) -> Iterator[Tuple[int, Match]]:
    for idx, line in enumerate(lines, start=1):
        match = pattern.search(line)
        if match:
            yield idx, match


def parse_pyproject_dependencies(path: Path) -> List[DependencyItem]:
    items: List[DependencyItem] = []
    if not path.exists():
        return items
    lines = path.read_text(encoding="utf-8").splitlines()
    in_deps = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("dependencies") and "=" in stripped:
            in_deps = True
            continue
        if in_deps:
            if stripped == "]":
                break
            match = re.search(r'["\']([^"\']+)["\']', stripped)
            if match:
                spec = match.group(1)
                name = spec.split("[")[0].split("<")[0].split(">")[0].split("=")[0].strip()
                ver_match = re.search(r">=([^,\"\']+)", spec)
                items.append(
                    DependencyItem(
                        name=name,
                        version=ver_match.group(1) if ver_match else None,
                        source="pyproject.toml",
                    )
                )
    return items


def parse_requirements(path: Path) -> List[DependencyItem]:
    items: List[DependencyItem] = []
    if not path.exists():
        return items
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = re.match(r"^([a-zA-Z0-9_-]+)(?:[=<>!~]+(.+))?", stripped)
        if match:
            items.append(
                DependencyItem(
                    name=match.group(1),
                    version=match.group(2),
                    source="requirements.txt",
                )
            )
    return items


def parse_package_json(path: Path) -> List[DependencyItem]:
    import json

    items: List[DependencyItem] = []
    if not path.exists():
        return items
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return items
    for section in ("dependencies", "devDependencies"):
        for name, version in data.get(section, {}).items():
            items.append(DependencyItem(name=name, version=version, source="package.json"))
    return items


def parse_pom_xml(path: Path) -> List[DependencyItem]:
    items: List[DependencyItem] = []
    if not path.exists():
        return items
    content = path.read_text(encoding="utf-8")
    for artifact, version in re.findall(
        r"<artifactId>([^<]+)</artifactId>\s*<version>([^<]+)</version>", content
    ):
        items.append(DependencyItem(name=artifact, version=version, source="pom.xml"))
    return items
