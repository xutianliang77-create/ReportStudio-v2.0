import json
import unittest
from pathlib import Path

from reportstudio.p1.ingest import ingest_file
from reportstudio.p1.metrics_analysis import compute_metrics, topn
from reportstudio.scripts.report.create import run_pipeline


FIXTURE = Path("tests/fixtures/sales.csv")


class P1PipelineTests(unittest.TestCase):
    def test_ingest_generates_schema_and_quality(self):
        ds = ingest_file(FIXTURE)
        self.assertEqual(ds.quality["total_rows"], 4)
        field_names = [f["name"] for f in ds.schema["fields"]]
        self.assertIn("amount", field_names)

    def test_metrics_and_topn(self):
        ds = ingest_file(FIXTURE)
        metrics = compute_metrics(ds.rows, "amount")
        self.assertEqual(metrics["sum"], 500.0)
        ranked = topn(ds.rows, "region", "amount", n=2)
        self.assertEqual(ranked[0]["region"], "East")


    def test_export_report_uses_unique_artifact_names(self):
        from reportstudio.p1.export_artifact import export_report

        out_dir = Path("reportstudio/data/artifacts")
        first = export_report({"layout": {}}, out_dir, report_name="dupcheck")
        second = export_report({"layout": {}}, out_dir, report_name="dupcheck")

        self.assertNotEqual(first["file"], second["file"])

    def test_e2e_run_pipeline(self):
        result = run_pipeline(FIXTURE, metric_field="amount", dimension_field="region")
        self.assertIn("artifact", result)
        artifact = Path(result["artifact"]["file"])
        self.assertTrue(artifact.exists())
        payload = json.loads(artifact.read_text(encoding="utf-8"))
        self.assertIn("layout", payload)


if __name__ == "__main__":
    unittest.main()
