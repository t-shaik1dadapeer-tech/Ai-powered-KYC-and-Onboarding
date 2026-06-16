from __future__ import annotations

from typing import List

from intelligence.models import FlowStep

LAYER_PARTICIPANT = {
    "controller": "Controller",
    "service": "Service",
    "repository": "Repository",
    "database": "Database",
    "external": "External",
}


def build_sequence_diagram(endpoint: str, steps: List[FlowStep]) -> str:
    if not steps:
        return "sequenceDiagram\n    Client->>API: request\n"

    lines = ["sequenceDiagram", "    autonumber", "    actor Client"]
    participants: List[str] = []
    for step in steps:
        participant = LAYER_PARTICIPANT.get(step.layer, step.layer.title())
        if participant not in participants:
            participants.append(participant)
            lines.append(f"    participant {participant}")

    prev = "Client"
    for step in steps:
        target = LAYER_PARTICIPANT.get(step.layer, step.layer.title())
        label = step.symbol
        if step.operation:
            label = f"{step.symbol} [{step.operation}]"
        lines.append(f"    {prev}->>+{target}: {label}")
        prev = target

    lines.append(f"    {prev}-->>-Client: {endpoint} response")
    return "\n".join(lines) + "\n"
