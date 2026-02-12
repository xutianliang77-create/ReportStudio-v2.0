"""API dependency helpers (authn/authz scaffolding)."""

from __future__ import annotations

from reportstudio.core.security.acl import ACLDeniedError, require_permission


def enforce_acl(
    *,
    resource_type: str,
    resource_id: str,
    principal_id: str | None,
    actions_any: set[str],
) -> None:
    require_permission(
        resource_type=resource_type,
        resource_id=resource_id,
        principal_id=principal_id,
        actions_any=actions_any,
    )


def acl_error_response(exc: ACLDeniedError) -> dict:
    return {
        "code": 403,
        "message": str(exc),
        "error_code": exc.code,
        "data": {},
    }
