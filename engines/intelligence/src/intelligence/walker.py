from __future__ import annotations

import os
from pathlib import Path
from typing import List, Set

DEFAULT_IGNORE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    "dist",
    "build",
    "target",
    ".idea",
    ".cursor",
    "htmlcov",
    "evidence",
}

DEFAULT_IGNORE_FILES = {".DS_Store"}


def load_analyzerignore(repo_path: Path) -> Set[str]:
    ignore_file = repo_path / ".analyzerignore"
    patterns: Set[str] = set()
    if ignore_file.is_file():
        for line in ignore_file.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                patterns.add(stripped)
    return patterns


def should_skip_dir(name: str, ignore_patterns: Set[str]) -> bool:
    if name in DEFAULT_IGNORE_DIRS:
        return True
    return any(name == p or name.startswith(p.rstrip("/")) for p in ignore_patterns)


def walk_repository(repo_path: Path) -> List[Path]:
    repo_path = repo_path.resolve()
    if not repo_path.is_dir():
        raise ValueError(f"Repository path does not exist: {repo_path}")

    ignore_patterns = load_analyzerignore(repo_path)
    files: List[Path] = []

    for root, dirs, filenames in os.walk(repo_path):
        dirs[:] = [d for d in dirs if not should_skip_dir(d, ignore_patterns)]
        for filename in filenames:
            if filename in DEFAULT_IGNORE_FILES:
                continue
            full = Path(root) / filename
            rel = full.relative_to(repo_path).as_posix()
            if any(part in DEFAULT_IGNORE_DIRS for part in full.parts):
                continue
            if any(rel.startswith(p.rstrip("/")) for p in ignore_patterns):
                continue
            files.append(full)

    return sorted(files)


def read_lines(path: Path) -> List[str]:
    try:
        return path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []
