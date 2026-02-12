"""Minimal API simulator for P1 API endpoints with deterministic command parsing.

Endpoints (simulated by CLI):
- reports.create
- renders.create
- artifacts.get
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[3]))

from reportstudio.p1.api import create_report, render_report, get_artifact
from reportstudio.p1.command_parser import parse_command


def _resolve_endpoint(endpoint: str | None, command: str | None) -> str:
    if endpoint:
        return endpoint
    if command:
        return parse_command(command).endpoint
    raise SystemExit("either positional endpoint or --command must be provided")


def main() -> int:
    parser = argparse.ArgumentParser(description="Simulate ReportStudio P1 API endpoints")
    parser.add_argument("endpoint", nargs="?", choices=["reports.create", "renders.create", "artifacts.get"])
    parser.add_argument("--command", help="deterministic command, e.g. 'create report' or 'render pdf'")
    parser.add_argument("--input", help="source CSV/JSON input path")
    parser.add_argument("--file", help="artifact file path for artifacts.get")
    parser.add_argument("--format", default="json", choices=["json", "xlsx", "pdf"])
    parser.add_argument("--metric-field", default="amount")
    parser.add_argument("--dimension-field", default="region")
    args = parser.parse_args()

    endpoint = _resolve_endpoint(args.endpoint, args.command)

    if endpoint == "reports.create":
        if not args.input:
            raise SystemExit("--input is required")
        response = create_report(Path(args.input), metric_field=args.metric_field, dimension_field=args.dimension_field)
    elif endpoint == "renders.create":
        if not args.input:
            raise SystemExit("--input is required")
        response = render_report(
            Path(args.input), fmt=args.format, metric_field=args.metric_field, dimension_field=args.dimension_field
        )
    else:
        if not args.file:
            raise SystemExit("--file is required")
        response = get_artifact(Path(args.file))

    print(json.dumps(response.__dict__, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
