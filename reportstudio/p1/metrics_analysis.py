"""P1-201~P1-204: 基础指标与分析能力。"""

from __future__ import annotations

from collections import defaultdict


def compute_metrics(rows: list[dict], metric_field: str) -> dict:
    values = [float(r[metric_field]) for r in rows if r.get(metric_field) not in (None, "")]
    total = sum(values)
    count = len(values)
    avg = total / count if count else 0
    return {"sum": round(total, 4), "count": count, "avg": round(avg, 4)}


def groupby_sum(rows: list[dict], dimension: str, metric_field: str) -> list[dict]:
    agg = defaultdict(float)
    for r in rows:
        key = r.get(dimension, "")
        value = float(r.get(metric_field, 0) or 0)
        agg[key] += value
    return [{dimension: k, "sum": round(v, 4)} for k, v in sorted(agg.items(), key=lambda i: i[1], reverse=True)]


def topn(rows: list[dict], dimension: str, metric_field: str, n: int = 10) -> list[dict]:
    return groupby_sum(rows, dimension, metric_field)[:n]
