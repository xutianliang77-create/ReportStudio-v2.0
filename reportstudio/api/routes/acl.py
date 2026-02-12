"""/acl/policies route handlers."""

from __future__ import annotations

from dataclasses import dataclass

from reportstudio.core.security.acl import list_policies, policy_to_dict, upsert_policy


@dataclass(frozen=True)
class UpsertACLPolicyDTO:
    resource_type: str
    resource_id: str
    principal_type: str
    principal_id: str
    actions_json: list[str]


def upsert_acl_policy_route(payload: UpsertACLPolicyDTO) -> dict:
    policy = upsert_policy(
        resource_type=payload.resource_type,
        resource_id=payload.resource_id,
        principal_type=payload.principal_type,
        principal_id=payload.principal_id,
        actions_json=payload.actions_json,
    )
    return {
        "code": 200,
        "message": "success",
        "data": {
            "policy": policy_to_dict(policy),
        },
    }


def list_acl_policies_route(*, resource_type: str, resource_id: str) -> dict:
    policies = [policy_to_dict(x) for x in list_policies(resource_type=resource_type, resource_id=resource_id)]
    return {
        "code": 200,
        "message": "success",
        "data": {
            "policies": policies,
        },
    }
