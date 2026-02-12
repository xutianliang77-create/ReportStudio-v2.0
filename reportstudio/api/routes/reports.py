"""/reports route handlers for report version snapshots."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from reportstudio.api.deps import acl_error_response, enforce_acl
from reportstudio.core.security.acl import ACLDeniedError, set_resource_owner
from reportstudio.core.version import service as version_service
from reportstudio.core.version.service import (
    commit_report_version,
    create_report,
    get_report_version,
    list_report_versions,
    render_from_current_spec,
    report_to_dict,
    report_version_to_dict,
    rollback_report,
    update_report_spec,
)


@dataclass(frozen=True)
class CreateReportDTO:
    name: str
    spec: dict[str, Any]


@dataclass(frozen=True)
class CommitReportVersionDTO:
    spec: dict[str, Any] | None = None


def create_report_route(payload: CreateReportDTO, *, principal_id: str = "owner") -> dict:
    report = create_report(name=payload.name, spec=payload.spec)
    set_resource_owner("report", report.report_id, principal_id)
    return {
        "code": 200,
        "message": "success",
        "data": {
            "report": report_to_dict(report),
        },
    }


def get_report_route(report_id: str, *, principal_id: str = "owner") -> dict:
    try:
        enforce_acl(resource_type="report", resource_id=report_id, principal_id=principal_id, actions_any={"view"})
    except ACLDeniedError as exc:
        return acl_error_response(exc)

    report = version_service._REPORTS[report_id]
    return {
        "code": 200,
        "message": "success",
        "data": {
            "report": report_to_dict(report),
        },
    }


def update_report_spec_route(report_id: str, spec: dict[str, Any]) -> dict:
    report = update_report_spec(report_id, spec)
    return {
        "code": 200,
        "message": "success",
        "data": {
            "report": report_to_dict(report),
        },
    }


def commit_report_version_route(report_id: str, payload: CommitReportVersionDTO) -> dict:
    version = commit_report_version(report_id=report_id, spec=payload.spec)
    return {
        "code": 200,
        "message": "success",
        "data": {
            "version": report_version_to_dict(version),
        },
    }


def rollback_report_route(report_id: str, *, version_id: str) -> dict:
    report = rollback_report(report_id=report_id, version_id=version_id)
    return {
        "code": 200,
        "message": "success",
        "data": {
            "report": report_to_dict(report),
        },
    }


def rerender_report_route(report_id: str) -> dict:
    payload = render_from_current_spec(report_id)
    return {
        "code": 200,
        "message": "success",
        "data": {
            "render": payload,
        },
    }


def list_report_versions_route(report_id: str) -> dict:
    versions = [report_version_to_dict(v) for v in list_report_versions(report_id)]
    return {
        "code": 200,
        "message": "success",
        "data": {
            "versions": versions,
        },
    }


def get_report_version_route(report_id: str, version_id: str) -> dict:
    version = get_report_version(report_id, version_id)
    return {
        "code": 200,
        "message": "success",
        "data": {
            "version": report_version_to_dict(version),
        },
    }
