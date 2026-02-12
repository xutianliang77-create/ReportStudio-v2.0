"""/preview-sessions route handlers."""

from __future__ import annotations

from dataclasses import dataclass

from reportstudio.core.preview.service import (
    create_preview_session,
    get_preview_session,
    mark_preview_render,
    preview_session_to_dict,
)
from reportstudio.core.render.job_service import create_job
from reportstudio.workers.queue import enqueue_render_job, queue_backend


@dataclass(frozen=True)
class CreatePreviewSessionDTO:
    report_id: str
    base_version_id: str | None = None


def create_preview_session_route(payload: CreatePreviewSessionDTO) -> dict:
    session = create_preview_session(report_id=payload.report_id, base_version_id=payload.base_version_id)
    return {
        "code": 200,
        "message": "success",
        "data": {
            "preview_session": preview_session_to_dict(session),
        },
    }


def get_preview_session_route(preview_session_id: str) -> dict:
    session = get_preview_session(preview_session_id)
    return {
        "code": 200,
        "message": "success",
        "data": {
            "preview_session": preview_session_to_dict(session),
        },
    }


def render_preview_session_route(preview_session_id: str) -> dict:
    session = get_preview_session(preview_session_id)
    spec = session.working_spec_json

    # Reuse existing render queue + worker pipeline/export logic.
    job, _ = create_job(
        input_path=str(spec.get("input_path", "tests/fixtures/sales.csv")),
        fmt=str(spec.get("format", "pdf")),
        metric_field=str(spec.get("metric_field", "amount")),
        dimension_field=str(spec.get("dimension_field", "region")),
    )
    enqueue_render_job(job.render_id)
    mark_preview_render(preview_session_id, job.render_id)

    return {
        "code": 200,
        "message": "success",
        "data": {
            "render": {
                "preview_session_id": preview_session_id,
                "render_id": job.render_id,
                "status": job.status,
                "backend": queue_backend(),
            }
        },
    }
