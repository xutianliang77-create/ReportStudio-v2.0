from reportstudio.report import Sale, build_sales_report, summarize_sales


def test_summarize_sales_groups_by_category() -> None:
    sales = [
        Sale(category="Books", amount=24.5),
        Sale(category="Books", amount=10.0),
        Sale(category="Games", amount=59.99),
    ]

    assert summarize_sales(sales) == {"Books": 34.5, "Games": 59.99}


def test_build_sales_report_handles_empty_sales() -> None:
    report = build_sales_report([])

    assert "# Sales Report" in report
    assert "| **Total** | **0.00** |" in report


def test_build_sales_report_sorts_categories() -> None:
    report = build_sales_report(
        [Sale(category="Z", amount=1.0), Sale(category="A", amount=2.0)]
    )

    lines = report.splitlines()
    assert lines[4] == "| A | 2.00 |"
    assert lines[5] == "| Z | 1.00 |"
