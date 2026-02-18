"""/templates route handlers for template model + versioning."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from reportstudio.api.deps import acl_error_response, enforce_acl
from reportstudio.core.security.acl import ACLDeniedError, set_resource_owner
from reportstudio.core.template.service import (
    TemplateSpec,
    create_template,
    create_template_version,
    get_template,
    list_template_versions,
    template_to_dict,
    version_to_dict,
)


@dataclass(frozen=True)
class TemplateSpecDTO:
    layout: dict[str, Any]
    mapping_contract: dict[str, Any]
    style_config: dict[str, Any]
    export_preset: dict[str, Any]

    def to_domain(self) -> TemplateSpec:
        return TemplateSpec(
            layout=self.layout,
            mapping_contract=self.mapping_contract,
            style_config=self.style_config,
            export_preset=self.export_preset,
        )


@dataclass(frozen=True)
class CreateTemplateDTO:
    name: str
    spec: TemplateSpecDTO
    description: str | None = None


@dataclass(frozen=True)
class CreateTemplateVersionDTO:
    spec: TemplateSpecDTO
    changelog: str | None = None


def create_template_route(payload: CreateTemplateDTO, *, principal_id: str = "owner") -> dict:
    template, version = create_template(name=payload.name, description=payload.description, spec=payload.spec.to_domain())
    set_resource_owner("template", template.template_id, principal_id)
    return {
        "code": 200,
        "message": "success",
        "data": {
            "template": template_to_dict(template, version),
            "version": version_to_dict(version),
        },
    }


def get_template_route(template_id: str, *, principal_id: str = "owner") -> dict:
    try:
        enforce_acl(
            resource_type="template",
            resource_id=template_id,
            principal_id=principal_id,
            actions_any={"edit", "manage"},
        )
    except ACLDeniedError as exc:
        return acl_error_response(exc)

    template, latest = get_template(template_id)
    return {
        "code": 200,
        "message": "success",
        "data": {
            "template": template_to_dict(template, latest),
        },
    }


def create_template_version_route(template_id: str, payload: CreateTemplateVersionDTO, *, principal_id: str = "owner") -> dict:
    try:
        enforce_acl(
            resource_type="template",
            resource_id=template_id,
            principal_id=principal_id,
            actions_any={"edit", "manage"},
        )
    except ACLDeniedError as exc:
        return acl_error_response(exc)

    version = create_template_version(template_id=template_id, spec=payload.spec.to_domain(), changelog=payload.changelog)
    return {
        "code": 200,
        "message": "success",
        "data": {
            "version": version_to_dict(version),
        },
    }


def list_template_versions_route(template_id: str, *, principal_id: str = "owner") -> dict:
    try:
        enforce_acl(
            resource_type="template",
            resource_id=template_id,
            principal_id=principal_id,
            actions_any={"edit", "manage"},
        )
    except ACLDeniedError as exc:
        return acl_error_response(exc)

    versions = [version_to_dict(v) for v in list_template_versions(template_id)]
    return {
        "code": 200,
        "message": "success",
        "data": {
            "versions": versions,
        },
    }
