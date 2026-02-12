"""Export entrypoint for ReportStudio scaffold (JSON/XLSX/PDF)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[3]))

from reportstudio.scripts.report.create import run_pipeline
from reportstudio.p1.export_artifact import export_report


def export_from_input(input_path: Path, metric_field: str, dimension_field: str, fmt: str = "json") -> dict:
    """Create report artifact and return downloadable metadata."""
    result = run_pipeline(input_path, metric_field=metric_field, dimension_field=dimension_field)
    # re-export to selected format
    artifact = export_report(
        {
            "trace_id": result["trace_id"],
            "metrics": result["metrics"],
            "topn": result["topn"],
            "delivery": result["delivery"],
        },
        out_dir=Path("reportstudio/data/artifacts"),
        report_name="report",
        fmt=fmt,
    )

    return {
        "status": "exported",
        "artifact_file": artifact["file"],
        "download_path": artifact["file"],
        "sha256": artifact["sha256"],
        "format": artifact["format"],
        "metrics": result["metrics"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export ReportStudio artifact from source data")
    parser.add_argument("--input", required=True, help="CSV/JSON input file")
    parser.add_argument("--metric-field", default="amount")
    parser.add_argument("--dimension-field", default="region")
    parser.add_argument("--format", default="json", choices=["json", "xlsx", "pdf"])
    args = parser.parse_args()

    payload = export_from_input(
        Path(args.input),
        metric_field=args.metric_field,
        dimension_field=args.dimension_field,
        fmt=args.format,
    )
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
