"""Op-based patch operations for PreviewSession working specs."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from reportstudio.core.metrics.ast import BinaryOp, FunctionCall, Identifier, RawExpression, UnaryOp
from reportstudio.core.metrics.dsl_parser import DSLParseError, parse_expression_to_ast


@dataclass(frozen=True)
class PreviewPatchError(ValueError):
    code: str
    message: str

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"


def _schema_field_names(spec: dict[str, Any]) -> set[str]:
    names: set[str] = set()
    for field in spec.get("dataset_fields", []):
        if isinstance(field, str):
            names.add(field)
    schema = spec.get("schema", {})
    if isinstance(schema, dict):
        fields = schema.get("fields", [])
        if isinstance(fields, list):
            for field in fields:
                if isinstance(field, str):
                    names.add(field)
                elif isinstance(field, dict) and isinstance(field.get("name"), str):
                    names.add(field["name"])
    return names


def _metric_names(spec: dict[str, Any]) -> set[str]:
    metrics = spec.get("metrics", {})
    if not isinstance(metrics, dict):
        return set()
    dsl = metrics.get("dsl", {})
    if not isinstance(dsl, dict):
        return set()
    return {name for name in dsl.keys() if isinstance(name, str)}


def _collect_identifiers(node: Any) -> set[str]:
    if isinstance(node, Identifier):
        return {node.name}
    if isinstance(node, UnaryOp):
        return _collect_identifiers(node.operand)
    if isinstance(node, BinaryOp):
        return _collect_identifiers(node.left) | _collect_identifiers(node.right)
    if isinstance(node, FunctionCall):
        names: set[str] = set()
        for arg in node.args:
            names |= _collect_identifiers(arg)
        return names
    if isinstance(node, RawExpression):
        return set()
    return set()


def _blocks_container(spec: dict[str, Any]) -> list[dict[str, Any]]:
    layout = spec.get("layout")
    if isinstance(layout, dict) and isinstance(layout.get("blocks"), list):
        return [x for x in layout["blocks"] if isinstance(x, dict)]
    if isinstance(spec.get("blocks"), list):
        return [x for x in spec["blocks"] if isinstance(x, dict)]
    spec.setdefault("layout", {})
    if isinstance(spec["layout"], dict):
        spec["layout"].setdefault("blocks", [])
        return spec["layout"]["blocks"]
    raise PreviewPatchError("E1003", "spec.layout must be an object")


def _locate_block(spec: dict[str, Any], block_id: str | None, chart_name: str | None) -> dict[str, Any]:
    blocks = _blocks_container(spec)
    for block in blocks:
        if block_id and block.get("block_id") == block_id:
            return block
        if chart_name:
            if block.get("chart_name") == chart_name:
                return block
            chart = block.get("chart")
            if isinstance(chart, dict) and chart.get("name") == chart_name:
                return block
    needle = block_id or chart_name or "unknown"
    raise PreviewPatchError("E1003", f"target block/chart not found: {needle}")


def _validate_mapping_fields(spec: dict[str, Any], mappings: dict[str, Any]) -> None:
    available = _schema_field_names(spec)
    if not available:
        return
    for source in mappings.keys():
        if source not in available:
            raise PreviewPatchError("E1003", f"field not found: {source}")


def _apply_replace_chart(spec: dict[str, Any], patch: dict[str, Any]) -> None:
    block = _locate_block(spec, patch.get("block_id"), patch.get("chart_name"))
    new_chart = patch.get("new_chart")
    if not isinstance(new_chart, dict):
        raise PreviewPatchError("E1003", "replace_chart requires object field 'new_chart'")
    block["chart"] = deepcopy(new_chart)


def _apply_update_metric(spec: dict[str, Any], patch: dict[str, Any]) -> None:
    metric_name = patch.get("metric_name")
    expression = patch.get("expression")
    if not isinstance(metric_name, str) or not isinstance(expression, str):
        raise PreviewPatchError("E1003", "update_metric requires 'metric_name' and 'expression'")

    metrics = spec.setdefault("metrics", {})
    if not isinstance(metrics, dict):
        raise PreviewPatchError("E1003", "spec.metrics must be an object")
    dsl = metrics.setdefault("dsl", {})
    if not isinstance(dsl, dict):
        raise PreviewPatchError("E1003", "spec.metrics.dsl must be an object")

    try:
        ast = parse_expression_to_ast(expression)
    except DSLParseError as exc:
        raise PreviewPatchError("E2001", str(exc)) from exc

    available = _schema_field_names(spec) | _metric_names(spec)
    available.add(metric_name)
    for name in _collect_identifiers(ast):
        if available and name not in available:
            raise PreviewPatchError("E1003", f"field not found: {name}")

    dsl[metric_name] = expression


def _apply_set_topn(spec: dict[str, Any], patch: dict[str, Any]) -> None:
    top_n = patch.get("top_n")
    if not isinstance(top_n, int) or top_n <= 0:
        raise PreviewPatchError("E1003", "set_topn requires positive integer 'top_n'")
    block = _locate_block(spec, patch.get("block_id"), patch.get("chart_name"))
    block["top_n"] = top_n
    if isinstance(block.get("chart"), dict):
        block["chart"]["top_n"] = top_n


def _apply_update_mapping(spec: dict[str, Any], patch: dict[str, Any]) -> None:
    mappings = patch.get("mappings")
    if not isinstance(mappings, dict):
        raise PreviewPatchError("E1003", "update_mapping requires object field 'mappings'")
    _validate_mapping_fields(spec, mappings)
    mapping_contract = spec.setdefault("mapping_contract", {})
    if not isinstance(mapping_contract, dict):
        raise PreviewPatchError("E1003", "spec.mapping_contract must be an object")
    fields = mapping_contract.setdefault("fields", {})
    if not isinstance(fields, dict):
        raise PreviewPatchError("E1003", "spec.mapping_contract.fields must be an object")
    fields.update(mappings)


def _apply_set_style(spec: dict[str, Any], patch: dict[str, Any]) -> None:
    style = patch.get("style")
    if not isinstance(style, dict):
        raise PreviewPatchError("E1003", "set_style requires object field 'style'")
    style_config = spec.setdefault("style_config", {})
    if not isinstance(style_config, dict):
        raise PreviewPatchError("E1003", "spec.style_config must be an object")
    style_config.update(style)


_HANDLERS = {
    "replace_chart": _apply_replace_chart,
    "update_metric": _apply_update_metric,
    "set_topn": _apply_set_topn,
    "update_mapping": _apply_update_mapping,
    "set_style": _apply_set_style,
}


def apply_patches(spec: dict[str, Any], patches: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(patches, list):
        raise PreviewPatchError("E1003", "patches must be a list")

    next_spec = deepcopy(spec)
    for patch in patches:
        if not isinstance(patch, dict):
            raise PreviewPatchError("E1003", "each patch must be an object")
        op = patch.get("op")
        if not isinstance(op, str) or op not in _HANDLERS:
            raise PreviewPatchError("E1003", f"unsupported patch op: {op}")
        _HANDLERS[op](next_spec, patch)
    return next_spec
