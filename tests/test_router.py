import unittest

from reportstudio.router import UnknownIntentError, load_routes, resolve_intent


class RouterTests(unittest.TestCase):
    def test_load_routes_has_expected_core_intents(self):
        routes = load_routes()
        self.assertIn("report.create", routes)
        self.assertIn("report.export", routes)
        self.assertIn("report.download", routes)
        self.assertIn("report.lineage.trace", routes)

    def test_resolve_intent_returns_expected_script(self):
        route = resolve_intent("report.create")
        self.assertEqual(route.script, "scripts/report/create.py")
        self.assertEqual(route.module, "Report Pipeline")

    def test_unknown_intent_raises(self):
        with self.assertRaises(UnknownIntentError):
            resolve_intent("report.not-exist")


if __name__ == "__main__":
    unittest.main()
