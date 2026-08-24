import copy
import json
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / 'plugins/101/skills'
ANALYTICS = SKILLS / 'analytics-visualization'
CHART_EXAMPLE = ANALYTICS / 'references/chart-payload-example.json'
ARTIFACT_EXAMPLE = ANALYTICS / 'references/artifact-payload-example.json'
ROUTING_CONTRACT = SKILLS / '101-index/references/presentation-routing.json'
COMPANION_ROUTING = SKILLS / '101-index/references/companion-routing.json'
ERROR_RECOVERY = SKILLS / '101-index/references/error-recovery.json'


MANIFEST_ALLOWED = {
    'version',
    'surface',
    'title',
    'generatedAt',
    'blocks',
    'description',
    'filters',
    'cards',
    'charts',
    'tables',
    'sources',
}
SNAPSHOT_ALLOWED = {
    'version',
    'generatedAt',
    'status',
    'datasets',
    'accessIssues',
}
BLOCK_ALLOWED = {'id', 'type', 'body', 'layout', 'cardIds', 'chartId', 'tableId', 'sourceId'}
CARD_ALLOWED = {'id', 'dataset', 'metrics', 'description', 'sourceId', 'filter'}
CARD_METRIC_ALLOWED = {'label', 'field', 'format', 'signed'}
CHART_ALLOWED = {
    'id', 'title', 'type', 'dataset', 'subtitle', 'showDescription',
    'headerMarkdown', 'intent', 'question', 'rationale', 'comparisonContext',
    'encodings', 'xAxisTitle', 'yAxisTitle', 'valueFormat', 'unit', 'layout',
    'combinationRationale', 'maxRows', 'referenceLines', 'emptyState',
    'compatibleTypes', 'surface', 'sourceId',
}
ENCODING_ROLES = {'x', 'y', 'color', 'lineStyle', 'size', 'facet', 'label', 'tooltip'}
ENCODING_ALLOWED = {
    'field', 'fields', 'type', 'aggregate', 'format', 'label', 'unit', 'time_unit',
}
TABLE_ALLOWED = {
    'id', 'title', 'dataset', 'columns', 'subtitle', 'showDescription',
    'headerMarkdown', 'defaultSort', 'density', 'sourceId', 'layout',
}
TABLE_COLUMN_ALLOWED = {'field', 'label', 'format', 'movement', 'role', 'semantic', 'type', 'unit'}
SOURCE_ALLOWED = {'engine', 'language', 'tool', 'executedAt', 'description', 'filters', 'metrics'}
SOURCE_METRIC_ALLOWED = {'id', 'definition'}
STANDALONE_ALLOWED = {'title', 'source', 'table', 'chart', 'display'}
STANDALONE_ENCODING_ALLOWED = {'field', 'type', 'aggregate', 'time_unit'}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def assert_allowed_keys(value: dict, allowed: set[str], path: str) -> None:
    extra = set(value) - allowed
    if extra:
        raise ValueError(f'{path}.{sorted(extra)[0]} is not allowed')


def validate_artifact_example(payload: dict) -> None:
    assert_allowed_keys(payload, {'surface', 'manifest', 'snapshot'}, 'payload')
    manifest = payload['manifest']
    snapshot = payload['snapshot']
    assert_allowed_keys(manifest, MANIFEST_ALLOWED, 'manifest')
    assert_allowed_keys(snapshot, SNAPSHOT_ALLOWED, 'snapshot')

    if payload['surface'] != 'report' or manifest['surface'] != 'report':
        raise ValueError('surface must be report')
    if manifest['version'] != 1 or snapshot['version'] != 1:
        raise ValueError('version must be 1')
    if snapshot['status'] not in {'ready', 'partial', 'blocked', 'fixture'}:
        raise ValueError('snapshot.status is not allowed')
    if not 1 <= len(snapshot['datasets']) <= 20:
        raise ValueError('snapshot.datasets must contain 1 to 20 datasets')

    scalar_types = (str, int, float, bool)
    for source_index, source in enumerate(manifest['sources']):
        source_path = f'manifest.sources[{source_index}]'
        assert_allowed_keys(source, SOURCE_ALLOWED, source_path)
        for key, value in source.get('filters', {}).items():
            if value is None or not isinstance(value, scalar_types):
                raise ValueError(
                    f'{source_path}.filters.{key} '
                    'must be a scalar'
                )
        for metric_index, metric in enumerate(source.get('metrics', [])):
            assert_allowed_keys(
                metric,
                SOURCE_METRIC_ALLOWED,
                f'{source_path}.metrics[{metric_index}]',
            )

    for block_index, block in enumerate(manifest['blocks']):
        assert_allowed_keys(block, BLOCK_ALLOWED, f'manifest.blocks[{block_index}]')

    for card_index, card in enumerate(manifest.get('cards', [])):
        card_path = f'manifest.cards[{card_index}]'
        assert_allowed_keys(card, CARD_ALLOWED, card_path)
        for metric_index, metric in enumerate(card['metrics']):
            assert_allowed_keys(
                metric,
                CARD_METRIC_ALLOWED,
                f'{card_path}.metrics[{metric_index}]',
            )

    for chart_index, chart in enumerate(manifest.get('charts', [])):
        chart_path = f'manifest.charts[{chart_index}]'
        assert_allowed_keys(chart, CHART_ALLOWED, chart_path)
        encodings = chart['encodings']
        assert_allowed_keys(encodings, ENCODING_ROLES, f'{chart_path}.encodings')
        for role, encoding in encodings.items():
            entries = encoding if role == 'tooltip' else [encoding]
            for encoding_index, entry in enumerate(entries):
                path = f'{chart_path}.encodings.{role}'
                if role == 'tooltip':
                    path += f'[{encoding_index}]'
                assert_allowed_keys(entry, ENCODING_ALLOWED, path)

    for table_index, table in enumerate(manifest.get('tables', [])):
        table_path = f'manifest.tables[{table_index}]'
        assert_allowed_keys(table, TABLE_ALLOWED, table_path)
        declared_columns = set()
        for column_index, column in enumerate(table['columns']):
            assert_allowed_keys(
                column,
                TABLE_COLUMN_ALLOWED,
                f'{table_path}.columns[{column_index}]',
            )
            declared_columns.add(column['field'])
        if 'defaultSort' in table:
            default_sort = table['defaultSort']
            assert_allowed_keys(
                default_sort,
                {'field', 'direction'},
                f'{table_path}.defaultSort',
            )
            if default_sort['field'] not in declared_columns:
                raise ValueError(
                    f'{table_path}.defaultSort.field references an undeclared column'
                )
            if default_sort['direction'] not in {'asc', 'desc'}:
                raise ValueError(f'{table_path}.defaultSort.direction is not allowed')

    chart_ids = {chart['id'] for chart in manifest.get('charts', [])}
    card_ids = {card['id'] for card in manifest.get('cards', [])}
    table_ids = {table['id'] for table in manifest.get('tables', [])}
    block_types = [block['type'] for block in manifest['blocks']]

    if len(chart_ids) != 3:
        raise ValueError('manifest must contain exactly three charts')
    if 'markdown' not in block_types or 'metric-strip' not in block_types:
        raise ValueError('manifest must contain text and KPI blocks')
    if 'table' not in block_types:
        raise ValueError('manifest must contain a table block')

    for block in manifest['blocks']:
        if block['type'] == 'chart' and block['chartId'] not in chart_ids:
            raise ValueError('chart block references a missing chart')
        if block['type'] == 'metric-strip':
            if not set(block['cardIds']) <= card_ids:
                raise ValueError('metric block references a missing card')
        if block['type'] == 'table' and block['tableId'] not in table_ids:
            raise ValueError('table block references a missing table')

    datasets = snapshot['datasets']
    for chart in manifest['charts']:
        rows = datasets[chart['dataset']]
        declared_fields = set(rows[0])
        for encoding in chart['encodings'].values():
            encodings = encoding if isinstance(encoding, list) else [encoding]
            for item in encodings:
                referenced = [item['field']] if 'field' in item else item['fields']
                if not set(referenced) <= declared_fields:
                    raise ValueError('chart encoding references a missing field')


def validate_chart_example(payload: dict) -> None:
    assert_allowed_keys(payload, STANDALONE_ALLOWED, 'payload')
    declared_fields = {column['key'] for column in payload['table']['columns']}
    encodings = payload['chart']['fields']

    for role in ('x', 'y'):
        encoding = encodings[role]
        if not isinstance(encoding, dict):
            raise ValueError(f'chart.fields.{role} must be an object')
        assert_allowed_keys(
            encoding,
            STANDALONE_ENCODING_ALLOWED,
            f'chart.fields.{role}',
        )
        if encoding['field'] not in declared_fields:
            raise ValueError(f'chart.fields.{role}.field is not declared')


class AnalyticsArtifactContractTest(unittest.TestCase):
    def test_exact_example_is_a_required_visualization_resource(self):
        skill = (ANALYTICS / 'SKILL.md').read_text(encoding='utf-8')

        self.assertIn('path: references/artifact-payload-example.json', skill)
        self.assertIn('kind: contract-example', skill)
        self.assertIn('manifest.scope', skill)

    def test_exact_example_matches_the_production_artifact_shape(self):
        payload = read_json(ARTIFACT_EXAMPLE)

        validate_artifact_example(payload)

    def test_manifest_scope_is_rejected_with_the_production_error_path(self):
        payload = read_json(ARTIFACT_EXAMPLE)
        payload = copy.deepcopy(payload)
        payload['manifest']['scope'] = 'resolved_company'

        with self.assertRaisesRegex(ValueError, r'^manifest\.scope is not allowed$'):
            validate_artifact_example(payload)


    def test_source_filters_reject_arrays_before_validate_artifact(self):
        payload = read_json(ARTIFACT_EXAMPLE)
        payload = copy.deepcopy(payload)
        payload['manifest']['sources'][0]['filters']['statuses'] = [
            'partner_verified',
            'client_accepted',
        ]

        with self.assertRaisesRegex(
            ValueError,
            r'^manifest\.sources\[0\]\.filters\.statuses must be a scalar$',
        ):
            validate_artifact_example(payload)

    def test_table_default_sort_must_reference_a_declared_column(self):
        payload = read_json(ARTIFACT_EXAMPLE)
        payload = copy.deepcopy(payload)
        payload['manifest']['tables'][0]['defaultSort'] = {
            'field': 'undeclared_month',
            'direction': 'asc',
        }

        with self.assertRaisesRegex(
            ValueError,
            r'^manifest\.tables\[0\]\.defaultSort\.field references '
            r'an undeclared column$',
        ):
            validate_artifact_example(payload)


class AnalyticsChartContractTest(unittest.TestCase):
    def test_exact_standalone_example_uses_typed_encodings(self):
        payload = read_json(CHART_EXAMPLE)

        validate_chart_example(payload)
        self.assertEqual(
            payload['chart']['fields']['x'],
            {'field': 'month', 'type': 'temporal', 'time_unit': 'month'},
        )
        self.assertEqual(
            payload['chart']['fields']['y'],
            {'field': 'profit', 'type': 'quantitative'},
        )

    def test_string_encoding_is_rejected(self):
        payload = read_json(CHART_EXAMPLE)
        payload = copy.deepcopy(payload)
        payload['chart']['fields']['x'] = 'month'

        with self.assertRaisesRegex(
            ValueError,
            r'^chart\.fields\.x must be an object$',
        ):
            validate_chart_example(payload)

class EventPositionsSkillContractTest(unittest.TestCase):
    def test_event_positions_uses_only_retained_price_list_reads(self):
        text = (SKILLS / 'event-positions/SKILL.md').read_text(encoding='utf-8')

        self.assertIn('  - list_price_lists', text)
        self.assertIn('  - get_price_list', text)
        self.assertNotIn('list_price_list_categories', text)
        self.assertNotIn('list_price_list_positions', text)
        self.assertNotIn('search_price_list_positions', text)


class PresentationRoutingContractTest(unittest.TestCase):
    def setUp(self):
        contract = read_json(ROUTING_CONTRACT)
        self.routes = {route['id']: route for route in contract['routes']}

    def test_russian_project_list_mounts_the_existing_projects_widget(self):
        route = self.routes['project_list']

        self.assertIn('выведи список проектов', route['examples'])
        self.assertEqual(route['tools'], ['list_projects', 'show_result'])
        self.assertEqual(route['widget']['kind'], 'projects')
        self.assertEqual(route['widget']['resourceUri'], 'ui://101/widget/app-2.0.7.html')

    def test_index_requires_the_routing_contract_and_show_result(self):
        index = (SKILLS / '101-index/SKILL.md').read_text(encoding='utf-8')

        self.assertIn('path: references/presentation-routing.json', index)
        self.assertIn('kind: routing-contract', index)
        self.assertIn('  - show_result', index)
        self.assertNotIn('Аналитика без графика', index)
        self.assertNotIn('сам факт аналитики не разрешает виджет', index)

    def test_companion_routes_keep_external_plugins_optional(self):
        self.assertTrue(COMPANION_ROUTING.is_file())
        contract = read_json(COMPANION_ROUTING)
        routes = {route['id']: route for route in contract['routes']}

        self.assertEqual(routes['crm_crud']['owner'], 'crm-management')
        self.assertEqual(routes['pdf_output']['owner'], 'pdf')
        self.assertFalse(routes['pdf_output']['required'])
        self.assertEqual(routes['extended_sales']['owner'], 'sales:index')
        self.assertFalse(routes['extended_sales']['required'])
        self.assertEqual(
            routes['extended_sales']['fallback'],
            'preserve_101_result',
        )

    def test_index_loads_companion_routing_contract(self):
        index = (SKILLS / '101-index/SKILL.md').read_text(encoding='utf-8')

        self.assertIn('path: references/companion-routing.json', index)
        self.assertIn('kind: routing-contract', index)

    def test_insufficient_tokens_has_browser_first_recovery_without_retry(self):
        contract = read_json(ERROR_RECOVERY)
        recovery = contract['errors']['insufficient_tokens']

        self.assertEqual(recovery['code'], 'insufficient_tokens')
        self.assertEqual(recovery['urlField'], 'topUpUrl')
        self.assertEqual(recovery['urlSource'], 'server_result_only')
        self.assertEqual(recovery['primaryAction'], 'open_in_app_browser')
        self.assertEqual(recovery['fallbackAction'], 'show_clickable_link')
        self.assertEqual(recovery['retry'], 'after_top_up_only')
        self.assertEqual(recovery['freeTools'], 'remain_available')

    def test_index_loads_and_explains_error_recovery_contract(self):
        index = (SKILLS / '101-index/SKILL.md').read_text(encoding='utf-8')

        self.assertIn('path: references/error-recovery.json', index)
        self.assertIn('kind: error-recovery-contract', index)
        self.assertIn('structuredContent.data.code', index)
        self.assertIn('browser:control-in-app-browser', index)
        self.assertIn('кликабельную Markdown-ссылку', index)
        self.assertIn('Не повторяй исходный тарифицируемый MCP-вызов', index)

    def test_russian_event_list_mounts_the_existing_events_widget(self):
        route = self.routes['event_list']

        self.assertIn('выведи список событий', route['examples'])
        self.assertEqual(route['tools'], ['list_events', 'show_result'])
        self.assertEqual(route['widget']['kind'], 'events')
        self.assertEqual(route['widget']['resourceUri'], 'ui://101/widget/app-2.0.7.html')

    def test_task_detail_routes_to_the_shared_application_widget(self):
        route = self.routes['task_detail']

        self.assertIn('открой задачу', route['examples'])
        self.assertEqual(route['tools'], ['get_task', 'show_result'])
        self.assertEqual(route['widget']['kind'], 'task_detail')
        self.assertEqual(
            route['widget']['resourceUri'],
            'ui://101/widget/app-2.0.7.html',
        )

    def test_analytics_routes_are_visual_but_scalar_reads_are_text_only(self):
        chart = self.routes['bounded_comparison_or_trend']
        artifact = self.routes['audit_or_multicomponent_analysis']
        scalar = self.routes['scalar_read']

        self.assertEqual(chart['tools'], ['render_chart'])
        self.assertEqual(artifact['tools'], ['validate_artifact', 'render_artifact'])
        self.assertEqual(
            artifact['artifact'],
            {'text': True, 'kpi': True, 'charts': 3, 'table': True},
        )
        self.assertEqual(scalar['tools'], [])
        self.assertFalse(scalar['presentation'])


class SkillsArchiveTest(unittest.TestCase):
    def test_download_archive_exactly_mirrors_the_plugin_skills(self):
        expected = {
            path.relative_to(SKILLS).as_posix(): path.read_bytes()
            for path in SKILLS.rglob('*')
            if path.is_file()
        }
        with zipfile.ZipFile(ROOT / 'downloads/101-skills.zip') as archive:
            actual = {
                name.removeprefix('101-skills/'): archive.read(name)
                for name in archive.namelist()
                if not name.endswith('/')
            }

        self.assertEqual(set(actual), set(expected))
        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
