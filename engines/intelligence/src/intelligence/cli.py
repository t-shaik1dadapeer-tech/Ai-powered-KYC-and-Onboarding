from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from intelligence.analyzer import analyze_repository


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze a repository and generate intelligence reports"
    )
    parser.add_argument("path", help="Path to repository root")
    parser.add_argument(
        "-o",
        "--output",
        default="reports",
        help="Output directory for markdown reports (default: reports)",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON summary to stdout")
    args = parser.parse_args()

    repo_path = Path(args.path)
    if not repo_path.is_dir():
        print(f"Error: path not found: {repo_path}", file=sys.stderr)
        sys.exit(1)

    result = analyze_repository(repo_path, output_dir=args.output)

    summary = {
        "repository": result.repository,
        "framework": result.framework,
        "confidence": result.confidence,
        "services": len(result.inventories.services),
        "controllers": len(result.inventories.controllers),
        "apis": len(result.inventories.apis),
        "models": len(result.inventories.models),
        "tests": len(result.inventories.tests),
        "dependencies": len(result.inventories.dependencies),
        "flow_traces": len(result.flow_traces),
        "output_dir": str(Path(args.output).resolve()),
    }

    print(f"Framework: {result.framework} ({result.confidence:.0%})")
    print(f"APIs: {summary['apis']} | Models: {summary['models']} | Tests: {summary['tests']}")
    print(f"Reports written to: {summary['output_dir']}")

    if args.json:
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
