import unittest

from reportstudio.api.routes.templates import (
    CreateTemplateDTO,
    CreateTemplateVersionDTO,
    TemplateSpecDTO,
    create_template_route,
    create_template_version_route,
    get_template_route,
    list_template_versions_route,
)
from reportstudio.core.template import service


class TemplateApiIntegrationTests(unittest.TestCase):
    def setUp(self):
        service._TEMPLATES.clear()
        service._TEMPLATE_VERSIONS.clear()
        service._AUDIT_LOGS.clear()

    def _spec(self, color: str) -> TemplateSpecDTO:
        return TemplateSpecDTO(
            layout={"sections": [{"id": "summary"}]},
            mapping_contract={"metrics": [{"name": "revenue"}]},
            style_config={"theme": color},
            export_preset={"formats": ["pdf", "xlsx"]},
        )

    def test_template_create_get_create_v2_and_list_versions(self):
        created = create_template_route(CreateTemplateDTO(name="finance-template", description="base", spec=self._spec("blue")))
        self.assertEqual(created["code"], 200)
        template_id = created["data"]["template"]["template_id"]
        self.assertEqual(created["data"]["version"]["version"], 1)

        fetched = get_template_route(template_id)
        self.assertEqual(fetched["data"]["template"]["latest_version"], 1)
        self.assertEqual(fetched["data"]["template"]["latest_spec"]["style_config"]["theme"], "blue")

        v2 = create_template_version_route(
            template_id,
            CreateTemplateVersionDTO(spec=self._spec("green"), changelog="update style"),
        )
        self.assertEqual(v2["code"], 200)
        self.assertEqual(v2["data"]["version"]["version"], 2)
        self.assertEqual(v2["data"]["version"]["changelog"], "update style")

        versions = list_template_versions_route(template_id)
        self.assertEqual(versions["code"], 200)
        self.assertEqual([v["version"] for v in versions["data"]["versions"]], [1, 2])

        logs = service.list_audit_logs()
        actions = [x["action"] for x in logs]
        self.assertIn("template.create", actions)
        self.assertIn("template.version.create", actions)


if __name__ == "__main__":
    unittest.main()
