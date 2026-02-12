"""P1 E2E pipeline entrypoint for report.create."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[3]))

from reportstudio.p1.infrastructure import AppConfig, RunContext, JsonLogger, ensure_workspace
from reportstudio.p1.ingest import ingest_file
from reportstudio.p1.metrics_analysis import compute_metrics, topn
from reportstudio.p1.charts_layout import recommend_chart, build_layout
from reportstudio.p1.export_artifact import export_report
from reportstudio.p1.dispatch import dispatch


def run_pipeline(input_path: Path, metric_field: str, dimension_field: str) -> dict:
    ctx = RunContext()
    logger = JsonLogger(ctx.trace_id)
    config = AppConfig()
    workspace = ensure_workspace(config)

    dataset = ingest_file(input_path)
    metrics = compute_metrics(dataset.rows, metric_field=metric_field)
    ranking = topn(dataset.rows, dimension=dimension_field, metric_field=metric_field, n=10)

    chart = recommend_chart(has_time_dimension=True, has_category_dimension=True)
    layout = build_layout(has_time_dimension=True, include_insight=True)

    snapshot = {
        "trace_id": ctx.trace_id,
        "input": str(input_path),
        "schema": dataset.schema,
        "quality": dataset.quality,
        "metrics": metrics,
        "topn": ranking,
        "chart": chart,
        "layout": layout,
        "events": [
            logger.event("ingest.completed", {"rows": len(dataset.rows)}),
            logger.event("metrics.completed", {"metric_field": metric_field}),
        ],
    }

    artifact = export_report(snapshot, out_dir=workspace / "artifacts", report_name="report")
    delivery = dispatch({"file": artifact["file"], "sha256": artifact["sha256"]})

    result = {
        "trace_id": ctx.trace_id,
        "artifact": artifact,
        "delivery": delivery,
        "metrics": metrics,
        "topn": ranking,
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run ReportStudio P1 report.create pipeline")
    parser.add_argument("--input", required=True, help="CSV/JSON input file")
    parser.add_argument("--metric-field", default="amount")
    parser.add_argument("--dimension-field", default="region")
    args = parser.parse_args()

    result = run_pipeline(Path(args.input), metric_field=args.metric_field, dimension_field=args.dimension_field)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
