from __future__ import annotations

import re
from pathlib import Path
from typing import List

from intelligence.detectors.base import DetectionResult, FrameworkDetector
from intelligence.walker import read_lines

SPRING_PATTERNS = [
    (re.compile(r"@RestController"), 0.25),
    (re.compile(r"@SpringBootApplication"), 0.25),
    (re.compile(r"@Service"), 0.1),
    (re.compile(r"@Repository"), 0.1),
    (re.compile(r"@Entity"), 0.1),
]


class SpringBootDetector(FrameworkDetector):
    name = "spring_boot"

    def detect(self, repo_path: Path, files: List[Path]) -> DetectionResult:
        score = 0.0
        signals: List[str] = []

        for marker in ("pom.xml", "build.gradle", "build.gradle.kts"):
            if (repo_path / marker).exists():
                score += 0.2
                signals.append(f"{marker} present")
                break

        for path in files:
            if path.suffix not in {".java", ".kt"}:
                continue
            text = "\n".join(read_lines(path))
            for pattern, weight in SPRING_PATTERNS:
                if pattern.search(text):
                    score += weight
                    signals.append(f"{pattern.pattern} in {path.name}")

        return DetectionResult(
            framework="spring_boot",
            confidence=min(score, 1.0),
            signals=list(dict.fromkeys(signals)),
        )
