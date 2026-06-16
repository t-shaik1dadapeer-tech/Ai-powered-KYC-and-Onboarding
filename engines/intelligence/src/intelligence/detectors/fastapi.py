from __future__ import annotations

import re
from pathlib import Path
from typing import List

from intelligence.detectors.base import DetectionResult, FrameworkDetector
from intelligence.walker import read_lines

FASTAPI_SIGNALS = [
    (re.compile(r"from fastapi import|import fastapi"), 0.25),
    (re.compile(r"APIRouter\s*\("), 0.2),
    (re.compile(r"uvicorn"), 0.1),
    (re.compile(r"services/onboarding-api|app/routers/"), 0.15),
]


class FastAPIDetector(FrameworkDetector):
    name = "fastapi"

    def detect(self, repo_path: Path, files: List[Path]) -> DetectionResult:
        score = 0.0
        signals: List[str] = []

        if (repo_path / "pyproject.toml").exists():
            content = read_lines(repo_path / "pyproject.toml")
            if any("fastapi" in line.lower() for line in content):
                score += 0.2
                signals.append("pyproject.toml lists fastapi")

        for path in files:
            if path.suffix != ".py":
                continue
            text = "\n".join(read_lines(path))
            for pattern, weight in FASTAPI_SIGNALS:
                if pattern.search(text):
                    score += weight
                    signals.append(f"{pattern.pattern} in {path.name}")

        if any("routers" in str(p) for p in files):
            score += 0.1
            signals.append("routers/ directory present")

        return DetectionResult(
            framework="fastapi",
            confidence=min(score, 1.0),
            signals=list(dict.fromkeys(signals)),
        )
