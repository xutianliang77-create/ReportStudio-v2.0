"""Preview session domain service."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
import uuid

from reportstudio.core.preview.patch import apply_patches
from reportstudio.core.version.service import get_report_version, list_report_versions


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class PreviewSession:
    preview_session_id: str
    report_id: str
    base_spec_version: str | None
    working_spec_json: dict[str, Any]
    patch_history_json: list[dict[str, Any]]
    status: str
    updated_at: str


_PREVIEW_SESSIONS: dict[str, PreviewSession] = {}
_AUDIT_LOGS: list[dict[str, Any]] = []


def _append_audit_log(action: str, detail: dict[str, Any]) -> None:
    _AUDIT_LOGS.append({"action": action, "detail": detail, "created_at": _now()})


def list_audit_logs(action: str | None = None) -> list[dict[str, Any]]:
    if action is None:
        return list(_AUDIT_LOGS)
    return [x for x in _AUDIT_LOGS if x["action"] == action]


def _resolve_base_spec(report_id: str, base_version_id: str | None) -> tuple[str | None, dict[str, Any]]:
    if base_version_id:
        version = get_report_version(report_id, base_version_id)
        return base_version_id, dict(version.spec_json)

    versions = list_report_versions(report_id)
    if versions:
        latest = versions[-1]
        return latest.version_id, dict(latest.spec_json)
    return None, {}


def create_preview_session(*, report_id: str, base_version_id: str | None = None) -> PreviewSession:
    resolved_version_id, spec = _resolve_base_spec(report_id, base_version_id)
    session = PreviewSession(
        preview_session_id=f"ps_{uuid.uuid4().hex[:12]}",
        report_id=report_id,
        base_spec_version=resolved_version_id,
        working_spec_json=spec,
        patch_history_json=[],
        status="active",
        updated_at=_now(),
    )
    _PREVIEW_SESSIONS[session.preview_session_id] = session
    _append_audit_log(
        "preview.session.create",
        {
            "preview_session_id": session.preview_session_id,
            "report_id": report_id,
            "base_spec_version": resolved_version_id,
        },
    )
    return session


def get_preview_session(preview_session_id: str) -> PreviewSession:
    return _PREVIEW_SESSIONS[preview_session_id]


def mark_preview_render(preview_session_id: str, render_id: str) -> PreviewSession:
    session = get_preview_session(preview_session_id)
    session.status = "rendering"
    session.updated_at = _now()
    _append_audit_log(
        "preview.render",
        {
            "preview_session_id": preview_session_id,
            "report_id": session.report_id,
            "render_id": render_id,
        },
    )
    return session


def apply_preview_patches(preview_session_id: str, patches: list[dict[str, Any]]) -> PreviewSession:
    session = get_preview_session(preview_session_id)
    next_spec = apply_patches(session.working_spec_json, patches)
    session.working_spec_json = next_spec
    session.patch_history_json.extend(patches)
    session.status = "active"
    session.updated_at = _now()
    _append_audit_log(
        "preview.patch",
        {
            "preview_session_id": preview_session_id,
            "report_id": session.report_id,
            "patch_count": len(patches),
            "ops": [p.get("op") for p in patches if isinstance(p, dict)],
        },
    )
    return session


def preview_session_to_dict(session: PreviewSession) -> dict[str, Any]:
    return {
        "preview_session_id": session.preview_session_id,
        "report_id": session.report_id,
        "base_spec_version": session.base_spec_version,
        "working_spec_json": session.working_spec_json,
        "patch_history_json": session.patch_history_json,
        "status": session.status,
        "updated_at": session.updated_at,
    }
