import unittest

from reportstudio.p1.command_parser import parse_command


class CommandParserTests(unittest.TestCase):
    def test_parse_create_report(self):
        parsed = parse_command("create report")
        self.assertEqual(parsed.intent, "report.create")
        self.assertEqual(parsed.endpoint, "reports.create")

    def test_parse_render_pdf(self):
        parsed = parse_command("render pdf")
        self.assertEqual(parsed.intent, "report.export")
        self.assertEqual(parsed.endpoint, "renders.create")

    def test_parse_download_artifact(self):
        parsed = parse_command("download artifact")
        self.assertEqual(parsed.intent, "report.download")
        self.assertEqual(parsed.endpoint, "artifacts.get")

    def test_invalid_command_raises(self):
        with self.assertRaises(ValueError):
            parse_command("show dashboard")


if __name__ == "__main__":
    unittest.main()
