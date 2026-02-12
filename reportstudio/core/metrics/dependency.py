"""Metric dependency graph utilities (AST -> DAG -> execution order)."""

from __future__ import annotations

from dataclasses import dataclass

from reportstudio.core.metrics.ast import BinaryOp, Expr, FunctionCall, Identifier, NumberLiteral, RawExpression, UnaryOp


class MetricDependencyError(ValueError):
    """Metric dependency error for DAG validation."""

    def __init__(self, message: str):
        self.code = "E2002"
        super().__init__(f"E2002: {message}")


@dataclass(frozen=True)
class MetricDependencyGraph:
    deps: dict[str, set[str]]


def _walk_identifiers(expr: Expr) -> set[str]:
    if isinstance(expr, Identifier):
        return {expr.name}
    if isinstance(expr, (NumberLiteral, RawExpression)):
        return set()
    if isinstance(expr, UnaryOp):
        return _walk_identifiers(expr.operand)
    if isinstance(expr, BinaryOp):
        return _walk_identifiers(expr.left) | _walk_identifiers(expr.right)
    if isinstance(expr, FunctionCall):
        out: set[str] = set()
        for arg in expr.args:
            out |= _walk_identifiers(arg)
        return out
    return set()


def build_dependency_graph(metric_asts: dict[str, Expr]) -> MetricDependencyGraph:
    names = set(metric_asts)
    deps: dict[str, set[str]] = {}
    for metric_name, ast in metric_asts.items():
        identifiers = _walk_identifiers(ast)
        deps[metric_name] = {x for x in identifiers if x in names}
    return MetricDependencyGraph(deps=deps)


def topological_sort(graph: MetricDependencyGraph) -> list[str]:
    deps = {k: set(v) for k, v in graph.deps.items()}
    reverse: dict[str, set[str]] = {k: set() for k in deps}
    for node, node_deps in deps.items():
        for dep in node_deps:
            reverse[dep].add(node)

    queue = [name for name, node_deps in deps.items() if not node_deps]
    order: list[str] = []

    while queue:
        current = queue.pop(0)
        order.append(current)
        for dependent in sorted(reverse[current]):
            if current in deps[dependent]:
                deps[dependent].remove(current)
            if not deps[dependent] and dependent not in order and dependent not in queue:
                queue.append(dependent)

    if len(order) != len(graph.deps):
        raise MetricDependencyError(_format_cycle_error(deps))

    return order


def _format_cycle_error(remaining: dict[str, set[str]]) -> str:
    nodes = [k for k, v in remaining.items() if v]
    if not nodes:
        return "cyclic dependency detected"

    start = nodes[0]
    path: list[str] = []
    seen: set[str] = set()
    cur = start
    while cur not in seen:
        seen.add(cur)
        path.append(cur)
        next_nodes = sorted(remaining.get(cur, set()))
        if not next_nodes:
            break
        cur = next_nodes[0]

    if cur in path:
        idx = path.index(cur)
        cycle = path[idx:] + [cur]
        return f"cyclic dependency detected: {' -> '.join(cycle)}"
    return "cyclic dependency detected"
