import unittest

from reportstudio.api.routes.renders import create_render
from reportstudio.core.render import job_service
from reportstudio.workers.render_worker import process_next_local_job


class RenderIdempotencyTests(unittest.TestCase):
    def setUp(self):
        while process_next_local_job() is not None:
            pass
        job_service._JOBS.clear()
        job_service._AUDIT_LOGS.clear()
        job_service._IDEMPOTENCY_INDEX.clear()

    def test_same_request_id_returns_same_job_and_single_queue_enqueue(self):
        first = create_render(
            input_path="tests/fixtures/sales.csv",
            fmt="pdf",
            workspace_id="ws_1",
            report_id="rp_1",
            render_request_id="req_001",
        )
        second = create_render(
            input_path="tests/fixtures/sales.csv",
            fmt="pdf",
            workspace_id="ws_1",
            report_id="rp_1",
            render_request_id="req_001",
        )

        first_id = first["data"]["render"]["render_id"]
        second_id = second["data"]["render"]["render_id"]
        self.assertEqual(first_id, second_id)
        self.assertEqual(len(job_service._JOBS), 1)

        processed = process_next_local_job()
        self.assertIsNotNone(processed)
        self.assertEqual(processed["render_id"], first_id)
        self.assertIsNone(process_next_local_job())

        logs = job_service.list_audit_logs(first_id)
        actions = [x["action"] for x in logs]
        self.assertIn("render.idempotent_hit", actions)

    def test_header_render_request_id_is_supported(self):
        first = create_render(
            input_path="tests/fixtures/sales.csv",
            fmt="pdf",
            workspace_id="ws_header",
            report_id="rp_header",
            headers={"x-render-request-id": "req_header_1"},
        )
        second = create_render(
            input_path="tests/fixtures/sales.csv",
            fmt="pdf",
            workspace_id="ws_header",
            report_id="rp_header",
            headers={"render_request_id": "req_header_1"},
        )

        self.assertEqual(first["data"]["render"]["render_id"], second["data"]["render"]["render_id"])


if __name__ == "__main__":
    unittest.main()
