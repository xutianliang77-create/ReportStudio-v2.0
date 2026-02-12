"""Metric compute planning helpers based on DSL AST + dependency DAG."""

from __future__ import annotations

from reportstudio.core.metrics.ast import Expr
from reportstudio.core.metrics.dependency import build_dependency_graph, topological_sort
from reportstudio.core.metrics.dsl_parser import parse_expression_to_ast


def build_metric_asts(metric_expressions: dict[str, str], *, fallback_to_dsl_basic: bool = False) -> dict[str, Expr]:
    return {
        metric_name: parse_expression_to_ast(expr, fallback_to_dsl_basic=fallback_to_dsl_basic)
        for metric_name, expr in metric_expressions.items()
    }


def plan_metric_compute_order(metric_expressions: dict[str, str], *, fallback_to_dsl_basic: bool = False) -> list[str]:
    asts = build_metric_asts(metric_expressions, fallback_to_dsl_basic=fallback_to_dsl_basic)
    graph = build_dependency_graph(asts)
    return topological_sort(graph)
