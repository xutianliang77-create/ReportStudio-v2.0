import unittest

from reportstudio.api.routes.renders import create_render, get_render
from reportstudio.core.render.job_service import list_audit_logs
from reportstudio.workers.render_worker import process_next_local_job


class RenderProgressTests(unittest.TestCase):
    def test_progress_monotonic_and_stage_order(self):
        created = create_render(input_path="tests/fixtures/sales.csv", fmt="pdf")
        render_id = created["data"]["render"]["render_id"]

        processed = process_next_local_job()
        self.assertIsNotNone(processed)
        self.assertEqual(processed["status"], "succeeded")

        status = get_render(render_id)
        render = status["data"]["render"]
        self.assertEqual(render["status"], "succeeded")
        self.assertEqual(render["progress"], 100)
        self.assertEqual(render["stage"], "upload")

        logs = list_audit_logs(render_id)
        progress_logs = [x for x in logs if x["action"] == "progress"]
        progress_values = [x["detail"]["progress"] for x in progress_logs]
        self.assertEqual(progress_values, sorted(progress_values))

        stages = [x["detail"]["stage"] for x in progress_logs]
        expected = ["compute", "plot", "export", "upload"]
        self.assertEqual(stages, expected)

    def test_failed_job_keeps_progress_and_sets_error(self):
        created = create_render(input_path="tests/fixtures/not_found.csv", fmt="pdf")
        render_id = created["data"]["render"]["render_id"]

        processed = process_next_local_job()
        self.assertIsNotNone(processed)
        self.assertEqual(processed["status"], "failed")

        status = get_render(render_id)["data"]["render"]
        self.assertEqual(status["status"], "failed")
        self.assertEqual(status["error_code"], "RENDER_FAILED")
        self.assertTrue(bool(status["error_message"]))
        # failed时 progress 停止（不重置）
        self.assertGreaterEqual(status["progress"], 10)
        self.assertLessEqual(status["progress"], 100)


if __name__ == "__main__":
    unittest.main()
