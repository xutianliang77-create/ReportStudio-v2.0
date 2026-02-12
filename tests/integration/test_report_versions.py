import unittest

from reportstudio.api.routes.reports import (
    CommitReportVersionDTO,
    CreateReportDTO,
    commit_report_version_route,
    create_report_route,
    get_report_version_route,
    list_report_versions_route,
    update_report_spec_route,
)
from reportstudio.core.version import service


class ReportVersionsIntegrationTests(unittest.TestCase):
    def setUp(self):
        service._REPORTS.clear()
        service._REPORT_VERSIONS.clear()
        service._AUDIT_LOGS.clear()

    def test_create_report_commit_v1_modify_spec_commit_v2_and_list(self):
        created = create_report_route(
            CreateReportDTO(
                name="sales-report",
                spec={"layout": {"sections": ["summary"]}, "filters": {"year": 2025}},
            )
        )
        report_id = created["data"]["report"]["report_id"]

        v1 = commit_report_version_route(report_id, CommitReportVersionDTO())
        self.assertEqual(v1["code"], 200)
        v1_id = v1["data"]["version"]["version_id"]
        self.assertEqual(v1["data"]["version"]["version_no"], 1)
        self.assertEqual(v1["data"]["version"]["spec"]["filters"]["year"], 2025)

        update_report_spec_route(
            report_id,
            {"layout": {"sections": ["summary", "trend"]}, "filters": {"year": 2026}},
        )

        v2 = commit_report_version_route(report_id, CommitReportVersionDTO())
        self.assertEqual(v2["code"], 200)
        v2_id = v2["data"]["version"]["version_id"]
        self.assertEqual(v2["data"]["version"]["version_no"], 2)
        self.assertEqual(v2["data"]["version"]["spec"]["filters"]["year"], 2026)

        versions = list_report_versions_route(report_id)
        self.assertEqual(versions["code"], 200)
        self.assertEqual([x["version_no"] for x in versions["data"]["versions"]], [1, 2])

        fetched_v1 = get_report_version_route(report_id, v1_id)
        fetched_v2 = get_report_version_route(report_id, v2_id)
        self.assertEqual(fetched_v1["data"]["version"]["spec"]["filters"]["year"], 2025)
        self.assertEqual(fetched_v2["data"]["version"]["spec"]["filters"]["year"], 2026)

        logs = service.list_audit_logs("report.version.commit")
        self.assertEqual(len(logs), 2)


if __name__ == "__main__":
    unittest.main()
