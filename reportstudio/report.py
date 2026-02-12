"""Utilities for building simple sales reports."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True)
class Sale:
    """A single sale entry."""

    category: str
    amount: float


def summarize_sales(sales: Iterable[Sale]) -> dict[str, float]:
    """Aggregate total sales by category.

    Args:
        sales: Iterable of :class:`Sale` records.

    Returns:
        A dictionary where keys are categories and values are total amounts.
    """
    totals: dict[str, float] = {}
    for sale in sales:
        totals[sale.category] = totals.get(sale.category, 0.0) + sale.amount
    return totals


def build_sales_report(sales: Iterable[Sale]) -> str:
    """Render a markdown sales report.

    The report includes one row per category and a grand total row.
    """
    totals = summarize_sales(sales)
    grand_total = sum(totals.values())

    lines = [
        "# Sales Report",
        "",
        "| Category | Amount |",
        "|---|---:|",
    ]

    for category in sorted(totals):
        lines.append(f"| {category} | {totals[category]:.2f} |")

    lines.append(f"| **Total** | **{grand_total:.2f}** |")
    return "\n".join(lines)
