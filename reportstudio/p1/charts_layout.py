"""P1-301~P1-303: 图表推荐与布局构建。"""

from __future__ import annotations


def recommend_chart(has_time_dimension: bool, has_category_dimension: bool) -> str:
    if has_time_dimension:
        return "line"
    if has_category_dimension:
        return "bar"
    return "kpi"


def build_layout(has_time_dimension: bool, include_insight: bool = True) -> list[str]:
    sections = ["cover"]
    if include_insight:
        sections.append("insight_summary")
    sections.append("kpi_cards")
    sections.append("trend_chart" if has_time_dimension else "structure_analysis")
    sections += ["detail_table", "glossary"]
    return sections
