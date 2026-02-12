"""Template service with in-memory models and versioning."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any
import uuid


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class TemplateSpec:
    layout: dict[str, Any]
    mapping_contract: dict[str, Any]
    style_config: dict[str, Any]
    export_preset: dict[str, Any]


@dataclass
class Template:
    template_id: str
    name: str
    description: str | None
    status: str
    latest_version: int
    created_at: str
    updated_at: str


@dataclass
class TemplateVersion:
    template_id: str
    version: int
    spec_json: dict[str, Any]
    changelog: str | None
    created_at: str


_TEMPLATES: dict[str, Template] = {}
_TEMPLATE_VERSIONS: dict[str, list[TemplateVersion]] = {}
_AUDIT_LOGS: list[dict[str, Any]] = []


def _append_audit_log(action: str, detail: dict[str, Any]) -> None:
    _AUDIT_LOGS.append({"action": action, "detail": detail, "created_at": _now()})


def list_audit_logs(action: str | None = None) -> list[dict[str, Any]]:
    if action is None:
        return list(_AUDIT_LOGS)
    return [x for x in _AUDIT_LOGS if x["action"] == action]


def create_template(*, name: str, spec: TemplateSpec, description: str | None = None) -> tuple[Template, TemplateVersion]:
    ts = _now()
    template_id = f"tpl_{uuid.uuid4().hex[:12]}"
    template = Template(
        template_id=template_id,
        name=name,
        description=description,
        status="active",
        latest_version=1,
        created_at=ts,
        updated_at=ts,
    )
    version = TemplateVersion(
        template_id=template_id,
        version=1,
        spec_json=asdict(spec),
        changelog="initial version",
        created_at=ts,
    )
    _TEMPLATES[template_id] = template
    _TEMPLATE_VERSIONS[template_id] = [version]
    _append_audit_log(
        "template.create",
        {"template_id": template_id, "version": 1, "name": name},
    )
    return template, version


def get_template(template_id: str) -> tuple[Template, TemplateVersion]:
    template = _TEMPLATES[template_id]
    version = _TEMPLATE_VERSIONS[template_id][-1]
    return template, version


def create_template_version(*, template_id: str, spec: TemplateSpec, changelog: str | None = None) -> TemplateVersion:
    template = _TEMPLATES[template_id]
    version = template.latest_version + 1
    created = TemplateVersion(
        template_id=template_id,
        version=version,
        spec_json=asdict(spec),
        changelog=changelog,
        created_at=_now(),
    )
    _TEMPLATE_VERSIONS[template_id].append(created)
    template.latest_version = version
    template.updated_at = _now()
    _append_audit_log(
        "template.version.create",
        {"template_id": template_id, "version": version, "changelog": changelog},
    )
    return created


def list_template_versions(template_id: str) -> list[TemplateVersion]:
    return list(_TEMPLATE_VERSIONS[template_id])


def template_to_dict(template: Template, latest: TemplateVersion) -> dict[str, Any]:
    return {
        "template_id": template.template_id,
        "name": template.name,
        "description": template.description,
        "status": template.status,
        "latest_version": template.latest_version,
        "latest_spec": latest.spec_json,
        "created_at": template.created_at,
        "updated_at": template.updated_at,
    }


def version_to_dict(version: TemplateVersion) -> dict[str, Any]:
    return {
        "template_id": version.template_id,
        "version": version.version,
        "spec": version.spec_json,
        "changelog": version.changelog,
        "created_at": version.created_at,
    }
