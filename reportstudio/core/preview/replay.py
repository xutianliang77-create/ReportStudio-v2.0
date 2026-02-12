"""Pure replay helpers for PreviewSession patches."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from reportstudio.core.preview.patch import apply_patches


def stable_spec_dumps(spec: dict[str, Any]) -> str:
    """Stable JSON serialization for deterministic hashing/replay checks."""

    return json.dumps(spec, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def spec_hash(spec: dict[str, Any]) -> str:
    return hashlib.sha256(stable_spec_dumps(spec).encode("utf-8")).hexdigest()


def replay_patches(base_spec: dict[str, Any], patch_history: list[dict[str, Any]]) -> dict[str, Any]:
    """Replay patch history from base spec into a deterministic working spec.

    This function is intentionally pure: no global state, no randomness,
    no time/io/network dependencies.
    """

    if not patch_history:
        return apply_patches(base_spec, [])
    return apply_patches(base_spec, patch_history)
