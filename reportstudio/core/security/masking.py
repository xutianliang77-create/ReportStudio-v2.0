"""Masking engine for preview/export data consistency."""

from __future__ import annotations

import re
from copy import deepcopy
from dataclasses import dataclass
from typing import Any


MASK_PHONE = "phone"
MASK_EMAIL = "email"
MASK_ID = "id"
MASK_ADDRESS = "address"


_PHONE_RE = re.compile(r"\d")
_EMAIL_RE = re.compile(r"^([^@\s]+)@([^@\s]+)$")


@dataclass(frozen=True)
class MaskingAppliedField:
    field: str
    rule: str


def _detect_rule(field_name: str) -> str | None:
    lowered = field_name.lower()
    if any(k in lowered for k in ("phone", "mobile", "tel", "手机号", "电话")):
        return MASK_PHONE
    if any(k in lowered for k in ("email", "邮箱", "mail")):
        return MASK_EMAIL
    if any(k in lowered for k in ("id", "身份证", "id_no", "证件")):
        return MASK_ID
    if any(k in lowered for k in ("address", "addr", "地址")):
        return MASK_ADDRESS
    return None


def _mask_phone(value: str, level: str) -> str:
    digits = [m.start() for m in _PHONE_RE.finditer(value)]
    if len(digits) < 7:
        return value
    if level == "strict":
        keep = {digits[0], digits[-1]}
    else:
        keep = {digits[0], digits[1], digits[-2], digits[-1]}
    chars = list(value)
    for idx in digits:
        if idx not in keep:
            chars[idx] = "*"
    return "".join(chars)


def _mask_email(value: str, level: str) -> str:
    m = _EMAIL_RE.match(value)
    if not m:
        return value
    local, domain = m.group(1), m.group(2)
    if not local:
        return value
    if level == "strict":
        local_masked = local[0] + "*" * max(1, len(local) - 1)
    else:
        local_masked = local[0] + "***"
    return f"{local_masked}@{domain}"


def _mask_id(value: str, level: str) -> str:
    if len(value) <= 4:
        return "*" * len(value)
    if level == "strict":
        return value[0] + "*" * (len(value) - 2) + value[-1]
    return value[:2] + "*" * (len(value) - 4) + value[-2:]


def _mask_address(value: str, level: str) -> str:
    if level == "strict":
        return value[:2] + "***" if len(value) > 2 else "***"
    if len(value) <= 6:
        return value[:3] + "***"
    return value[:6] + "***"


_MASKERS = {
    MASK_PHONE: _mask_phone,
    MASK_EMAIL: _mask_email,
    MASK_ID: _mask_id,
    MASK_ADDRESS: _mask_address,
}


def apply_masking(
    rows: list[dict[str, Any]],
    *,
    masking_level: str = "standard",
    rules: dict[str, str] | None = None,
) -> tuple[list[dict[str, Any]], list[MaskingAppliedField]]:
    """Apply field-level masking to rows.

    - masking_level: none/standard/strict
    - rules: explicit mapping {field_name: rule_type}; auto detection is fallback
    """

    if masking_level == "none":
        return deepcopy(rows), []

    explicit_rules = rules or {}
    masked_rows = deepcopy(rows)

    applied: dict[str, str] = {}
    for row in masked_rows:
        for key, value in list(row.items()):
            if value is None:
                continue
            text = str(value)
            rule = explicit_rules.get(key) or _detect_rule(key)
            if rule not in _MASKERS:
                continue
            row[key] = _MASKERS[rule](text, masking_level)
            applied[key] = rule

    applied_fields = [MaskingAppliedField(field=k, rule=v) for k, v in sorted(applied.items())]
    return masked_rows, applied_fields
