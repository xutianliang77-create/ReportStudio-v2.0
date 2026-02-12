"""/renders route handler (P2-001 async queue model)."""

from __future__ import annotations

from reportstudio.core.render.job_service import create_job, get_job, job_to_dict
from reportstudio.workers.queue import enqueue_render_job, queue_backend


def _resolve_render_request_id(render_request_id: str | None, headers: dict[str, str] | None) -> str | None:
    if render_request_id:
        return render_request_id
    if not headers:
        return None
    return headers.get("render_request_id") or headers.get("x-render-request-id")


def create_render(
    input_path: str,
    fmt: str = "pdf",
    metric_field: str = "amount",
    dimension_field: str = "region",
    workspace_id: str = "default-workspace",
    report_id: str = "default-report",
    render_request_id: str | None = None,
    headers: dict[str, str] | None = None,
) -> dict:
    request_id = _resolve_render_request_id(render_request_id, headers)
    job, created = create_job(
        input_path=input_path,
        fmt=fmt,
        metric_field=metric_field,
        dimension_field=dimension_field,
        workspace_id=workspace_id,
        report_id=report_id,
        render_request_id=request_id,
    )
    if created:
        enqueue_render_job(job.render_id)

    # P1 response compatibility: keep code/message/data envelope, add render_id/status/backend
    return {
        "code": 200,
        "message": "success",
        "data": {
            "render": {
                "render_id": job.render_id,
                "status": job.status,
                "format": job.fmt,
                "backend": queue_backend(),
            }
        },
    }


def get_render(render_id: str) -> dict:
    job = get_job(render_id)
    return {
        "code": 200,
        "message": "success",
        "data": {
            "render": job_to_dict(job),
        },
    }
