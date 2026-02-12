import json
import unittest
import zipfile
from pathlib import Path

from reportstudio.api.routes.reports import CreateReportDTO, create_report_route
from reportstudio.api.routes.renders import export_render_docx
from reportstudio.core.render import job_service
from reportstudio.core.security import acl as acl_service


class DocxExportIntegrationTests(unittest.TestCase):
    def setUp(self):
        job_service._JOBS.clear()
        job_service._AUDIT_LOGS.clear()
        job_service._IDEMPOTENCY_INDEX.clear()
        acl_service._POLICIES.clear()
        acl_service._RESOURCE_OWNERS.clear()
        acl_service._AUDIT_LOGS.clear()

    def _prepare_intermediate(self, base: Path) -> None:
        (base / "images").mkdir(parents=True, exist_ok=True)
        (base / "kpis.json").write_text(json.dumps({"sum": 100, "avg": 10}, ensure_ascii=False), encoding="utf-8")
        (base / "tables.json").write_text(
            json.dumps({"rows": [{"region": "华东", "amount": 100}]}, ensure_ascii=False), encoding="utf-8"
        )
        (base / "glossary.json").write_text(
            json.dumps({"revenue": "sum(amount)"}, ensure_ascii=False), encoding="utf-8"
        )
        (base / "images" / "chart_1.png").write_bytes(b"\x89PNG\r\n\x1a\n")

    def test_export_docx_generated_and_contains_title(self):
        report = create_report_route(
            CreateReportDTO(name="docx report", spec={"input_path": "tests/fixtures/sales.csv"}),
            principal_id="owner_u1",
        )
        report_id = report["data"]["report"]["report_id"]

        render_id = "rj_docx_001"
        job_service._JOBS[render_id] = job_service.RenderJob(
            render_id=render_id,
            status="succeeded",
            input_path="tests/fixtures/sales.csv",
            fmt="docx",
            metric_field="amount",
            dimension_field="region",
            workspace_id="default-workspace",
            report_id=report_id,
            created_at="",
            updated_at="",
        )

        intermediate_dir = Path("reportstudio/data/intermediate/test_docx")
        self._prepare_intermediate(intermediate_dir)

        resp = export_render_docx(
            render_id,
            intermediate_dir=str(intermediate_dir),
            principal_id="owner_u1",
            title="Monthly Sales Report",
        )
        self.assertEqual(resp["code"], 200)

        artifact_file = Path(resp["data"]["artifact"]["file"])
        self.assertTrue(artifact_file.exists())
        self.assertGreater(artifact_file.stat().st_size, 0)

        with zipfile.ZipFile(artifact_file, "r") as zf:
            xml = zf.read("word/document.xml").decode("utf-8")
        self.assertIn("Monthly Sales Report", xml)

        logs = [x for x in job_service.list_audit_logs(render_id) if x["action"] == "export.docx"]
        self.assertGreaterEqual(len(logs), 1)
        self.assertEqual(logs[-1]["detail"]["status"], "succeeded")


if __name__ == "__main__":
    unittest.main()
