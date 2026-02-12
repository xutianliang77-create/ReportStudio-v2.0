"""Report version snapshot service (immutable version records + rollback)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from typing import Any
import uuid


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash_spec(spec: dict[str, Any]) -> str:
    payload = json.dumps(spec, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass
class Report:
    report_id: str
    name: str
    current_spec: dict[str, Any]
    current_spec_version_id: str | None
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class ReportVersion:
    version_id: str
    report_id: str
    version_no: int
    spec_json: dict[str, Any]
    created_at: str


_REPORTS: dict[str, Report] = {}
_REPORT_VERSIONS: dict[str, list[ReportVersion]] = {}
_AUDIT_LOGS: list[dict[str, Any]] = []


def _append_audit_log(action: str, detail: dict[str, Any]) -> None:
    _AUDIT_LOGS.append({"action": action, "detail": detail, "created_at": _now()})


def list_audit_logs(action: str | None = None) -> list[dict[str, Any]]:
    if action is None:
        return list(_AUDIT_LOGS)
    return [x for x in _AUDIT_LOGS if x["action"] == action]


def create_report(*, name: str, spec: dict[str, Any]) -> Report:
    ts = _now()
    report = Report(
        report_id=f"rp_{uuid.uuid4().hex[:12]}",
        name=name,
        current_spec=dict(spec),
        current_spec_version_id=None,
        created_at=ts,
        updated_at=ts,
    )
    _REPORTS[report.report_id] = report
    _REPORT_VERSIONS[report.report_id] = []
    return report


def update_report_spec(report_id: str, spec: dict[str, Any]) -> Report:
    report = _REPORTS[report_id]
    report.current_spec = dict(spec)
    report.current_spec_version_id = None
    report.updated_at = _now()
    return report


def commit_report_version(*, report_id: str, spec: dict[str, Any] | None = None) -> ReportVersion:
    report = _REPORTS[report_id]
    versions = _REPORT_VERSIONS[report_id]
    next_no = len(versions) + 1
    snapshot = dict(spec) if spec is not None else dict(report.current_spec)

    # immutable snapshot record: append-only object, never updated in-place
    version = ReportVersion(
        version_id=f"rv_{uuid.uuid4().hex[:12]}",
        report_id=report_id,
        version_no=next_no,
        spec_json=snapshot,
        created_at=_now(),
    )
    versions.append(version)
    report.current_spec = dict(snapshot)
    report.current_spec_version_id = version.version_id
    report.updated_at = _now()
    _append_audit_log(
        "report.version.commit",
        {
            "report_id": report_id,
            "version_id": version.version_id,
            "version_no": version.version_no,
        },
    )
    return version


def rollback_report(*, report_id: str, version_id: str) -> Report:
    report = _REPORTS[report_id]
    target = get_report_version(report_id, version_id)
    from_version = report.current_spec_version_id
    report.current_spec = dict(target.spec_json)
    report.current_spec_version_id = target.version_id
    report.updated_at = _now()
    _append_audit_log(
        "report.rollback",
        {
            "report_id": report_id,
            "from_version_id": from_version,
            "to_version_id": target.version_id,
        },
    )
    return report


def render_from_current_spec(report_id: str) -> dict[str, Any]:
    """Scaffold rerender hook that depends on current spec only."""

    report = _REPORTS[report_id]
    spec_hash = _hash_spec(report.current_spec)
    return {
        "report_id": report_id,
        "spec_hash": spec_hash,
        "current_spec_version_id": report.current_spec_version_id,
    }


def list_report_versions(report_id: str) -> list[ReportVersion]:
    return list(_REPORT_VERSIONS[report_id])


def get_report_version(report_id: str, version_id: str) -> ReportVersion:
    for item in _REPORT_VERSIONS[report_id]:
        if item.version_id == version_id:
            return item
    raise KeyError(version_id)


def report_to_dict(report: Report) -> dict[str, Any]:
    return {
        "report_id": report.report_id,
        "name": report.name,
        "spec": report.current_spec,
        "current_spec_version_id": report.current_spec_version_id,
        "created_at": report.created_at,
        "updated_at": report.updated_at,
    }


def report_version_to_dict(version: ReportVersion) -> dict[str, Any]:
    return {
        "version_id": version.version_id,
        "report_id": version.report_id,
        "version_no": version.version_no,
        "spec": version.spec_json,
        "created_at": version.created_at,
    }
