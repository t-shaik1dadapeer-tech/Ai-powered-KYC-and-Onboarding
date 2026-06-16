from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List

from intelligence.walker import walk_repository


@dataclass
class DetectionResult:
    framework: str
    confidence: float
    signals: List[str]


class FrameworkDetector(ABC):
    name: str

    @abstractmethod
    def detect(self, repo_path: Path, files: List[Path]) -> DetectionResult:
        pass


def select_detector(repo_path: Path) -> DetectionResult:
    files = walk_repository(repo_path)
    from intelligence.detectors.fastapi import FastAPIDetector
    from intelligence.detectors.nodejs import NodeJSDetector
    from intelligence.detectors.spring_boot import SpringBootDetector

    detectors: List[FrameworkDetector] = [
        SpringBootDetector(),
        FastAPIDetector(),
        NodeJSDetector(),
    ]
    results = [d.detect(repo_path, files) for d in detectors]
    best = max(results, key=lambda r: r.confidence)
    if best.confidence < 0.3:
        return DetectionResult(
            framework="unknown", confidence=0.0, signals=["no framework matched"]
        )
    return best
