"""Render job service for async queue flow with progress tracking."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from threading import Lock
from typing import Any
import uuid


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


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

            render_id = f"rj_{uuid.uuid4().hex[:12]}"
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
                progress=0,
                stage="queued",
                created_at=ts,
                updated_at=ts,
            )
            _JOBS[render_id] = job
            _IDEMPOTENCY_INDEX[key] = render_id

    else:
        render_id = f"rj_{uuid.uuid4().hex[:12]}"
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
            render_request_id=None,
            progress=0,
            stage="queued",
            created_at=ts,
            updated_at=ts,
        )
        _JOBS[render_id] = job

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
        },
    )
    return job, True


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
