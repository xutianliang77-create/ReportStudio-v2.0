import unittest

from reportstudio.core.metrics.cache import build_metric_cache_key, cache_clear
from reportstudio.core.metrics.compute import compute_metrics_with_cache


class MetricCacheIntegrationTests(unittest.TestCase):
    def setUp(self):
        cache_clear()

    def test_cache_hit_uses_same_key_and_emits_debug_log(self):
        counter = {"count": 0}

        def compute_fn() -> dict:
            counter["count"] += 1
            return {"sum": 100, "count": 2}

        dataset_id = "ds_sales"
        params = {"workspace_id": "ws_1", "secret": "token-123"}
        metric_expressions = {"m_sum": "sum(revenue)"}

        first = compute_metrics_with_cache(
            dataset_id=dataset_id,
            params=params,
            metric_expressions=metric_expressions,
            compute_fn=compute_fn,
        )
        with self.assertLogs("reportstudio.core.metrics.compute", level="DEBUG") as cm:
            second = compute_metrics_with_cache(
                dataset_id=dataset_id,
                params=params,
                metric_expressions=metric_expressions,
                compute_fn=compute_fn,
            )

        self.assertEqual(first, second)
        self.assertEqual(counter["count"], 1)

        key = build_metric_cache_key(dataset_id=dataset_id, params=params, metric_expressions=metric_expressions)
        log_text = "\n".join(cm.output)
        self.assertIn("metrics cache hit", log_text)
        self.assertIn(key.params_hash, log_text)
        self.assertIn(key.metric_expr_hash, log_text)
        self.assertNotIn("token-123", log_text)

    def test_cache_miss_when_metric_expr_changes(self):
        counter = {"count": 0}

        def compute_fn() -> dict:
            counter["count"] += 1
            return {"sum": counter["count"]}

        params = {"workspace_id": "ws_1"}
        compute_metrics_with_cache(
            dataset_id="ds_sales",
            params=params,
            metric_expressions={"m_sum": "sum(revenue)"},
            compute_fn=compute_fn,
        )
        compute_metrics_with_cache(
            dataset_id="ds_sales",
            params=params,
            metric_expressions={"m_sum": "sum(cost)"},
            compute_fn=compute_fn,
        )

        self.assertEqual(counter["count"], 2)


if __name__ == "__main__":
    unittest.main()
