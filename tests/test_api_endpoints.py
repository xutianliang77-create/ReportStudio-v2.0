import unittest
from pathlib import Path

from reportstudio.p1.api import create_report, render_report, get_artifact


FIXTURE = Path("tests/fixtures/sales.csv")


class ApiEndpointTests(unittest.TestCase):
    def test_reports_create(self):
        resp = create_report(FIXTURE)
        self.assertEqual(resp.code, 200)
        self.assertIn("report_id", resp.data)
        self.assertIn("metrics", resp.data)

    def test_renders_create_pdf(self):
        resp = render_report(FIXTURE, fmt="pdf")
        self.assertEqual(resp.code, 200)
        artifact_path = Path(resp.data["render"]["artifact_file"])
        self.assertTrue(artifact_path.exists())
        self.assertEqual(artifact_path.suffix, ".pdf")

    def test_artifacts_get(self):
        render = render_report(FIXTURE, fmt="xlsx")
        file_path = Path(render.data["render"]["artifact_file"])
        resp = get_artifact(file_path)
        self.assertEqual(resp.code, 200)
        self.assertEqual(resp.data["artifact"]["status"], "ready")
        self.assertEqual(len(resp.data["artifact"]["sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
