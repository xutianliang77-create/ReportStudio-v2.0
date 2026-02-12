"""P1-601~P1-603 API façade for reports/renders/artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from reportstudio.scripts.report.create import run_pipeline
from reportstudio.scripts.export.export import export_from_input
from reportstudio.scripts.export.download import build_download_info


@dataclass(frozen=True)
class ApiResponse:
    code: int
    message: str
    data: dict[str, Any]


def create_report(input_path: Path, metric_field: str = "amount", dimension_field: str = "region") -> ApiResponse:
    result = run_pipeline(input_path=input_path, metric_field=metric_field, dimension_field=dimension_field)
    return ApiResponse(
        code=200,
        message="success",
        data={
            "report_id": result["trace_id"],
            "trace_id": result["trace_id"],
            "metrics": result["metrics"],
            "topn": result["topn"],
            "artifact": result["artifact"],
        },
    )


def render_report(input_path: Path, fmt: str = "json", metric_field: str = "amount", dimension_field: str = "region") -> ApiResponse:
    export_result = export_from_input(
        input_path=input_path,
        metric_field=metric_field,
        dimension_field=dimension_field,
        fmt=fmt,
    )
    return ApiResponse(code=200, message="success", data={"render": export_result})


def get_artifact(file_path: Path) -> ApiResponse:
    info = build_download_info(file_path)
    return ApiResponse(code=200, message="success", data={"artifact": info})
