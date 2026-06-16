#!/usr/bin/env python3
"""Generate dashboard evidence SVG from Prometheus text metrics."""

from __future__ import annotations

import re
import sys
from pathlib import Path

METRIC_PATTERN = re.compile(
    r"^(?P<name>[a-zA-Z_:][a-zA-Z0-9_:]*)(?:\{(?P<labels>[^}]*)\})?\s+(?P<value>[-+eE0-9.]+)$"
)


def parse_metrics(text: str) -> dict[str, float]:
    totals: dict[str, float] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = METRIC_PATTERN.match(line)
        if not match:
            continue
        name = match.group("name")
        labels = match.group("labels") or ""
        value = float(match.group("value"))
        key = f"{name}{{{labels}}}" if labels else name
        if name.endswith("_bucket") or name.endswith("_sum") or name.endswith("_count"):
            continue
        totals[key] = value
    return totals


def bar_chart_svg(
    title: str,
    items: list[tuple[str, float]],
    x: int,
    y: int,
    width: int,
    height: int,
) -> str:
    if not items:
        items = [("(no data)", 0.0)]
    max_val = max(v for _, v in items) or 1.0
    bar_h = max(18, (height - 40) // len(items))
    parts = [
        f'<g transform="translate({x},{y})">',
        f'  <rect width="{width}" height="{height}" fill="#1f1f23" stroke="#444" rx="4"/>',
        f'  <text x="12" y="22" fill="#ddd" font-family="sans-serif" font-size="14" font-weight="bold">{title}</text>',
    ]
    for i, (label, val) in enumerate(items):
        by = 36 + i * bar_h
        bw = int((width - 140) * (val / max_val)) if max_val else 0
        parts.append(
            f'  <text x="12" y="{by + 14}" fill="#aaa" font-family="monospace" font-size="11">{label[:28]}</text>'
        )
        parts.append(
            f'  <rect x="130" y="{by}" width="{bw}" height="{bar_h - 4}" fill="#5794f2" rx="2"/>'
        )
        parts.append(
            f'  <text x="{130 + bw + 6}" y="{by + 14}" fill="#ccc" font-family="monospace" font-size="11">{val:g}</text>'
        )
    parts.append("</g>")
    return "\n".join(parts)


def build_dashboard_svg(metrics: dict[str, float]) -> str:
    kyc = [(k, v) for k, v in metrics.items() if k.startswith("kyc_submissions_total")]
    risk = [(k, v) for k, v in metrics.items() if k.startswith("risk_assessments_total")]
    verify = [
        (k, v)
        for k, v in metrics.items()
        if k.startswith("pan_verifications_total") or k.startswith("bank_verifications_total")
    ]
    customers = [(k, v) for k, v in metrics.items() if k.startswith("customers_created_total")]
    http = sum(v for k, v in metrics.items() if k.startswith("http_requests_total"))

    panels = [
        bar_chart_svg("KYC Submissions", kyc, 20, 60, 460, 120),
        bar_chart_svg("Risk Assessments", risk, 500, 60, 460, 120),
        bar_chart_svg("Verifications", verify, 20, 200, 460, 120),
        bar_chart_svg("Customers Created", customers, 500, 200, 460, 120),
    ]

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="980" height="340" viewBox="0 0 980 340">
  <rect width="100%" height="100%" fill="#111217"/>
  <text x="20" y="36" fill="#fff" font-family="sans-serif" font-size="20" font-weight="bold">KYC Platform — Metrics Snapshot</text>
  <text x="20" y="54" fill="#888" font-family="sans-serif" font-size="12">Generated from /metrics (Grafana dashboard: infra/grafana/dashboards/kyc-platform.json)</text>
  <text x="780" y="36" fill="#73bf69" font-family="monospace" font-size="13">http_requests_total ≈ {http:g}</text>
{chr(10).join(panels)}
</svg>
"""


def main() -> int:
    metrics_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("evidence/screenshots")

    if metrics_path is None or not metrics_path.is_file():
        print("Usage: generate-dashboard-evidence.py <metrics.txt> [out_dir]", file=sys.stderr)
        return 1

    text = metrics_path.read_text()
    metrics = parse_metrics(text)
    svg = build_dashboard_svg(metrics)

    out_dir.mkdir(parents=True, exist_ok=True)
    svg_path = out_dir / "kyc-platform-dashboard.svg"
    svg_path.write_text(svg)
    print(str(svg_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
