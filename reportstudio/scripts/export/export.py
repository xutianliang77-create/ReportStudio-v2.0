"""Export entrypoint for ReportStudio scaffold (design-phase downloadable artifact)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[3]))

from reportstudio.scripts.report.create import run_pipeline


def export_from_input(input_path: Path, metric_field: str, dimension_field: str) -> dict:
    """Create report artifact and return export metadata."""
    result = run_pipeline(input_path, metric_field=metric_field, dimension_field=dimension_field)
    artifact_file = Path(result["artifact"]["file"])
    return {
        "status": "exported",
        "artifact_file": str(artifact_file),
        "download_path": str(artifact_file),
        "sha256": result["artifact"]["sha256"],
        "metrics": result["metrics"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export ReportStudio artifact from source data")
    parser.add_argument("--input", required=True, help="CSV/JSON input file")
    parser.add_argument("--metric-field", default="amount")
    parser.add_argument("--dimension-field", default="region")
    args = parser.parse_args()

    payload = export_from_input(Path(args.input), metric_field=args.metric_field, dimension_field=args.dimension_field)
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
