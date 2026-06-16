from __future__ import annotations

import json
import re
from pathlib import Path
from typing import List

from intelligence.detectors.base import DetectionResult, FrameworkDetector
from intelligence.walker import read_lines

EXPRESS_PATTERNS = [
    (re.compile(r"require\s*\(\s*['\"]express['\"]\s*\)"), 0.25),
    (re.compile(r"from\s+['\"]express['\"]"), 0.25),
    (re.compile(r"express\.Router\s*\("), 0.2),
    (re.compile(r"router\.(get|post|put|delete|patch)\s*\("), 0.15),
    (re.compile(r"app\.(get|post|put|delete|patch)\s*\("), 0.15),
]


class NodeJSDetector(FrameworkDetector):
    name = "node_express"

    def detect(self, repo_path: Path, files: List[Path]) -> DetectionResult:
        score = 0.0
        signals: List[str] = []

        pkg = repo_path / "package.json"
        if pkg.exists():
            try:
                data = json.loads(pkg.read_text(encoding="utf-8"))
                deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                if "express" in deps:
                    score += 0.3
                    signals.append("package.json lists express")
            except json.JSONDecodeError:
                pass

        for path in files:
            if path.suffix not in {".js", ".ts", ".mjs", ".cjs"}:
                continue
            text = "\n".join(read_lines(path))
            for pattern, weight in EXPRESS_PATTERNS:
                if pattern.search(text):
                    score += weight
                    signals.append(f"{pattern.pattern} in {path.name}")

        return DetectionResult(
            framework="node_express",
            confidence=min(score, 1.0),
            signals=list(dict.fromkeys(signals)),
        )
