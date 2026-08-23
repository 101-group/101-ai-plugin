import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


class PluginManifestTest(unittest.TestCase):
    def test_required_101_app_matches_the_production_dependency(self):
        app_manifest = read_json('plugins/101/.app.json')

        self.assertEqual(
            app_manifest,
            {
                'apps': {
                    '101-v2': {
                        'id': 'asdk_app_6a8a2c8be2088191b622c8c0fd50d4e8',
                        'required': True,
                    },
                },
            },
        )

    def test_marketplace_requires_authentication_during_install(self):
        marketplace = read_json('.agents/plugins/marketplace.json')
        plugin = next(
            item for item in marketplace['plugins'] if item['name'] == '101'
        )

        self.assertEqual(plugin['policy']['authentication'], 'ON_INSTALL')

    def test_patch_release_is_declared_consistently(self):
        manifest = read_json('plugins/101/.codex-plugin/plugin.json')
        readme = (ROOT / 'README.md').read_text(encoding='utf-8')

        self.assertEqual(manifest['version'], '2.0.2')
        self.assertIn('Текущая версия плагина для Codex: `2.0.2`.', readme)


if __name__ == '__main__':
    unittest.main()
