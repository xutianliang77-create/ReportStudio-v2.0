import json
import tempfile
import unittest
from pathlib import Path

from reportstudio.p1.export_artifact import export_report


class ExportArtifactTests(unittest.TestCase):
    def test_export_report_uses_unique_artifact_filename_per_call(self):
        snapshot = {
            "trace_id": "trace-1",
            "metrics": {"sum": 1, "count": 1, "avg": 1},
            "topn": [{"region": "north", "amount": 1}],
            "delivery": {},
        }

        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            first = export_report(snapshot=snapshot, out_dir=out_dir, report_name="render", fmt="json")
            second = export_report(snapshot=snapshot, out_dir=out_dir, report_name="render", fmt="json")

            self.assertNotEqual(first["file"], second["file"])
            self.assertTrue(Path(first["file"]).exists())
            self.assertTrue(Path(second["file"]).exists())

            self.assertEqual(json.loads(Path(first["file"]).read_text(encoding="utf-8"))["trace_id"], "trace-1")
            self.assertEqual(json.loads(Path(second["file"]).read_text(encoding="utf-8"))["trace_id"], "trace-1")

    def test_export_report_includes_artifact_id_and_keeps_paths_unique(self):
        snapshot = {
            "trace_id": "trace-2",
            "metrics": {"sum": 2, "count": 1, "avg": 2},
            "topn": [{"region": "south", "amount": 2}],
            "delivery": {},
        }

        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            first = export_report(
                snapshot=snapshot,
                out_dir=out_dir,
                report_name="render",
                fmt="json",
                artifact_id="rid-123",
            )
            second = export_report(
                snapshot=snapshot,
                out_dir=out_dir,
                report_name="render",
                fmt="json",
                artifact_id="rid-123",
            )

            self.assertIn("rid-123", Path(first["file"]).name)
            self.assertIn("rid-123", Path(second["file"]).name)
            self.assertNotEqual(first["file"], second["file"])


if __name__ == "__main__":
    unittest.main()
