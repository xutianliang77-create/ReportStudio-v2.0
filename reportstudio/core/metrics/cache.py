"""Metric compute cache keyed by dataset + params hash + metric expr hash."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any


@dataclass(frozen=True)
class MetricCacheKey:
    dataset_id: str
    params_hash: str
    metric_expr_hash: str

    def to_key(self) -> str:
        return f"{self.dataset_id}:{self.params_hash}:{self.metric_expr_hash}"


def _stable_hash(value: Any) -> str:
    blob = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def build_metric_cache_key(*, dataset_id: str, params: dict[str, Any], metric_expressions: dict[str, str]) -> MetricCacheKey:
    return MetricCacheKey(
        dataset_id=dataset_id,
        params_hash=_stable_hash(params),
        metric_expr_hash=_stable_hash(metric_expressions),
    )


_CACHE: dict[str, dict[str, Any]] = {}


def cache_get(key: MetricCacheKey) -> dict[str, Any] | None:
    value = _CACHE.get(key.to_key())
    if value is None:
        return None
    return dict(value)


def cache_set(key: MetricCacheKey, value: dict[str, Any]) -> None:
    _CACHE[key.to_key()] = dict(value)


def cache_clear() -> None:
    _CACHE.clear()
