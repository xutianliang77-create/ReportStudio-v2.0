from __future__ import annotations

import pytest

from reportstudio.core.metrics.compute import build_metric_asts, plan_metric_compute_order
from reportstudio.core.metrics.dependency import MetricDependencyError, build_dependency_graph, topological_sort


def test_extract_dependencies_from_ast():
    asts = build_metric_asts(
        {
            "m_revenue": "sum(revenue)",
            "m_cost": "sum(cost)",
            "m_profit": "m_revenue - m_cost",
            "m_margin": "m_profit / m_revenue",
        }
    )
    graph = build_dependency_graph(asts)
    assert graph.deps["m_revenue"] == set()
    assert graph.deps["m_cost"] == set()
    assert graph.deps["m_profit"] == {"m_revenue", "m_cost"}
    assert graph.deps["m_margin"] == {"m_profit", "m_revenue"}


def test_topological_order_respects_dependencies():
    order = plan_metric_compute_order(
        {
            "m_revenue": "sum(revenue)",
            "m_cost": "sum(cost)",
            "m_profit": "m_revenue - m_cost",
            "m_margin": "m_profit / m_revenue",
        }
    )
    assert order.index("m_revenue") < order.index("m_profit")
    assert order.index("m_cost") < order.index("m_profit")
    assert order.index("m_profit") < order.index("m_margin")


def test_non_metric_identifiers_are_ignored_as_dependencies():
    order = plan_metric_compute_order(
        {
            "a": "sum(revenue)",
            "b": "a + lag(revenue,1)",
        }
    )
    assert order == ["a", "b"]


def test_nested_function_still_extracts_metric_identifier_deps():
    asts = build_metric_asts(
        {
            "a": "sum(revenue)",
            "b": "avg(a + lag(cost,2))",
        }
    )
    graph = build_dependency_graph(asts)
    assert graph.deps["b"] == {"a"}


def test_self_reference_is_detected_as_cycle():
    graph = build_dependency_graph(build_metric_asts({"a": "a + 1"}))
    with pytest.raises(MetricDependencyError) as exc:
        topological_sort(graph)
    assert "E2002" in str(exc.value)


def test_simple_cycle_raises_e2002():
    metric_expressions = {
        "a": "b + 1",
        "b": "c + 1",
        "c": "a + 1",
    }
    with pytest.raises(MetricDependencyError) as exc:
        plan_metric_compute_order(metric_expressions)
    message = str(exc.value)
    assert "E2002" in message
    assert "cyclic dependency" in message


def test_invalid_syntax_bubbles_up_without_fallback():
    with pytest.raises(ValueError) as exc:
        plan_metric_compute_order({"a": "1 +"})
    assert "E2001" in str(exc.value)


def test_invalid_syntax_fallback_keeps_ordering_possible():
    order = plan_metric_compute_order(
        {
            "a": "1 +",
            "b": "a + 1",
        },
        fallback_to_dsl_basic=True,
    )
    assert order == ["a", "b"]
