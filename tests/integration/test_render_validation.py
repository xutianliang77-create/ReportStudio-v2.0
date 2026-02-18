import unittest

from reportstudio.api.routes.renders import create_render
from reportstudio.core.render import job_service


class RenderValidationTests(unittest.TestCase):
    def test_create_render_rejects_docx_until_worker_supports_it(self):
        before_jobs = len(job_service._JOBS)
        resp = create_render(input_path="tests/fixtures/sales.csv", fmt="docx")
        self.assertEqual(resp["code"], 400)
        self.assertEqual(resp["error_code"], "E3003")

        after_jobs = len(job_service._JOBS)
        self.assertEqual(after_jobs, before_jobs)


if __name__ == "__main__":
    unittest.main()
