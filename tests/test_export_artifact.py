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


if __name__ == "__main__":
    unittest.main()
