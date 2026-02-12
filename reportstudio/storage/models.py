"""Storage model placeholders for render jobs.

This scaffold does not persist DB rows yet; fields mirror migration intent.
"""

from __future__ import annotations

from dataclasses import dataclass


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


# Intended DB constraint (for SQLAlchemy/Alembic-backed deployments):
# UNIQUE(workspace_id, report_id, render_request_id)
