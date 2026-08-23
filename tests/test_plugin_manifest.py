import hashlib
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

        self.assertEqual(manifest['version'], '2.0.4')
        self.assertIn('Текущая версия плагина для Codex: `2.0.4`.', readme)

    def test_bundled_analytics_runtime_matches_its_immutable_release_lock(self):
        widget_root = ROOT / 'plugins/101/widgets/analytics/v2'
        manifest = read_json('plugins/101/widgets/analytics/v2/manifest.json')

        self.assertEqual(
            manifest['sourceCommit'],
            'eda7eb007001aa3d7f2b025743bb836b1031d8d9',
        )
        for resource in manifest['resources']:
            content = (widget_root / resource['file']).read_bytes()
            self.assertEqual(len(content), resource['bytes'])
            self.assertEqual(hashlib.sha256(content).hexdigest(), resource['sha256'])


if __name__ == '__main__':
    unittest.main()
