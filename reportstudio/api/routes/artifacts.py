"""/artifacts route handlers."""

from __future__ import annotations

from reportstudio.api.deps import acl_error_response, enforce_acl
from reportstudio.core.render.job_service import get_job
from reportstudio.core.security.acl import ACLDeniedError


def sign_artifact_route(artifact_id: str, *, principal_id: str = "owner") -> dict:
    # In this scaffold, artifact_id == render_id.
    job = get_job(artifact_id)
    try:
        enforce_acl(
            resource_type="report",
            resource_id=job.report_id,
            principal_id=principal_id,
            actions_any={"export"},
        )
    except ACLDeniedError as exc:
        return acl_error_response(exc)

    return {
        "code": 200,
        "message": "success",
        "data": {
            "artifact": {
                "artifact_id": artifact_id,
                "signed_url": f"https://example.local/artifacts/{artifact_id}?token=stub",
            }
        },
    }
