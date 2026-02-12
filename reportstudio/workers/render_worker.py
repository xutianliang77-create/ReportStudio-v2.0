"""Render worker for queued render jobs."""

from __future__ import annotations

from pathlib import Path

from reportstudio.core.render.job_service import (
    append_audit_log,
    get_job,
    update_job,
)
from reportstudio.p1.export_artifact import export_report
from reportstudio.scripts.report.create import run_pipeline
from reportstudio.workers.queue import dequeue_local_render_job


def process_render_job(render_id: str) -> dict:
    job = get_job(render_id)
    update_job(render_id, status="running")
    append_audit_log(render_id, "running", {"input_path": job.input_path, "fmt": job.fmt})

    try:
        # Run pipeline once and reuse intermediate result for export (no recompute in export script)
        result = run_pipeline(Path(job.input_path), metric_field=job.metric_field, dimension_field=job.dimension_field)
        artifact = export_report(
            {
                "trace_id": result["trace_id"],
                "metrics": result["metrics"],
                "topn": result["topn"],
                "delivery": result["delivery"],
            },
            out_dir=Path("reportstudio/data/artifacts"),
            report_name="render",
            fmt=job.fmt,
        )
        update_job(render_id, status="succeeded", artifact_file=artifact["file"], sha256=artifact["sha256"])
        append_audit_log(render_id, "succeeded", {"artifact_file": artifact["file"], "sha256": artifact["sha256"]})
        return {"render_id": render_id, "status": "succeeded", "artifact": artifact}
    except Exception as exc:  # keep worker resilient
        update_job(render_id, status="failed", error_code="RENDER_FAILED", error_message=str(exc))
        append_audit_log(
            render_id,
            "failed",
            {"error_code": "RENDER_FAILED", "error_message": str(exc)},
        )
        return {"render_id": render_id, "status": "failed", "error_code": "RENDER_FAILED", "error_message": str(exc)}


def process_next_local_job() -> dict | None:
    render_id = dequeue_local_render_job()
    if not render_id:
        return None
    return process_render_job(render_id)
