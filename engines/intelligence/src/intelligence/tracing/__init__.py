from __future__ import annotations

from pathlib import Path
from typing import List

from intelligence.models import FlowTrace, Inventories
from intelligence.tracing.fastapi_tracer import FastAPIFlowTracer, SpringFlowTracer


def trace_flows(
    framework: str, repo_path: Path, files: List[Path], inventories: Inventories
) -> List[FlowTrace]:
    if framework == "fastapi":
        return FastAPIFlowTracer(repo_path, files, inventories).trace_all()
    if framework == "spring_boot":
        return SpringFlowTracer(repo_path, files, inventories).trace_all()
    return _generic_flow_traces(inventories)


def _generic_flow_traces(inventories: Inventories) -> List[FlowTrace]:
    from intelligence.models import FlowStep
    from intelligence.tracing.sequence import build_sequence_diagram

    traces: List[FlowTrace] = []
    for api in inventories.apis:
        steps = [
            FlowStep(layer="controller", symbol=api.handler, file=api.file, line=api.line),
            FlowStep(layer="service", symbol="Service.handle"),
            FlowStep(layer="repository", symbol="Repository.persist"),
            FlowStep(layer="database", symbol="table:unknown", operation="SQL"),
        ]
        trace = FlowTrace(
            endpoint=f"{api.method} {api.path}",
            steps=steps,
            confidence=0.45,
            uncertainties=["Generic trace — deep resolver not available for this framework"],
            sequence_diagram=build_sequence_diagram(f"{api.method} {api.path}", steps),
        )
        trace.sync_chain_from_steps()
        traces.append(trace)
    return traces
