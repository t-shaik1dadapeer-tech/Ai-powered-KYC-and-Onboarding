from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from intelligence.extractors.fastapi import extract_fastapi
from intelligence.extractors.nodejs import extract_nodejs
from intelligence.extractors.spring_boot import extract_spring_boot
from intelligence.models import Inventories
from intelligence.tracing import trace_flows


def extract_inventories(framework: str, repo_path: Path, files: List[Path]) -> Inventories:
    if framework == "fastapi":
        data = extract_fastapi(repo_path, files)
    elif framework == "spring_boot":
        data = extract_spring_boot(repo_path, files)
    elif framework == "node_express":
        data = extract_nodejs(repo_path, files)
    else:
        data = {
            "services": [],
            "controllers": [],
            "apis": [],
            "models": [],
            "tests": [],
            "dependencies": [],
        }
    return Inventories(**data)


def extract_flow_traces(
    framework: str,
    repo_path: Path,
    inventories: Inventories,
    files: Optional[List[Path]] = None,
) -> List:
    from intelligence.walker import walk_repository

    if files is None:
        files = walk_repository(repo_path)
    return trace_flows(framework, repo_path, files, inventories)
