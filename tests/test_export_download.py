import unittest
from pathlib import Path

from reportstudio.scripts.export.export import export_from_input
from reportstudio.scripts.export.download import build_download_info


FIXTURE = Path("tests/fixtures/sales.csv")


class ExportDownloadTests(unittest.TestCase):
    def test_export_json_returns_downloadable_artifact(self):
        result = export_from_input(FIXTURE, metric_field="amount", dimension_field="region", fmt="json")
        self.assertEqual(result["status"], "exported")
        self.assertEqual(result["format"], "json")
        self.assertTrue(Path(result["artifact_file"]).exists())

    def test_export_xlsx(self):
        result = export_from_input(FIXTURE, metric_field="amount", dimension_field="region", fmt="xlsx")
        self.assertEqual(result["format"], "xlsx")
        artifact = Path(result["artifact_file"])
        self.assertTrue(artifact.exists())
        self.assertEqual(artifact.suffix, ".xlsx")

    def test_export_pdf(self):
        result = export_from_input(FIXTURE, metric_field="amount", dimension_field="region", fmt="pdf")
        self.assertEqual(result["format"], "pdf")
        artifact = Path(result["artifact_file"])
        self.assertTrue(artifact.exists())
        self.assertEqual(artifact.suffix, ".pdf")

    def test_download_info_reports_sha(self):
        result = export_from_input(FIXTURE, metric_field="amount", dimension_field="region", fmt="pdf")
        info = build_download_info(Path(result["artifact_file"]))
        self.assertEqual(info["status"], "ready")
        self.assertTrue(info["size"] > 0)
        self.assertEqual(len(info["sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
