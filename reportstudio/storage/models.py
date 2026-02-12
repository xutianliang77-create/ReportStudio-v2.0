"""Storage model placeholders for render jobs, templates, and report versions.

This scaffold does not persist DB rows yet; fields mirror migration intent.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class RenderJobModel:
    render_id: str
    status: str
    input_path: str
    fmt: str
    metric_field: str
    dimension_field: str
    workspace_id: str
    report_id: str
    render_request_id: str | None = None
    progress: int = 0
    stage: str = "queued"
    artifact_file: str | None = None
    sha256: str | None = None
    error_code: str | None = None
    error_message: str | None = None


@dataclass
class TemplateModel:
    template_id: str
    name: str
    description: str | None = None
    status: str = "active"
    latest_version: int = 1


@dataclass
class TemplateVersionModel:
    template_id: str
    version: int
    spec_json: dict[str, Any] | None = None
    changelog: str | None = None


@dataclass
class ReportVersionModel:
    version_id: str
    report_id: str
    version_no: int
    spec_json: dict[str, Any]
    created_at: str


@dataclass
class PreviewSessionModel:
    preview_session_id: str
    report_id: str
    base_spec_version: str | None = None
    working_spec_json: dict[str, Any] | None = None
    patch_history_json: list[dict[str, Any]] | None = None
    status: str = "active"
    updated_at: str = ""


@dataclass
class ACLPolicyModel:
    resource_type: str
    resource_id: str
    principal_type: str
    principal_id: str
    actions_json: list[str]


# Intended DB constraints (for SQLAlchemy/Alembic-backed deployments):
# UNIQUE(workspace_id, report_id, render_request_id)
# UNIQUE(template_id, version)
# INDEX(template_id, latest_version)
# UNIQUE(report_id, version_no)
# UNIQUE(version_id)

# UNIQUE(preview_session_id)
# INDEX(report_id, updated_at)

# UNIQUE(resource_type, resource_id, principal_type, principal_id)
