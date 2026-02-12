import unittest

from reportstudio.api.routes.preview_sessions import (
    CreatePreviewSessionDTO,
    create_preview_session_route,
    get_preview_session_route,
    render_preview_session_route,
)
from reportstudio.api.routes.reports import CommitReportVersionDTO, CreateReportDTO, commit_report_version_route, create_report_route
from reportstudio.api.routes.renders import get_render
from reportstudio.core.preview import service as preview_service
from reportstudio.core.version import service as version_service
from reportstudio.workers.render_worker import process_next_local_job


class PreviewSessionApiIntegrationTests(unittest.TestCase):
    def setUp(self):
        version_service._REPORTS.clear()
        version_service._REPORT_VERSIONS.clear()
        version_service._AUDIT_LOGS.clear()
        preview_service._PREVIEW_SESSIONS.clear()
        preview_service._AUDIT_LOGS.clear()
        while process_next_local_job() is not None:
            pass

    def test_create_get_render_and_poll_success(self):
        report = create_report_route(
            CreateReportDTO(
                name="preview-report",
                spec={
                    "input_path": "tests/fixtures/sales.csv",
                    "format": "pdf",
                    "metric_field": "amount",
                    "dimension_field": "region",
                },
            )
        )
        report_id = report["data"]["report"]["report_id"]
        committed = commit_report_version_route(report_id, CommitReportVersionDTO())
        base_version_id = committed["data"]["version"]["version_id"]

        created = create_preview_session_route(
            CreatePreviewSessionDTO(report_id=report_id, base_version_id=base_version_id)
        )
        self.assertEqual(created["code"], 200)
        preview_session_id = created["data"]["preview_session"]["preview_session_id"]

        got = get_preview_session_route(preview_session_id)
        self.assertEqual(got["code"], 200)
        self.assertEqual(got["data"]["preview_session"]["base_spec_version"], base_version_id)

        queued = render_preview_session_route(preview_session_id)
        self.assertEqual(queued["code"], 200)
        render_id = queued["data"]["render"]["render_id"]

        processed = process_next_local_job()
        self.assertIsNotNone(processed)
        self.assertEqual(processed["render_id"], render_id)
        self.assertEqual(processed["status"], "succeeded")

        final = get_render(render_id)
        self.assertEqual(final["data"]["render"]["status"], "succeeded")

        actions = [x["action"] for x in preview_service.list_audit_logs()]
        self.assertIn("preview.session.create", actions)
        self.assertIn("preview.render", actions)


if __name__ == "__main__":
    unittest.main()
