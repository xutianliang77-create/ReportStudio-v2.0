import unittest

from reportstudio.api.routes.renders import create_render


class RenderValidationTests(unittest.TestCase):
    def test_create_render_rejects_docx_until_worker_supports_it(self):
        resp = create_render(input_path="tests/fixtures/sales.csv", fmt="docx")
        self.assertEqual(resp["code"], 400)
        self.assertEqual(resp["error_code"], "E3003")


if __name__ == "__main__":
    unittest.main()
