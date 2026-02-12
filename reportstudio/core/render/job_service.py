"""Render job service for P2-001 async queue flow."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
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
    artifact_file: str | None = None
    sha256: str | None = None
    error_code: str | None = None
    error_message: str | None = None
    created_at: str = ""
    updated_at: str = ""


_JOBS: dict[str, RenderJob] = {}
_AUDIT_LOGS: list[dict[str, Any]] = []


def create_job(input_path: str, fmt: str, metric_field: str, dimension_field: str) -> RenderJob:
    render_id = f"rj_{uuid.uuid4().hex[:12]}"
    ts = _now()
    job = RenderJob(
        render_id=render_id,
        status="queued",
        input_path=input_path,
        fmt=fmt,
        metric_field=metric_field,
        dimension_field=dimension_field,
        created_at=ts,
        updated_at=ts,
    )
    _JOBS[render_id] = job
    append_audit_log(render_id, "queued", {"fmt": fmt, "input_path": input_path})
    return job


def get_job(render_id: str) -> RenderJob:
    return _JOBS[render_id]


def update_job(render_id: str, **patch: Any) -> RenderJob:
    job = get_job(render_id)
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
