import unittest

from reportstudio.core.preview.replay import replay_patches, spec_hash


class PatchReplayUnitTests(unittest.TestCase):
    def test_replay_is_deterministic_and_hash_stable(self):
        base_spec = {
            "dataset_fields": ["amount", "region", "order_count", "sales"],
            "metrics": {"dsl": {"revenue": "amount+1"}},
            "mapping_contract": {"fields": {"amount": "sales"}},
            "style_config": {"brand_color": "#111111"},
            "layout": {
                "blocks": [
                    {
                        "block_id": "b1",
                        "chart_name": "trend",
                        "top_n": 5,
                        "chart": {"name": "trend", "type": "line", "top_n": 5},
                    },
                    {
                        "block_id": "b2",
                        "chart_name": "table_sales",
                        "top_n": 10,
                        "chart": {"name": "table_sales", "type": "table", "top_n": 10},
                    },
                ]
            },
        }
        patch_history = [
            {
                "op": "replace_chart",
                "block_id": "b1",
                "new_chart": {"name": "trend", "type": "bar", "top_n": 7},
            },
            {
                "op": "update_metric",
                "metric_name": "revenue",
                "expression": "lag(order_count,1)+amount",
            },
            {
                "op": "set_topn",
                "chart_name": "table_sales",
                "top_n": 3,
            },
            {
                "op": "update_mapping",
                "mappings": {"amount": "sales", "region": "region"},
            },
            {
                "op": "set_style",
                "style": {
                    "brand_color": "#FF0000",
                    "font_family": "PingFang SC",
                    "header_text": "Monthly Report",
                    "footer_text": "Internal",
                },
            },
        ]

        replay1 = replay_patches(base_spec, patch_history)
        replay2 = replay_patches(base_spec, patch_history)

        self.assertEqual(replay1, replay2)
        self.assertEqual(spec_hash(replay1), spec_hash(replay2))


if __name__ == "__main__":
    unittest.main()
