from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from intelligence.walker import read_lines

CLASS_DEF = re.compile(r"^class\s+(\w+)")
SERVICE_INIT_REPO = re.compile(r"self\._(\w+)\s*=\s*(\w+Repository)\s*\(")
REPO_INIT = re.compile(r"^class\s+(\w+Repository)")
METHOD_DEF = re.compile(r"^\s+def\s+(\w+)\s*\(")
TABLENAME = re.compile(r'__tablename__\s*=\s*["\']([^"\']+)["\']')
MODEL_CLASS = re.compile(r"^class\s+(\w+)\s*\(")
MODEL_USAGE = re.compile(r"\b([A-Z][a-zA-Z0-9_]+)\s*\(")
DB_GET = re.compile(r"self\._db\.get\s*\(\s*(\w+)")


@dataclass
class MethodInfo:
    name: str
    start_line: int
    body_lines: List[str]


@dataclass
class ClassInfo:
    name: str
    file: str
    repo_attrs: Dict[str, str] = field(default_factory=dict)  # attr -> RepositoryClass
    methods: Dict[str, MethodInfo] = field(default_factory=dict)


class CodeIndex:
    """Static index of services, repositories, and models for flow resolution."""

    def __init__(self, repo_path: Path, files: List[Path]):
        self.repo_path = repo_path
        self.services: Dict[str, ClassInfo] = {}
        self.repositories: Dict[str, ClassInfo] = {}
        self.model_tables: Dict[str, str] = {}
        self._build(files)

    def _build(self, files: List[Path]) -> None:
        for path in files:
            if path.suffix != ".py":
                continue
            rel = path.relative_to(self.repo_path).as_posix()
            lines = read_lines(path)
            self._index_models(rel, lines)
            self._index_class(rel, lines, "Service", self.services, index_repos=True)
            self._index_class(rel, lines, "Repository", self.repositories, index_repos=False)

    def _index_models(self, rel: str, lines: List[str]) -> None:
        current_class = ""
        for line_no, line in enumerate(lines, start=1):
            match = MODEL_CLASS.match(line.strip())
            if match and "Base" in line:
                current_class = match.group(1)
            tab_match = TABLENAME.search(line)
            if tab_match and current_class:
                self.model_tables[current_class] = tab_match.group(1)

    def _index_class(
        self,
        rel: str,
        lines: List[str],
        suffix: str,
        store: Dict[str, ClassInfo],
        index_repos: bool,
    ) -> None:
        current: Optional[ClassInfo] = None
        for line_no, line in enumerate(lines, start=1):
            stripped = line.strip()
            class_match = CLASS_DEF.match(stripped)
            if class_match and class_match.group(1).endswith(suffix):
                name = class_match.group(1)
                current = ClassInfo(name=name, file=rel)
                store[name] = current
                continue
            if current is None:
                continue
            if stripped.startswith("class ") and not stripped.endswith(f"{suffix}:"):
                current = None
                continue
            if index_repos:
                repo_match = SERVICE_INIT_REPO.search(line)
                if repo_match:
                    current.repo_attrs[repo_match.group(1)] = repo_match.group(2)
            method_match = METHOD_DEF.match(line)
            if method_match and not method_match.group(1).startswith("_"):
                method_name = method_match.group(1)
                body = self._extract_method_body(lines, line_no - 1)
                current.methods[method_name] = MethodInfo(
                    name=method_name, start_line=line_no, body_lines=body
                )

    def _extract_method_body(self, lines: List[str], start_idx: int) -> List[str]:
        if start_idx >= len(lines):
            return []
        def_line = lines[start_idx]
        indent = len(def_line) - len(def_line.lstrip())
        body: List[str] = []
        for line in lines[start_idx + 1 :]:
            if not line.strip():
                body.append(line)
                continue
            line_indent = len(line) - len(line.lstrip())
            if line_indent <= indent and line.strip():
                break
            body.append(line)
        return body

    def resolve_repo_table(
        self, repo_class: str, method_name: str
    ) -> Tuple[Optional[str], List[str]]:
        uncertainties: List[str] = []
        repo = self.repositories.get(repo_class)
        if not repo:
            return None, [f"Repository class not indexed: {repo_class}"]

        method = repo.methods.get(method_name)
        if not method:
            return None, [f"Repository method not found: {repo_class}.{method_name}"]

        body_text = "\n".join(method.body_lines)
        for model_name, table in self.model_tables.items():
            if re.search(rf"\b{model_name}\s*\(", body_text):
                return table, uncertainties
            db_get = DB_GET.search(body_text)
            if db_get and db_get.group(1) == model_name:
                return table, uncertainties

        hints = self._table_hints_from_method(method_name)
        if hints:
            return hints, [f"Table inferred from method name `{method_name}`"]

        return None, [f"Could not resolve table for {repo_class}.{method_name}"]

    @staticmethod
    def _table_hints_from_method(method_name: str) -> Optional[str]:
        mapping = {
            "create": None,
            "get_by_id": None,
            "get_by_email": "customers",
            "create_submission": "kyc_submissions",
            "save_pan_record": "pan_records",
            "save_bank_record": "bank_records",
            "update_submission_status": "kyc_submissions",
            "update_status": "customers",
            "save_risk_assessment": "risk_assessments",
        }
        return mapping.get(method_name)
