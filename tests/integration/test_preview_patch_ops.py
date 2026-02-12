import unittest

from reportstudio.api.routes.preview_sessions import (
    CreatePreviewSessionDTO,
    PatchPreviewSessionDTO,
    create_preview_session_route,
    get_preview_session_route,
    patch_preview_session_route,
)
from reportstudio.api.routes.reports import CommitReportVersionDTO, CreateReportDTO, commit_report_version_route, create_report_route
from reportstudio.core.preview import service as preview_service
from reportstudio.core.version import service as version_service


class PreviewPatchOpsIntegrationTests(unittest.TestCase):
    def setUp(self):
        version_service._REPORTS.clear()
        version_service._REPORT_VERSIONS.clear()
        version_service._AUDIT_LOGS.clear()
        preview_service._PREVIEW_SESSIONS.clear()
        preview_service._AUDIT_LOGS.clear()

    def _seed_session(self) -> str:
        report = create_report_route(
            CreateReportDTO(
                name="patch-report",
                spec={
                    "input_path": "tests/fixtures/sales.csv",
                    "format": "pdf",
                    "metric_field": "amount",
                    "dimension_field": "region",
                    "dataset_fields": ["amount", "region", "order_count", "sales"],
                    "metrics": {
                        "dsl": {
                            "revenue": "amount + 1",
                            "lagged": "lag(revenue,1)",
                        }
                    },
                    "mapping_contract": {"fields": {"amount": "sales"}},
                    "style_config": {"brand_color": "#0000FF"},
                    "layout": {
                        "blocks": [
                            {
                                "block_id": "b1",
                                "chart_name": "trend",
                                "top_n": 5,
                                "chart": {"name": "trend", "type": "line", "top_n": 5},
                            },
                            {
                                "block_id": "b2",
                                "chart_name": "table_sales",
                                "top_n": 10,
                                "chart": {"name": "table_sales", "type": "table", "top_n": 10},
                            },
                        ]
                    },
                },
            )
        )
        report_id = report["data"]["report"]["report_id"]
        committed = commit_report_version_route(report_id, CommitReportVersionDTO())
        base_version_id = committed["data"]["version"]["version_id"]

        created = create_preview_session_route(
            CreatePreviewSessionDTO(report_id=report_id, base_version_id=base_version_id)
        )
        return created["data"]["preview_session"]["preview_session_id"]

    def test_apply_all_patch_ops(self):
        preview_session_id = self._seed_session()

        response = patch_preview_session_route(
            preview_session_id,
            PatchPreviewSessionDTO(
                patches=[
                    {
                        "op": "replace_chart",
                        "block_id": "b1",
                        "new_chart": {"name": "trend", "type": "bar", "top_n": 7},
                    },
                    {
                        "op": "update_metric",
                        "metric_name": "revenue",
                        "expression": "lag(order_count,1)+amount",
                    },
                    {
                        "op": "set_topn",
                        "chart_name": "table_sales",
                        "top_n": 3,
                    },
                    {
                        "op": "update_mapping",
                        "mappings": {"amount": "sales", "region": "region"},
                    },
                    {
                        "op": "set_style",
                        "style": {
                            "brand_color": "#FF0000",
                            "font_family": "PingFang SC",
                            "header_text": "Monthly Report",
                            "footer_text": "Internal",
                        },
                    },
                ]
            ),
        )
        self.assertEqual(response["code"], 200)

        got = get_preview_session_route(preview_session_id)
        session = got["data"]["preview_session"]

        blocks = session["working_spec_json"]["layout"]["blocks"]
        self.assertEqual(blocks[0]["chart"]["type"], "bar")
        self.assertEqual(blocks[1]["top_n"], 3)
        self.assertEqual(blocks[1]["chart"]["top_n"], 3)

        self.assertEqual(
            session["working_spec_json"]["metrics"]["dsl"]["revenue"],
            "lag(order_count,1)+amount",
        )
        self.assertEqual(
            session["working_spec_json"]["mapping_contract"]["fields"]["region"],
            "region",
        )
        self.assertEqual(session["working_spec_json"]["style_config"]["brand_color"], "#FF0000")
        self.assertEqual(len(session["patch_history_json"]), 5)

        logs = preview_service.list_audit_logs("preview.patch")
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]["detail"]["patch_count"], 5)

    def test_patch_validation_dsl_error_returns_e2001(self):
        preview_session_id = self._seed_session()

        response = patch_preview_session_route(
            preview_session_id,
            PatchPreviewSessionDTO(
                patches=[
                    {
                        "op": "update_metric",
                        "metric_name": "revenue",
                        "expression": "lag(",
                    }
                ]
            ),
        )
        self.assertEqual(response["code"], 400)
        self.assertEqual(response["error_code"], "E2001")

    def test_patch_validation_missing_field_returns_e1003(self):
        preview_session_id = self._seed_session()

        response = patch_preview_session_route(
            preview_session_id,
            PatchPreviewSessionDTO(
                patches=[
                    {
                        "op": "update_mapping",
                        "mappings": {"not_exist": "x"},
                    }
                ]
            ),
        )
        self.assertEqual(response["code"], 400)
        self.assertEqual(response["error_code"], "E1003")


if __name__ == "__main__":
    unittest.main()
