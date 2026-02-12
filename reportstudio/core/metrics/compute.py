"""Metric compute helpers based on DSL AST + dependency DAG."""

from __future__ import annotations

import logging
from typing import Any, Callable

from reportstudio.core.metrics.ast import Expr
from reportstudio.core.metrics.cache import build_metric_cache_key, cache_get, cache_set
from reportstudio.core.metrics.dependency import build_dependency_graph, topological_sort
from reportstudio.core.metrics.dsl_parser import parse_expression_to_ast

logger = logging.getLogger(__name__)


def build_metric_asts(metric_expressions: dict[str, str], *, fallback_to_dsl_basic: bool = False) -> dict[str, Expr]:
    return {
        metric_name: parse_expression_to_ast(expr, fallback_to_dsl_basic=fallback_to_dsl_basic)
        for metric_name, expr in metric_expressions.items()
    }


def plan_metric_compute_order(metric_expressions: dict[str, str], *, fallback_to_dsl_basic: bool = False) -> list[str]:
    asts = build_metric_asts(metric_expressions, fallback_to_dsl_basic=fallback_to_dsl_basic)
    graph = build_dependency_graph(asts)
    return topological_sort(graph)


def compute_metrics_with_cache(
    *,
    dataset_id: str,
    params: dict[str, Any],
    metric_expressions: dict[str, str],
    compute_fn: Callable[[], dict[str, Any]],
) -> dict[str, Any]:
    """Compute metric payloads with key-based cache.

    Cache key format is effectively: dataset_id + params_hash + metric_expr_hash.
    """

    key = build_metric_cache_key(dataset_id=dataset_id, params=params, metric_expressions=metric_expressions)
    cached = cache_get(key)
    if cached is not None:
        logger.debug(
            "metrics cache hit dataset_id=%s params_hash=%s metric_expr_hash=%s",
            dataset_id,
            key.params_hash,
            key.metric_expr_hash,
        )
        return cached

    result = compute_fn()
    cache_set(key, result)
    return result
