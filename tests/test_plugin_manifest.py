import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


class PluginManifestTest(unittest.TestCase):
    def test_public_mcp_and_optional_apps_do_not_gate_installation(self):
        self.assertTrue((ROOT / 'plugins/101/.mcp.json').is_file())
        self.assertEqual(
            read_json('plugins/101/.mcp.json'),
            {
                'mcpServers': {
                    '101': {
                        'type': 'http',
                        'url': 'https://app.101-group.ru/mcp',
                        'oauth_resource': 'https://app.101-group.ru/mcp',
                    },
                },
            },
        )
        self.assertEqual(
            read_json('plugins/101/.app.json'),
            {
                'apps': {
                    'google_drive': {
                        'id': 'connector_5f3c8c41a1e54ad7a76272c89e2554fa',
                        'required': False,
                    },
                    'notion': {
                        'id': 'asdk_app_69c18c28f1188191bf5b8445c4ab0a2e',
                        'required': False,
                    },
                },
            },
        )

    def test_public_marketplace_authenticates_on_first_use(self):
        marketplace = read_json('.agents/plugins/marketplace.json')
        plugin = marketplace['plugins'][0]

        self.assertEqual(marketplace['name'], '101-marketplace')
        self.assertEqual(
            marketplace['interface']['displayName'],
            '101 Marketplace',
        )
        self.assertEqual(plugin['name'], '101')
        self.assertEqual(
            plugin['policy'],
            {
                'installation': 'AVAILABLE',
                'authentication': 'ON_USE',
            },
        )

    def test_public_plugin_manifest_exposes_release_components(self):
        manifest = read_json('plugins/101/.codex-plugin/plugin.json')

        self.assertEqual(manifest['name'], '101')
        self.assertEqual(manifest['version'], '2.0.6')
        self.assertEqual(manifest['mcpServers'], './.mcp.json')
        self.assertEqual(manifest['apps'], './.app.json')
        self.assertEqual(manifest['interface']['displayName'], '101')
        self.assertLessEqual(len(manifest['interface']['defaultPrompt']), 3)
        self.assertNotIn('private', manifest['description'].lower())
        self.assertNotIn(
            'private',
            manifest['interface']['longDescription'].lower(),
        )

    def test_patch_release_is_declared_consistently(self):
        manifest = read_json('plugins/101/.codex-plugin/plugin.json')
        readme = (ROOT / 'README.md').read_text(encoding='utf-8')

        self.assertEqual(manifest['version'], '2.0.6')
        self.assertIn('Текущая версия плагина для Codex: `2.0.6`.', readme)

    def test_bundled_analytics_runtime_matches_its_immutable_release_lock(self):
        widget_root = ROOT / 'plugins/101/widgets/analytics/v2'
        manifest = read_json('plugins/101/widgets/analytics/v2/manifest.json')

        self.assertEqual(
            manifest['sourceCommit'],
            'e8aa60b5555a72dc4beec58f53277bfcc1e97d99',
        )
        self.assertEqual(
            manifest['releaseId'],
            '4cb582b0b836f8af15dbf2cc3ebac684d7cdb9dea7bd8378249d1eccd426acf9',
        )
        for resource in manifest['resources']:
            content = (widget_root / resource['file']).read_bytes()
            self.assertEqual(len(content), resource['bytes'])
            self.assertEqual(hashlib.sha256(content).hexdigest(), resource['sha256'])


if __name__ == '__main__':
    unittest.main()
