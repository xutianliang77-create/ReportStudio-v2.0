"""/templates route handlers for template model + versioning."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

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


def create_template_route(payload: CreateTemplateDTO) -> dict:
    template, version = create_template(name=payload.name, description=payload.description, spec=payload.spec.to_domain())
    return {
        "code": 200,
        "message": "success",
        "data": {
            "template": template_to_dict(template, version),
            "version": version_to_dict(version),
        },
    }


def get_template_route(template_id: str) -> dict:
    template, latest = get_template(template_id)
    return {
        "code": 200,
        "message": "success",
        "data": {
            "template": template_to_dict(template, latest),
        },
    }


def create_template_version_route(template_id: str, payload: CreateTemplateVersionDTO) -> dict:
    version = create_template_version(template_id=template_id, spec=payload.spec.to_domain(), changelog=payload.changelog)
    return {
        "code": 200,
        "message": "success",
        "data": {
            "version": version_to_dict(version),
        },
    }


def list_template_versions_route(template_id: str) -> dict:
    versions = [version_to_dict(v) for v in list_template_versions(template_id)]
    return {
        "code": 200,
        "message": "success",
        "data": {
            "versions": versions,
        },
    }
