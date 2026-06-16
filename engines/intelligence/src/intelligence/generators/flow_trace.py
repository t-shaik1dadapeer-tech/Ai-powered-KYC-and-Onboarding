from __future__ import annotations

import re
from pathlib import Path
from typing import List

from intelligence.models import AnalysisResult, FlowTrace


def generate_flow_trace_report(traces: List[FlowTrace]) -> str:
    lines = [
        "# Flow Tracing Report",
        "",
        "End-to-end traces: **Request → Controller → Service → Repository → Database**",
        "",
    ]
    if not traces:
        lines.append("_No flow traces generated._")
        return "\n".join(lines) + "\n"

    avg_conf = sum(t.confidence for t in traces) / len(traces)
    lines.extend(
        [
            f"**Endpoints traced:** {len(traces)}",
            f"**Average confidence:** {avg_conf:.0%}",
            "",
        ]
    )

    for trace in traces:
        lines.extend([f"## {trace.endpoint}", "", f"**Confidence:** {trace.confidence:.0%}", ""])
        lines.append("### Flow Steps")
        lines.extend(["", "| # | Layer | Symbol | File |", "| --- | --- | --- | --- |"])
        for idx, step in enumerate(trace.steps, start=1):
            loc = f"`{step.file}:{step.line}`" if step.file and step.line else "—"
            lines.append(f"| {idx} | {step.layer} | `{step.symbol}` | {loc} |")
        if trace.uncertainties:
            lines.extend(["", "### Uncertainties", ""])
            for item in trace.uncertainties:
                lines.append(f"- {item}")
        lines.append("")

    return "\n".join(lines) + "\n"


def generate_uncertainty_report(traces: List[FlowTrace]) -> str:
    lines = [
        "# Uncertainty Report",
        "",
        "Documents low-confidence edges and unresolved symbols in flow traces.",
        "",
    ]
    flagged = [t for t in traces if t.uncertainties]
    high_conf = [t for t in traces if t.confidence >= 0.85 and not t.uncertainties]
    lines.extend(
        [
            f"- Endpoints with uncertainties: **{len(flagged)}** / {len(traces)}",
            f"- Fully resolved (≥85%, no uncertainties): **{len(high_conf)}**",
            "",
        ]
    )

    if flagged:
        lines.append("## Flagged Endpoints")
        lines.append("")
        for trace in flagged:
            lines.append(f"### {trace.endpoint} ({trace.confidence:.0%})")
            for item in trace.uncertainties:
                lines.append(f"- {item}")
            lines.append("")

    low = [t for t in traces if t.confidence < 0.7]
    if low:
        lines.extend(["## Low Confidence (<70%)", ""])
        for trace in low:
            lines.append(f"- {trace.endpoint}: {trace.confidence:.0%}")

    if not flagged and not low:
        lines.append("_All endpoints resolved with acceptable confidence._")

    return "\n".join(lines) + "\n"


def generate_flow_documentation(trace: FlowTrace) -> str:
    lines = [
        f"# Flow: {trace.endpoint}",
        "",
        f"**Confidence:** {trace.confidence:.0%}",
        "",
        "## Request → Database Chain",
        "",
    ]
    for idx, step in enumerate(trace.steps, start=1):
        loc = f" (`{step.file}:{step.line}`)" if step.file and step.line else ""
        op = f" — {step.operation}" if step.operation else ""
        lines.append(f"{idx}. **{step.layer}** → `{step.symbol}`{loc}{op}")

    lines.extend(["", "## Sequence Diagram", "", "```mermaid"])
    lines.append((trace.sequence_diagram or "").strip())
    lines.extend(["```", ""])

    if trace.uncertainties:
        lines.extend(["## Uncertainties", ""])
        for item in trace.uncertainties:
            lines.append(f"- {item}")

    return "\n".join(lines) + "\n"


def write_flow_reports(result: AnalysisResult, output_dir: Path) -> List[str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written: List[str] = []

    flow_path = output_dir / "flow-tracing-report.md"
    flow_path.write_text(generate_flow_trace_report(result.flow_traces), encoding="utf-8")
    written.append(str(flow_path))

    uncertainty_path = output_dir / "uncertainty-report.md"
    uncertainty_path.write_text(generate_uncertainty_report(result.flow_traces), encoding="utf-8")
    written.append(str(uncertainty_path))

    seq_dir = output_dir / "sequence-diagrams"
    seq_dir.mkdir(exist_ok=True)
    docs_dir = output_dir / "flow-docs"
    docs_dir.mkdir(exist_ok=True)

    for trace in result.flow_traces:
        slug = re.sub(r"[^a-zA-Z0-9]+", "-", trace.endpoint).strip("-").lower()
        if trace.sequence_diagram:
            seq_file = seq_dir / f"{slug}.mmd"
            seq_file.write_text(trace.sequence_diagram, encoding="utf-8")
            written.append(str(seq_file))
        doc_file = docs_dir / f"{slug}.md"
        doc_file.write_text(generate_flow_documentation(trace), encoding="utf-8")
        written.append(str(doc_file))

    return written
