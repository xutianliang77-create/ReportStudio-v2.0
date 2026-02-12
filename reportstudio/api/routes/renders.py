"""/renders route handler (P2-001 async queue model)."""

from __future__ import annotations

from reportstudio.core.render.job_service import create_job, get_job, job_to_dict
from reportstudio.workers.queue import enqueue_render_job, queue_backend


def create_render(input_path: str, fmt: str = "pdf", metric_field: str = "amount", dimension_field: str = "region") -> dict:
    job = create_job(input_path=input_path, fmt=fmt, metric_field=metric_field, dimension_field=dimension_field)
    enqueue_render_job(job.render_id)

    # P1 response compatibility: keep code/message/data envelope, add render_id/status/backend
    return {
        "code": 200,
        "message": "success",
        "data": {
            "render": {
                "render_id": job.render_id,
                "status": "queued",
                "format": fmt,
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
