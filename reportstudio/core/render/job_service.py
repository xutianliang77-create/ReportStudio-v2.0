"""Render job service for async queue flow with progress tracking."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from threading import Lock
from typing import Any
import uuid


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_render_id() -> str:
    return f"rj_{uuid.uuid4().hex[:12]}"


@dataclass
class RenderJob:
    render_id: str
    status: str
    input_path: str
    fmt: str
    metric_field: str
    dimension_field: str
    workspace_id: str
    report_id: str
    render_request_id: str | None = None
    source_render_id: str | None = None
    attempt: int = 1
    # P2-002 progress tracking
    progress: int = 0
    stage: str = "queued"
    artifact_file: str | None = None
    sha256: str | None = None
    error_code: str | None = None
    error_message: str | None = None
    created_at: str = ""
    updated_at: str = ""


_JOBS: dict[str, RenderJob] = {}
_AUDIT_LOGS: list[dict[str, Any]] = []
_IDEMPOTENCY_INDEX: dict[tuple[str, str, str], str] = {}
_LOCK = Lock()


def _build_job(
    *,
    input_path: str,
    fmt: str,
    metric_field: str,
    dimension_field: str,
    workspace_id: str,
    report_id: str,
    render_request_id: str | None,
    source_render_id: str | None,
    attempt: int,
) -> RenderJob:
    render_id = _new_render_id()
    ts = _now()
    job = RenderJob(
        render_id=render_id,
        status="queued",
        input_path=input_path,
        fmt=fmt,
        metric_field=metric_field,
        dimension_field=dimension_field,
        workspace_id=workspace_id,
        report_id=report_id,
        render_request_id=render_request_id,
        source_render_id=source_render_id,
        attempt=attempt,
        progress=0,
        stage="queued",
        created_at=ts,
        updated_at=ts,
    )
    _JOBS[render_id] = job
    return job


def create_job(
    input_path: str,
    fmt: str,
    metric_field: str,
    dimension_field: str,
    workspace_id: str = "default-workspace",
    report_id: str = "default-report",
    render_request_id: str | None = None,
) -> tuple[RenderJob, bool]:
    """Create a render job.

    Returns (job, created) where created=False means an idempotent hit.
    """

    if render_request_id:
        key = (workspace_id, report_id, render_request_id)
        with _LOCK:
            hit_id = _IDEMPOTENCY_INDEX.get(key)
            if hit_id is not None:
                hit = _JOBS[hit_id]
                append_audit_log(
                    hit.render_id,
                    "render.idempotent_hit",
                    {
                        "workspace_id": workspace_id,
                        "report_id": report_id,
                        "render_request_id": render_request_id,
                    },
                )
                return hit, False

            job = _build_job(
                input_path=input_path,
                fmt=fmt,
                metric_field=metric_field,
                dimension_field=dimension_field,
                workspace_id=workspace_id,
                report_id=report_id,
                render_request_id=render_request_id,
                source_render_id=None,
                attempt=1,
            )
            _IDEMPOTENCY_INDEX[key] = job.render_id
    else:
        job = _build_job(
            input_path=input_path,
            fmt=fmt,
            metric_field=metric_field,
            dimension_field=dimension_field,
            workspace_id=workspace_id,
            report_id=report_id,
            render_request_id=None,
            source_render_id=None,
            attempt=1,
        )

    append_audit_log(
        job.render_id,
        "queued",
        {
            "fmt": fmt,
            "input_path": input_path,
            "progress": 0,
            "stage": "queued",
            "workspace_id": workspace_id,
            "report_id": report_id,
            "render_request_id": render_request_id,
            "source_render_id": job.source_render_id,
            "attempt": job.attempt,
        },
    )
    return job, True


def cancel_job(render_id: str) -> RenderJob:
    job = get_job(render_id)
    if job.status != "queued":
        raise ValueError("only queued job can be canceled")
    canceled = update_job(render_id, status="canceled", stage="canceled")
    append_audit_log(canceled.render_id, "render.cancel", {"status": canceled.status, "stage": canceled.stage})
    return canceled


def retry_failed_job(
    render_id: str,
    *,
    input_path: str | None = None,
    fmt: str | None = None,
    metric_field: str | None = None,
    dimension_field: str | None = None,
) -> RenderJob:
    source = get_job(render_id)
    if source.status != "failed":
        raise ValueError("only failed job can be retried")

    retry_job = _build_job(
        input_path=input_path or source.input_path,
        fmt=fmt or source.fmt,
        metric_field=metric_field or source.metric_field,
        dimension_field=dimension_field or source.dimension_field,
        workspace_id=source.workspace_id,
        report_id=source.report_id,
        render_request_id=None,
        source_render_id=source.render_id,
        attempt=source.attempt + 1,
    )
    append_audit_log(
        retry_job.render_id,
        "render.retry",
        {
            "source_render_id": source.render_id,
            "attempt": retry_job.attempt,
        },
    )
    append_audit_log(
        retry_job.render_id,
        "queued",
        {
            "fmt": retry_job.fmt,
            "input_path": retry_job.input_path,
            "progress": 0,
            "stage": "queued",
            "workspace_id": retry_job.workspace_id,
            "report_id": retry_job.report_id,
            "render_request_id": retry_job.render_request_id,
            "source_render_id": retry_job.source_render_id,
            "attempt": retry_job.attempt,
        },
    )
    return retry_job


def get_job(render_id: str) -> RenderJob:
    return _JOBS[render_id]


def update_job(render_id: str, **patch: Any) -> RenderJob:
    job = get_job(render_id)

    # enforce monotonic progress [0, 100]
    if "progress" in patch:
        next_progress = int(patch["progress"])
        if next_progress < job.progress:
            next_progress = job.progress
        if next_progress < 0:
            next_progress = 0
        if next_progress > 100:
            next_progress = 100
        patch["progress"] = next_progress

    for k, v in patch.items():
        setattr(job, k, v)
    job.updated_at = _now()
    return job


def append_audit_log(render_id: str, action: str, detail: dict[str, Any]) -> None:
    _AUDIT_LOGS.append(
        {
            "render_id": render_id,
            "action": action,
            "detail": detail,
            "created_at": _now(),
        }
    )


def list_audit_logs(render_id: str | None = None) -> list[dict[str, Any]]:
    if render_id is None:
        return list(_AUDIT_LOGS)
    return [x for x in _AUDIT_LOGS if x["render_id"] == render_id]


def job_to_dict(job: RenderJob) -> dict[str, Any]:
    return asdict(job)
