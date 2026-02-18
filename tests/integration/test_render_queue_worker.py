import unittest

from reportstudio.api.routes.renders import create_render, get_render
from reportstudio.core.render.job_service import list_audit_logs
from reportstudio.workers.render_worker import process_next_local_job


class RenderQueueWorkerTests(unittest.TestCase):
    def test_async_render_job_success(self):
        created = create_render(input_path="tests/fixtures/sales.csv", fmt="pdf")
        self.assertEqual(created["code"], 200)
        self.assertEqual(created["data"]["render"]["status"], "queued")

        render_id = created["data"]["render"]["render_id"]
        processed = process_next_local_job()
        self.assertIsNotNone(processed)
        self.assertEqual(processed["render_id"], render_id)
        self.assertEqual(processed["status"], "succeeded")

        status = get_render(render_id)
        self.assertEqual(status["data"]["render"]["status"], "succeeded")
        artifact_file = status["data"]["render"]["artifact_file"]
        self.assertTrue(artifact_file.endswith(".pdf"))
        self.assertIn(render_id, artifact_file)

    def test_async_render_job_failed_writes_error_and_audit(self):
        created = create_render(input_path="tests/fixtures/not_found.csv", fmt="xlsx")
        render_id = created["data"]["render"]["render_id"]

        processed = process_next_local_job()
        self.assertIsNotNone(processed)
        self.assertEqual(processed["status"], "failed")
        self.assertEqual(processed["error_code"], "RENDER_FAILED")

        status = get_render(render_id)
        self.assertEqual(status["data"]["render"]["status"], "failed")
        self.assertEqual(status["data"]["render"]["error_code"], "RENDER_FAILED")
        self.assertTrue(bool(status["data"]["render"]["error_message"]))

        logs = list_audit_logs(render_id)
        actions = [x["action"] for x in logs]
        self.assertIn("failed", actions)


if __name__ == "__main__":
    unittest.main()
