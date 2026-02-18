"""/renders route handler (P2-001 async queue model)."""

from __future__ import annotations

from pathlib import Path

from reportstudio.api.deps import acl_error_response, enforce_acl
from reportstudio.core.export.artifact_service import ExportDocxError, export_docx_artifact
from reportstudio.core.render.job_service import (
    cancel_job,
    create_job,
    get_job,
    job_to_dict,
    retry_failed_job,
)
from reportstudio.core.security.acl import ACLDeniedError
from reportstudio.workers.queue import enqueue_render_job, queue_backend


SUPPORTED_QUEUE_EXPORT_FORMATS = frozenset({"pdf", "xlsx", "json"})


def _normalize_export_format(fmt: object | None) -> str:
    if not isinstance(fmt, str):
        return ""
    return fmt.strip().lower()


def _resolve_render_request_id(render_request_id: str | None, headers: dict[str, str] | None) -> str | None:
    if render_request_id:
        return render_request_id
    if not headers:
        return None
    return headers.get("render_request_id") or headers.get("x-render-request-id")


def create_render(
    input_path: str,
    fmt: str | None = "pdf",
    metric_field: str = "amount",
    dimension_field: str = "region",
    workspace_id: str = "default-workspace",
    report_id: str = "default-report",
    render_request_id: str | None = None,
    headers: dict[str, str] | None = None,
    principal_id: str = "owner",
) -> dict:
    fmt = _normalize_export_format(fmt)
    if fmt not in SUPPORTED_QUEUE_EXPORT_FORMATS:
        return {
            "code": 400,
            "message": "unsupported format",
            "error_code": "E3003",
            "data": {},
        }
    try:
        enforce_acl(
            resource_type="report",
            resource_id=report_id,
            principal_id=principal_id,
            actions_any={"view", "render"},
        )
    except ACLDeniedError as exc:
        return acl_error_response(exc)

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


def export_render_docx(
    render_id: str,
    *,
    intermediate_dir: str,
    principal_id: str = "owner",
    title: str = "Report",
) -> dict:
    job = get_job(render_id)
    try:
        enforce_acl(
            resource_type="report",
            resource_id=job.report_id,
            principal_id=principal_id,
            actions_any={"export"},
        )
    except ACLDeniedError as exc:
        return acl_error_response(exc)

    try:
        artifact = export_docx_artifact(
            render_id=render_id,
            intermediate_dir=Path(intermediate_dir),
            out_dir=Path("reportstudio/data/artifacts"),
            title=title,
        )
        return {
            "code": 200,
            "message": "success",
            "data": {
                "artifact": artifact,
            },
        }
    except ExportDocxError as exc:
        return {
            "code": 400,
            "message": str(exc),
            "error_code": "E3003",
            "data": {
                "render_id": render_id,
            },
        }


def cancel_render(render_id: str, *, principal_id: str = "owner") -> dict:
    base_job = get_job(render_id)
    try:
        enforce_acl(
            resource_type="report",
            resource_id=base_job.report_id,
            principal_id=principal_id,
            actions_any={"render", "manage"},
        )
    except ACLDeniedError as exc:
        return acl_error_response(exc)

    job = cancel_job(render_id)
    return {
        "code": 200,
        "message": "success",
        "data": {
            "render": {
                "render_id": job.render_id,
                "status": job.status,
            }
        },
    }


def retry_render(
    render_id: str,
    *,
    input_path: str | None = None,
    fmt: str | None = None,
    metric_field: str | None = None,
    dimension_field: str | None = None,
    principal_id: str = "owner",
) -> dict:
    base_job = get_job(render_id)
    try:
        enforce_acl(
            resource_type="report",
            resource_id=base_job.report_id,
            principal_id=principal_id,
            actions_any={"render", "manage"},
        )
    except ACLDeniedError as exc:
        return acl_error_response(exc)

    retry_job = retry_failed_job(
        render_id,
        input_path=input_path,
        fmt=fmt,
        metric_field=metric_field,
        dimension_field=dimension_field,
    )
    enqueue_render_job(retry_job.render_id)
    return {
        "code": 200,
        "message": "success",
        "data": {
            "render": {
                "render_id": retry_job.render_id,
                "status": retry_job.status,
                "format": retry_job.fmt,
                "backend": queue_backend(),
                "source_render_id": retry_job.source_render_id,
                "attempt": retry_job.attempt,
            }
        },
    }


def get_render(render_id: str, *, principal_id: str = "owner") -> dict:
    base_job = get_job(render_id)
    try:
        enforce_acl(
            resource_type="report",
            resource_id=base_job.report_id,
            principal_id=principal_id,
            actions_any={"view", "render", "manage"},
        )
    except ACLDeniedError as exc:
        return acl_error_response(exc)

    job = get_job(render_id)
    return {
        "code": 200,
        "message": "success",
        "data": {
            "render": job_to_dict(job),
        },
    }
