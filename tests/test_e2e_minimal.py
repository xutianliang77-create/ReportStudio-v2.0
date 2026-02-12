import json
import subprocess
import unittest
from pathlib import Path


FIXTURE = Path("tests/fixtures/sales.csv")


class E2EMinimalTests(unittest.TestCase):
    def test_minimal_flow_create_render_download(self):
        create_out = subprocess.check_output(
            [
                "python3",
                "reportstudio/scripts/preview/serve.py",
                "--command",
                "create report",
                "--input",
                str(FIXTURE),
            ],
            text=True,
        )
        create_payload = json.loads(create_out)
        self.assertEqual(create_payload["code"], 200)

        render_out = subprocess.check_output(
            [
                "python3",
                "reportstudio/scripts/preview/serve.py",
                "--command",
                "render pdf",
                "--input",
                str(FIXTURE),
                "--format",
                "pdf",
            ],
            text=True,
        )
        render_payload = json.loads(render_out)
        self.assertEqual(render_payload["code"], 200)
        artifact = render_payload["data"]["render"]["artifact_file"]

        download_out = subprocess.check_output(
            [
                "python3",
                "reportstudio/scripts/preview/serve.py",
                "--command",
                "download artifact",
                "--file",
                artifact,
            ],
            text=True,
        )
        download_payload = json.loads(download_out)
        self.assertEqual(download_payload["code"], 200)
        self.assertEqual(download_payload["data"]["artifact"]["status"], "ready")


if __name__ == "__main__":
    unittest.main()
