import unittest
from pathlib import Path

from reportstudio.core.render import job_service
from reportstudio.core.render.pipeline import export_tables_payload, preview_tables_payload, write_tables_json


class MaskingConsistencyIntegrationTests(unittest.TestCase):
    def setUp(self):
        job_service._AUDIT_LOGS.clear()

    def test_preview_and_export_are_masked_consistently(self):
        rows = [
            {
                "phone": "13812345678",
                "email": "alice@example.com",
                "id_no": "110101199001011234",
                "address": "上海市浦东新区世纪大道100号",
                "region": "华东",
            }
        ]

        preview = preview_tables_payload(rows=rows, render_id="rj_mask_1", masking_level="standard")
        export = export_tables_payload(rows=rows, render_id="rj_mask_1", masking_level="standard")

        self.assertEqual(preview["rows"], export["rows"])
        masked = preview["rows"][0]
        self.assertNotEqual(masked["phone"], rows[0]["phone"])
        self.assertNotEqual(masked["email"], rows[0]["email"])
        self.assertNotEqual(masked["id_no"], rows[0]["id_no"])
        self.assertNotEqual(masked["address"], rows[0]["address"])

        tables_path = Path("reportstudio/data/artifacts/test_tables_masking.json")
        written = write_tables_json(rows=rows, render_id="rj_mask_1", out_file=tables_path, masking_level="standard")
        self.assertEqual(written["rows"], preview["rows"])

        logs = [x for x in job_service.list_audit_logs("rj_mask_1") if x["action"] == "masking.applied"]
        self.assertGreaterEqual(len(logs), 1)
        fields = logs[-1]["detail"]["fields"]
        self.assertTrue(any(item["field"] == "phone" and item["rule"] == "phone" for item in fields))

        # ensure logs do not contain raw sensitive values
        self.assertNotIn("13812345678", str(logs[-1]))
        self.assertNotIn("alice@example.com", str(logs[-1]))


if __name__ == "__main__":
    unittest.main()
