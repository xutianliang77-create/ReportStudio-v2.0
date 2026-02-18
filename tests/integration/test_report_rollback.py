import unittest

from reportstudio.api.routes.reports import (
    CommitReportVersionDTO,
    CreateReportDTO,
    commit_report_version_route,
    create_report_route,
    rerender_report_route,
    rollback_report_route,
    update_report_spec_route,
)
from reportstudio.core.version import service


class ReportRollbackIntegrationTests(unittest.TestCase):
    def setUp(self):
        service._REPORTS.clear()
        service._REPORT_VERSIONS.clear()
        service._AUDIT_LOGS.clear()

    def test_rollback_switches_current_version_and_rerender_uses_old_spec(self):
        created = create_report_route(
            CreateReportDTO(
                name="ops-report",
                spec={"layout": {"sections": ["summary"]}, "filters": {"year": 2024}},
            )
        )
        report_id = created["data"]["report"]["report_id"]

        v1 = commit_report_version_route(report_id, CommitReportVersionDTO())
        v1_id = v1["data"]["version"]["version_id"]

        update_report_spec_route(
            report_id,
            {"layout": {"sections": ["summary", "trend"]}, "filters": {"year": 2025}},
        )
        v2 = commit_report_version_route(report_id, CommitReportVersionDTO())
        v2_id = v2["data"]["version"]["version_id"]

        before = rerender_report_route(report_id)
        before_hash = before["data"]["render"]["spec_hash"]
        self.assertEqual(before["data"]["render"]["current_spec_version_id"], v2_id)

        rolled = rollback_report_route(report_id, version_id=v1_id)
        self.assertEqual(rolled["code"], 200)
        self.assertEqual(rolled["data"]["report"]["current_spec_version_id"], v1_id)

        after = rerender_report_route(report_id)
        after_hash = after["data"]["render"]["spec_hash"]

        self.assertNotEqual(before_hash, after_hash)
        self.assertEqual(after["data"]["render"]["current_spec_version_id"], v1_id)

        logs = service.list_audit_logs("report.rollback")
        self.assertEqual(len(logs), 1)
        detail = logs[0]["detail"]
        self.assertEqual(detail["from_version_id"], v2_id)
        self.assertEqual(detail["to_version_id"], v1_id)


if __name__ == "__main__":
    unittest.main()
