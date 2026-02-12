"""In-memory ACL/RBAC policy engine for scaffold APIs."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, NoReturn


@dataclass(frozen=True)
class ACLPolicy:
    resource_type: str
    resource_id: str
    principal_type: str
    principal_id: str
    actions_json: list[str]


@dataclass(frozen=True)
class ACLDeniedError(PermissionError):
    code: str
    message: str

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"


_POLICIES: dict[tuple[str, str, str, str], ACLPolicy] = {}
_RESOURCE_OWNERS: dict[tuple[str, str], str] = {}
_AUDIT_LOGS: list[dict[str, Any]] = []


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _append_audit_log(action: str, detail: dict[str, Any]) -> None:
    _AUDIT_LOGS.append({"action": action, "detail": detail, "created_at": _now()})


def list_audit_logs(action: str | None = None) -> list[dict[str, Any]]:
    if action is None:
        return list(_AUDIT_LOGS)
    return [x for x in _AUDIT_LOGS if x["action"] == action]


def set_resource_owner(resource_type: str, resource_id: str, owner_id: str) -> None:
    _RESOURCE_OWNERS[(resource_type, resource_id)] = owner_id


def get_resource_owner(resource_type: str, resource_id: str) -> str | None:
    return _RESOURCE_OWNERS.get((resource_type, resource_id))


def upsert_policy(
    *,
    resource_type: str,
    resource_id: str,
    principal_type: str,
    principal_id: str,
    actions_json: list[str],
) -> ACLPolicy:
    policy = ACLPolicy(
        resource_type=resource_type,
        resource_id=resource_id,
        principal_type=principal_type,
        principal_id=principal_id,
        actions_json=sorted({x for x in actions_json if isinstance(x, str)}),
    )
    _POLICIES[(resource_type, resource_id, principal_type, principal_id)] = policy
    return policy


def list_policies(*, resource_type: str, resource_id: str) -> list[ACLPolicy]:
    values: list[ACLPolicy] = []
    for policy in _POLICIES.values():
        if policy.resource_type == resource_type and policy.resource_id == resource_id:
            values.append(policy)
    return values


def policy_to_dict(policy: ACLPolicy) -> dict[str, Any]:
    return asdict(policy)


def _raise_deny(*, code: str, message: str, detail: dict[str, Any]) -> NoReturn:
    _append_audit_log("acl.deny", detail)
    raise ACLDeniedError(code=code, message=message)


def require_permission(
    *,
    resource_type: str,
    resource_id: str,
    principal_id: str | None,
    actions_any: set[str],
    principal_type: str = "user",
) -> None:
    if not principal_id:
        _raise_deny(
            code="E4001",
            message="missing principal",
            detail={
                "resource_type": resource_type,
                "resource_id": resource_id,
                "principal_type": principal_type,
                "principal_id": principal_id,
                "required_actions": sorted(actions_any),
                "reason": "missing_principal",
            },
        )

    pid = principal_id
    assert pid is not None
    owner_id = get_resource_owner(resource_type, resource_id)
    if owner_id is None and pid == "owner":
        return
    if owner_id is not None and pid == owner_id:
        return

    matched = list_policies(resource_type=resource_type, resource_id=resource_id)
    # Default policy requirement: owner full access; without policy only owner allowed.
    if not matched:
        _raise_deny(
            code="E4002",
            message="permission denied",
            detail={
                "resource_type": resource_type,
                "resource_id": resource_id,
                "principal_type": principal_type,
                "principal_id": principal_id,
                "required_actions": sorted(actions_any),
                "reason": "no_policy_non_owner",
            },
        )

    principal_policy = _POLICIES.get((resource_type, resource_id, principal_type, pid))
    if principal_policy is None:
        _raise_deny(
            code="E4002",
            message="permission denied",
            detail={
                "resource_type": resource_type,
                "resource_id": resource_id,
                "principal_type": principal_type,
                "principal_id": principal_id,
                "required_actions": sorted(actions_any),
                "reason": "principal_policy_not_found",
            },
        )

    granted = set(principal_policy.actions_json)
    if not granted.intersection(actions_any):
        _raise_deny(
            code="E4002",
            message="permission denied",
            detail={
                "resource_type": resource_type,
                "resource_id": resource_id,
                "principal_type": principal_type,
                "principal_id": principal_id,
                "required_actions": sorted(actions_any),
                "granted_actions": sorted(granted),
                "reason": "action_not_granted",
            },
        )
