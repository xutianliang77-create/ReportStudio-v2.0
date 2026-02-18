import unittest

from reportstudio.api.routes.renders import cancel_render, create_render, get_render, retry_render
from reportstudio.core.render import job_service
from reportstudio.workers.render_worker import process_next_local_job


class RenderCancelRetryTests(unittest.TestCase):
    def setUp(self):
        while process_next_local_job() is not None:
            pass
        job_service._JOBS.clear()
        job_service._AUDIT_LOGS.clear()
        job_service._IDEMPOTENCY_INDEX.clear()

    def test_cancel_queued_job_will_not_execute(self):
        created = create_render(input_path="tests/fixtures/sales.csv", fmt="pdf")
        render_id = created["data"]["render"]["render_id"]

        canceled = cancel_render(render_id, principal_id="owner")
        self.assertEqual(canceled["data"]["render"]["status"], "canceled")

        processed = process_next_local_job()
        self.assertIsNotNone(processed)
        self.assertEqual(processed["render_id"], render_id)
        self.assertEqual(processed["status"], "canceled")

        status = get_render(render_id)["data"]["render"]
        self.assertEqual(status["status"], "canceled")

        logs = job_service.list_audit_logs(render_id)
        actions = [x["action"] for x in logs]
        self.assertIn("render.cancel", actions)
        self.assertIn("render.skip_canceled", actions)

    def test_retry_failed_job_can_succeed_and_is_traceable(self):
        created = create_render(input_path="tests/fixtures/not_found.csv", fmt="pdf")
        failed_id = created["data"]["render"]["render_id"]

        first_run = process_next_local_job()
        self.assertIsNotNone(first_run)
        self.assertEqual(first_run["status"], "failed")

        retried = retry_render(failed_id, input_path="tests/fixtures/sales.csv")
        retry_id = retried["data"]["render"]["render_id"]
        self.assertNotEqual(failed_id, retry_id)
        self.assertEqual(retried["data"]["render"]["source_render_id"], failed_id)
        self.assertEqual(retried["data"]["render"]["attempt"], 2)

        second_run = process_next_local_job()
        self.assertIsNotNone(second_run)
        self.assertEqual(second_run["render_id"], retry_id)
        self.assertEqual(second_run["status"], "succeeded")

        retry_status = get_render(retry_id)["data"]["render"]
        self.assertEqual(retry_status["status"], "succeeded")
        self.assertEqual(retry_status["source_render_id"], failed_id)
        self.assertEqual(retry_status["attempt"], 2)

        retry_logs = job_service.list_audit_logs(retry_id)
        retry_actions = [x["action"] for x in retry_logs]
        self.assertIn("render.retry", retry_actions)


if __name__ == "__main__":
    unittest.main()
