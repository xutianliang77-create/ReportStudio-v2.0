import unittest

from reportstudio.api.routes.acl import UpsertACLPolicyDTO, upsert_acl_policy_route
from reportstudio.api.routes.artifacts import sign_artifact_route
from reportstudio.api.routes.renders import cancel_render, create_render
from reportstudio.api.routes.reports import CreateReportDTO, create_report_route, get_report_route
from reportstudio.api.routes.templates import CreateTemplateDTO, TemplateSpecDTO, create_template_route, get_template_route
from reportstudio.core.security import acl as acl_service
from reportstudio.core.version import service as version_service
from reportstudio.workers.render_worker import process_next_local_job


class ACLEnforcementIntegrationTests(unittest.TestCase):
    def setUp(self):
        version_service._REPORTS.clear()
        version_service._REPORT_VERSIONS.clear()
        version_service._AUDIT_LOGS.clear()
        acl_service._POLICIES.clear()
        acl_service._RESOURCE_OWNERS.clear()
        acl_service._AUDIT_LOGS.clear()
        while process_next_local_job() is not None:
            pass

    def test_sign_artifact_without_export_permission_returns_e4002(self):
        report = create_report_route(
            CreateReportDTO(name="acl-report", spec={"input_path": "tests/fixtures/sales.csv"}),
            principal_id="owner_u1",
        )
        report_id = report["data"]["report"]["report_id"]

        render_created = create_render(
            input_path="tests/fixtures/sales.csv",
            fmt="pdf",
            report_id=report_id,
            principal_id="owner_u1",
        )
        render_id = render_created["data"]["render"]["render_id"]

        process_next_local_job()

        denied = sign_artifact_route(render_id, principal_id="user_u2")
        self.assertEqual(denied["code"], 403)
        self.assertEqual(denied["error_code"], "E4002")

        deny_logs = acl_service.list_audit_logs("acl.deny")
        self.assertGreaterEqual(len(deny_logs), 1)

    def test_cancel_render_without_permission_returns_e4002(self):
        report = create_report_route(
            CreateReportDTO(name="acl-cancel", spec={"input_path": "tests/fixtures/sales.csv"}),
            principal_id="owner_u1",
        )
        report_id = report["data"]["report"]["report_id"]

        created = create_render(
            input_path="tests/fixtures/sales.csv",
            fmt="pdf",
            report_id=report_id,
            principal_id="owner_u1",
        )
        render_id = created["data"]["render"]["render_id"]

        denied = cancel_render(render_id, principal_id="user_u2")
        self.assertEqual(denied["code"], 403)
        self.assertEqual(denied["error_code"], "E4002")

    def test_cancel_render_missing_principal_returns_e4001(self):
        report = create_report_route(
            CreateReportDTO(name="acl-cancel-missing-principal", spec={"input_path": "tests/fixtures/sales.csv"}),
            principal_id="owner_u1",
        )
        report_id = report["data"]["report"]["report_id"]

        created = create_render(
            input_path="tests/fixtures/sales.csv",
            fmt="pdf",
            report_id=report_id,
            principal_id="owner_u1",
        )
        render_id = created["data"]["render"]["render_id"]

        denied = cancel_render(render_id)
        self.assertEqual(denied["code"], 403)
        self.assertEqual(denied["error_code"], "E4001")

    def test_acl_allows_view_and_manage_when_policy_granted(self):
        report = create_report_route(
            CreateReportDTO(name="acl-view", spec={"input_path": "tests/fixtures/sales.csv"}),
            principal_id="owner_u1",
        )
        report_id = report["data"]["report"]["report_id"]

        upsert_acl_policy_route(
            UpsertACLPolicyDTO(
                resource_type="report",
                resource_id=report_id,
                principal_type="user",
                principal_id="user_u2",
                actions_json=["view"],
            )
        )

        got = get_report_route(report_id, principal_id="user_u2")
        self.assertEqual(got["code"], 200)

        tpl = create_template_route(
            CreateTemplateDTO(
                name="tpl",
                spec=TemplateSpecDTO(layout={}, mapping_contract={}, style_config={}, export_preset={}),
            ),
            principal_id="owner_u1",
        )
        template_id = tpl["data"]["template"]["template_id"]

        denied_tpl = get_template_route(template_id, principal_id="user_u2")
        self.assertEqual(denied_tpl["error_code"], "E4002")

        upsert_acl_policy_route(
            UpsertACLPolicyDTO(
                resource_type="template",
                resource_id=template_id,
                principal_type="user",
                principal_id="user_u2",
                actions_json=["manage"],
            )
        )
        allowed_tpl = get_template_route(template_id, principal_id="user_u2")
        self.assertEqual(allowed_tpl["code"], 200)


if __name__ == "__main__":
    unittest.main()
