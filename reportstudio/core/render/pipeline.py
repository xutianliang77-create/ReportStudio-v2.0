"""Render pipeline helpers with unified masking before tables.json."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any
import json

from reportstudio.core.render.job_service import append_audit_log
from reportstudio.core.security.masking import apply_masking


def build_tables_json(
    *,
    rows: list[dict[str, Any]],
    render_id: str,
    masking_level: str = "standard",
    masking_rules: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Build masked tables payload used by both preview and export.

    Masking is applied before generating tables.json to ensure consistency.
    """

    masked_rows, applied_fields = apply_masking(rows, masking_level=masking_level, rules=masking_rules)

    append_audit_log(
        render_id,
        "masking.applied",
        {
            "masking_level": masking_level,
            "fields": [{"field": x.field, "rule": x.rule} for x in applied_fields],
        },
    )

    return {
        "masking_level": masking_level,
        "rows": masked_rows,
        "columns": sorted({k for row in masked_rows for k in row.keys()}),
    }


def write_tables_json(
    *,
    rows: list[dict[str, Any]],
    render_id: str,
    out_file: Path,
    masking_level: str = "standard",
    masking_rules: dict[str, str] | None = None,
) -> dict[str, Any]:
    tables = build_tables_json(
        rows=rows,
        render_id=render_id,
        masking_level=masking_level,
        masking_rules=masking_rules,
    )
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(tables, ensure_ascii=False, sort_keys=True, indent=2), encoding="utf-8")
    return tables


def preview_tables_payload(
    *,
    rows: list[dict[str, Any]],
    render_id: str,
    masking_level: str = "standard",
    masking_rules: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Preview side payload builder (delegates to same masking path)."""

    return build_tables_json(
        rows=rows,
        render_id=render_id,
        masking_level=masking_level,
        masking_rules=masking_rules,
    )


def export_tables_payload(
    *,
    rows: list[dict[str, Any]],
    render_id: str,
    masking_level: str = "standard",
    masking_rules: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Export side payload builder (delegates to same masking path)."""

    return build_tables_json(
        rows=rows,
        render_id=render_id,
        masking_level=masking_level,
        masking_rules=masking_rules,
    )


def clone_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return deepcopy(rows)
