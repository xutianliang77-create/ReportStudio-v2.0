"""Render worker for queued render jobs with progress/stage tracking."""

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


STAGE_COMPUTE = "compute"
STAGE_PLOT = "plot"
STAGE_EXPORT = "export"
STAGE_UPLOAD = "upload"


def _set_progress(render_id: str, status: str, stage: str, progress: int) -> None:
    update_job(render_id, status=status, stage=stage, progress=progress)
    append_audit_log(render_id, "progress", {"status": status, "stage": stage, "progress": progress})


def process_render_job(render_id: str) -> dict:
    job = get_job(render_id)
    _set_progress(render_id, status="running", stage=STAGE_COMPUTE, progress=10)

    try:
        # compute: run full pipeline once
        result = run_pipeline(Path(job.input_path), metric_field=job.metric_field, dimension_field=job.dimension_field)

        # plot: in this scaffold, chart/layout are included in pipeline output
        _set_progress(render_id, status="running", stage=STAGE_PLOT, progress=40)

        # export: reuse intermediate result, do not recalculate pipeline in export layer
        _set_progress(render_id, status="running", stage=STAGE_EXPORT, progress=70)
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

        # upload: in scaffold treated as artifact registration/delivery writeback
        _set_progress(render_id, status="running", stage=STAGE_UPLOAD, progress=90)

        update_job(
            render_id,
            status="succeeded",
            progress=100,
            stage=STAGE_UPLOAD,
            artifact_file=artifact["file"],
            sha256=artifact["sha256"],
        )
        append_audit_log(
            render_id,
            "succeeded",
            {
                "artifact_file": artifact["file"],
                "sha256": artifact["sha256"],
                "progress": 100,
                "stage": STAGE_UPLOAD,
            },
        )
        return {"render_id": render_id, "status": "succeeded", "artifact": artifact}
    except Exception as exc:  # keep worker resilient
        failed = update_job(
            render_id,
            status="failed",
            error_code="RENDER_FAILED",
            error_message=str(exc),
            # progress remains monotonic and frozen when failed
        )
        append_audit_log(
            render_id,
            "failed",
            {
                "error_code": "RENDER_FAILED",
                "error_message": str(exc),
                "progress": failed.progress,
                "stage": failed.stage,
            },
        )
        return {
            "render_id": render_id,
            "status": "failed",
            "error_code": "RENDER_FAILED",
            "error_message": str(exc),
        }


def process_next_local_job() -> dict | None:
    render_id = dequeue_local_render_job()
    if not render_id:
        return None
    return process_render_job(render_id)
