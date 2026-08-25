import re
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / 'plugins/101/skills'

USER_COMPLETION_STATUSES = (
    'готово',
    'частично',
    'не завершено',
)

EXPECTED_SKILL_NAMES = {
    '101-index',
    'analytics-visualization',
    'company-analytics',
    'crm-management',
    'data-import',
    'entity-resolution',
    'estimate-management',
    'event-positions',
    'file-handling',
    'financial-account-audit',
    'project-management',
    'report-management',
    'settlements-and-transfers',
    'task-management',
    'wiki-management',
    'write-preflight',
}

EXPECTED_SHARED_RESOURCES = {
    'shared-resources/context-and-identity.md',
    'shared-resources/data-import-rules.md',
    'shared-resources/events-and-positions.md',
    'shared-resources/finance-and-balances.md',
    'shared-resources/financial-risks-and-project-controls.md',
    'shared-resources/management-reporting-and-balances.md',
    'shared-resources/safety-and-permissions.md',
    'shared-resources/technical-integrity-audit.md',
    'shared-resources/wiki-content-and-files.md',
}

ALLOWED_RESOURCE_KINDS = {
    'error-recovery-contract',
    'payload-example',
    'routing-contract',
    'semantic-guide',
    'token-snapshot',
}


def skill_paths() -> list[Path]:
    return sorted(SKILLS.glob('*/SKILL.md'))


def shared_resource_paths() -> list[Path]:
    return sorted((SKILLS / 'shared-resources').glob('*.md'))


def parse_yaml_scalar(value: str):
    if value == '[]':
        return []
    if value == 'true':
        return True
    if value == 'false':
        return False
    if value in {'null', '~'}:
        return None
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def indentation(line: str) -> int:
    return len(line) - len(line.lstrip(' '))


def parse_yaml_subset(lines: list[str], start: int, indent: int):
    if start >= len(lines) or indentation(lines[start]) != indent:
        raise ValueError('invalid YAML indentation')

    is_list = lines[start].lstrip(' ').startswith('- ')
    value = [] if is_list else {}
    index = start

    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        current_indent = indentation(line)
        if current_indent < indent:
            break
        if current_indent > indent:
            raise ValueError(f'unexpected YAML indentation: {line}')
        stripped = line.strip()

        if is_list:
            if not stripped.startswith('- '):
                raise ValueError(f'mixed YAML list and mapping: {line}')
            item = stripped[2:]
            if ': ' not in item and not item.endswith(':'):
                value.append(parse_yaml_scalar(item))
                index += 1
                continue

            key, raw_value = item.split(':', 1)
            mapping = {}
            raw_value = raw_value.strip()
            index += 1
            if raw_value:
                mapping[key] = parse_yaml_scalar(raw_value)
            elif index < len(lines) and indentation(lines[index]) > indent:
                nested_indent = indentation(lines[index])
                mapping[key], index = parse_yaml_subset(lines, index, nested_indent)
            else:
                mapping[key] = None

            while index < len(lines):
                continuation = lines[index]
                if not continuation.strip():
                    index += 1
                    continue
                if indentation(continuation) <= indent:
                    break
                if indentation(continuation) != indent + 2:
                    raise ValueError(f'invalid YAML mapping indentation: {continuation}')
                item_key, item_value = continuation.strip().split(':', 1)
                item_value = item_value.strip()
                index += 1
                if item_value:
                    mapping[item_key] = parse_yaml_scalar(item_value)
                elif index < len(lines) and indentation(lines[index]) > indent + 2:
                    nested_indent = indentation(lines[index])
                    mapping[item_key], index = parse_yaml_subset(
                        lines,
                        index,
                        nested_indent,
                    )
                else:
                    mapping[item_key] = None
            value.append(mapping)
            continue

        if ':' not in stripped:
            raise ValueError(f'invalid YAML mapping entry: {line}')
        key, raw_value = stripped.split(':', 1)
        raw_value = raw_value.strip()
        index += 1
        if raw_value:
            value[key] = parse_yaml_scalar(raw_value)
        elif index < len(lines) and lines[index].strip():
            nested_indent = indentation(lines[index])
            if nested_indent <= indent:
                value[key] = None
            else:
                value[key], index = parse_yaml_subset(lines, index, nested_indent)
        else:
            value[key] = None
    return value, index


def frontmatter_data(skill_path: Path) -> dict:
    parts = skill_path.read_text(encoding='utf-8').split('---', 2)
    if len(parts) != 3 or parts[0].strip():
        raise AssertionError(f'valid frontmatter missing in {skill_path}')

    data, index = parse_yaml_subset(parts[1].splitlines(), 0, 0)
    if index != len(parts[1].splitlines()):
        raise AssertionError(f'unparsed frontmatter in {skill_path}')
    if not isinstance(data, dict):
        raise AssertionError(f'frontmatter is not a mapping in {skill_path}')
    return data


def frontmatter_list(skill_path: Path, key: str) -> tuple[str, ...]:
    value = frontmatter_data(skill_path).get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise AssertionError(f'{key} missing in {skill_path}')
    return tuple(value)


def completion_statuses(skill_path: Path) -> tuple[str, ...]:
    completion = frontmatter_data(skill_path).get('completion')
    if not isinstance(completion, dict):
        raise AssertionError(f'completion.statuses missing in {skill_path}')
    statuses = completion.get('statuses')
    if not isinstance(statuses, list) or not all(
        isinstance(status, str) for status in statuses
    ):
        raise AssertionError(f'completion.statuses missing in {skill_path}')
    return tuple(statuses)


def read_skill_resource(relative_path: str) -> str:
    return (SKILLS / relative_path).read_text(encoding='utf-8')


def policy_bullets(policy: str) -> list[str]:
    return [
        line.removeprefix('- ').strip()
        for line in policy.splitlines()
        if line.startswith('- ')
    ]


def parse_unfinished_completion_examples(policy: str) -> dict[str, str]:
    match = re.search(
        (
            r'```text\n'
            r'(частично)\n([^\n]+)\n'
            r'(не завершено)\n([^\n]+)\n'
            r'```'
        ),
        policy,
    )
    if match is None:
        raise AssertionError('missing canonical unfinished completion example block')

    return {
        match.group(1): match.group(2),
        match.group(3): match.group(4),
    }


def confirmation_policy_lines(policy: str) -> list[str]:
    normalized_lines = [
        line.strip().removeprefix('- ').lower()
        for line in policy.splitlines()
        if line.strip()
    ]
    return [
        line
        for line in normalized_lines
        if 'conversational confirmation' in line or 'central mcp confirmation' in line
    ]


def depends_on(skill_path: Path) -> tuple[str, ...]:
    return frontmatter_list(skill_path, 'depends_on')


def optional_tools(skill_path: Path) -> tuple[str, ...]:
    return frontmatter_list(skill_path, 'optional_tools')


def skill_body(skill_path: Path) -> str:
    parts = skill_path.read_text(encoding='utf-8').split('---', 2)
    if len(parts) != 3 or parts[0].strip():
        raise AssertionError(f'valid frontmatter missing in {skill_path}')
    return parts[2]


def relative_to_skills(path: Path) -> str | None:
    try:
        return path.resolve().relative_to(SKILLS.resolve()).as_posix()
    except ValueError:
        return None


def dependency_graph_errors() -> list[str]:
    errors = []
    paths = skill_paths()
    actual_names = {path.parent.name for path in paths}
    if actual_names != EXPECTED_SKILL_NAMES:
        errors.append(
            f'skill inventory mismatch: expected {sorted(EXPECTED_SKILL_NAMES)}, '
            f'got {sorted(actual_names)}'
        )

    frontmatters = {}
    names = {}
    for path in paths:
        try:
            data = frontmatter_data(path)
        except (AssertionError, ValueError) as error:
            errors.append(str(error))
            continue
        frontmatters[path.parent.name] = data
        name = data.get('name')
        if not isinstance(name, str):
            errors.append(f'{path}: name is missing')
        elif name in names:
            errors.append(f'duplicate skill name {name}: {names[name]} and {path}')
        else:
            names[name] = path

    graph = {}
    for directory_name, data in frontmatters.items():
        declared_name = data.get('name')
        dependencies = data.get('depends_on')
        if not isinstance(dependencies, list) or not all(
            isinstance(dependency, str) for dependency in dependencies
        ):
            errors.append(f'{directory_name}: depends_on must be a YAML list')
            continue
        graph[declared_name] = dependencies
        for dependency in dependencies:
            if dependency not in names:
                errors.append(f'{declared_name}: unresolved dependency {dependency}')
            if dependency == declared_name:
                errors.append(f'{declared_name}: self dependency')

    visited = set()
    visiting = set()

    def visit(name: str, trail: tuple[str, ...]) -> None:
        if name in visiting:
            errors.append(f'dependency cycle: {" -> ".join((*trail, name))}')
            return
        if name in visited or name not in graph:
            return
        visiting.add(name)
        for dependency in graph[name]:
            visit(dependency, (*trail, name))
        visiting.remove(name)
        visited.add(name)

    for name in graph:
        visit(name, ())
    return errors


def resource_link_errors() -> list[str]:
    errors = []
    actual_resources = {
        path.relative_to(SKILLS).as_posix()
        for path in shared_resource_paths()
    }
    if actual_resources != EXPECTED_SHARED_RESOURCES:
        errors.append(
            f'shared resource inventory mismatch: '
            f'expected {sorted(EXPECTED_SHARED_RESOURCES)}, '
            f'got {sorted(actual_resources)}'
        )

    for skill_path in skill_paths():
        try:
            resources = frontmatter_data(skill_path).get('resources')
        except (AssertionError, ValueError) as error:
            errors.append(str(error))
            continue
        if not isinstance(resources, list):
            errors.append(f'{skill_path.parent.name}: resources must be a YAML list')
            continue
        for resource in resources:
            if not isinstance(resource, dict):
                errors.append(f'{skill_path.parent.name}: invalid resource declaration')
                continue
            relative_path = resource.get('path')
            if not isinstance(relative_path, str):
                errors.append(f'{skill_path.parent.name}: resource path is missing')
                continue
            resolved = skill_path.parent / relative_path
            normalized = relative_to_skills(resolved)
            if normalized is None:
                errors.append(
                    f'{skill_path.parent.name}: resource escapes skills root: '
                    f'{relative_path}'
                )
            elif not resolved.is_file():
                errors.append(
                    f'{skill_path.parent.name}: unresolved resource {relative_path}'
                )
    return errors


def resource_contract_errors() -> list[str]:
    errors = []
    for skill_path in skill_paths():
        try:
            resources = frontmatter_data(skill_path).get('resources')
        except (AssertionError, ValueError) as error:
            errors.append(str(error))
            continue
        if not isinstance(resources, list):
            errors.append(f'{skill_path.parent.name}: resources must be a YAML list')
            continue
        for resource in resources:
            if not isinstance(resource, dict):
                errors.append(f'{skill_path.parent.name}: invalid resource declaration')
                continue
            if resource.get('required') is not True:
                errors.append(
                    f'{skill_path.parent.name}: resource must declare required: true'
                )
            if resource.get('kind') not in ALLOWED_RESOURCE_KINDS:
                errors.append(
                    f'{skill_path.parent.name}: invalid resource kind '
                    f'{resource.get("kind")!r}'
                )
    return errors


def completion_safety_resource_errors() -> list[str]:
    errors = []
    for skill_path in skill_paths():
        data = frontmatter_data(skill_path)
        completion = data.get('completion')
        if not isinstance(completion, dict) or 'statuses' not in completion:
            continue
        resources = data.get('resources')
        has_safety_policy = isinstance(resources, list) and any(
            resource.get('path') == '../shared-resources/safety-and-permissions.md'
            and resource.get('required') is True
            for resource in resources
            if isinstance(resource, dict)
        )
        if not has_safety_policy:
            errors.append(
                f'{skill_path.parent.name}: missing required safety-and-permissions '
                'resource'
            )
    return errors


def public_completion_contract_errors() -> list[str]:
    errors = []
    policy = read_skill_resource('shared-resources/safety-and-permissions.md')
    template = (
        'частично',
        'Reason: <concrete reason>. Next safe step: <smallest safe next step>.',
        'не завершено',
        'Reason: <concrete reason>. Next safe step: <smallest safe next step>.',
    )
    policy_lines = tuple(policy.splitlines())
    if not any(
        policy_lines[index:index + len(template)] == template
        for index in range(len(policy_lines) - len(template) + 1)
    ):
        errors.append('canonical unfinished completion template is missing')

    errors.extend(completion_safety_resource_errors())

    for skill_path in skill_paths():
        if completion_statuses(skill_path) != USER_COMPLETION_STATUSES:
            errors.append(f'{skill_path.parent.name}: invalid completion statuses')
        if 'заблокировано' in skill_body(skill_path):
            errors.append(f'{skill_path.parent.name}: user-facing заблокировано')

    analytics = skill_body(SKILLS / 'analytics-visualization/SKILL.md')
    chart_design = read_skill_resource(
        'analytics-visualization/references/chart-design.md'
    )
    if '`snapshot.status` uses only `ready|partial|blocked|fixture`' not in analytics:
        errors.append('analytics technical blocked contract changed')
    if '`ready|partial|blocked|fixture` are the only statuses.' not in chart_design:
        errors.append('chart technical blocked contract changed')
    return errors


class SkillBehaviorContractTest(unittest.TestCase):
    def test_all_dependencies_and_resources_resolve(self):
        self.assertEqual(dependency_graph_errors(), [])
        self.assertEqual(resource_link_errors(), [])

    def test_resource_declarations_are_required_and_use_allowed_kinds(self):
        self.assertEqual(resource_contract_errors(), [])

    def test_every_completion_bearing_skill_directly_declares_safety_policy(self):
        self.assertEqual(completion_safety_resource_errors(), [])

    def test_all_public_skill_bodies_keep_the_completion_boundary(self):
        self.assertEqual(public_completion_contract_errors(), [])

    def test_frontmatter_contract_runs_without_site_packages(self):
        result = subprocess.run(
            [
                sys.executable,
                '-S',
                '-m',
                'unittest',
                'tests.test_skill_behavior_contract.SkillBehaviorContractTest.'
                'test_all_dependencies_and_resources_resolve',
                'tests.test_skill_behavior_contract.SkillBehaviorContractTest.'
                'test_every_skill_uses_the_user_completion_contract',
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_yaml_frontmatter_preserves_inline_empty_lists(self):
        analytics_path = SKILLS / 'analytics-visualization/SKILL.md'
        self.assertEqual(depends_on(analytics_path), ())
        self.assertEqual(optional_tools(analytics_path), ())

    def test_stdlib_parser_supports_block_maps_lists_and_inline_empty_lists(self):
        parsed, index = parse_yaml_subset(
            [
                'depends_on: []',
                'resources:',
                '  - path: ../shared-resources/safety-and-permissions.md',
                '    kind: semantic-guide',
                '    required: true',
                'completion:',
                '  statuses:',
                '    - готово',
                '    - не завершено',
            ],
            0,
            0,
        )
        self.assertEqual(index, 9)
        self.assertEqual(parsed['depends_on'], [])
        self.assertEqual(
            parsed['resources'],
            [
                {
                    'path': '../shared-resources/safety-and-permissions.md',
                    'kind': 'semantic-guide',
                    'required': True,
                }
            ],
        )
        self.assertEqual(parsed['completion']['statuses'], ['готово', 'не завершено'])

    def test_every_skill_uses_the_user_completion_contract(self):
        paths = skill_paths()

        self.assertEqual(
            {path.parent.name for path in paths},
            EXPECTED_SKILL_NAMES,
        )
        for skill_path in paths:
            self.assertEqual(
                completion_statuses(skill_path),
                USER_COMPLETION_STATUSES,
                skill_path.parent.name,
            )

    def test_shared_policy_runs_safe_steps_and_formats_unfinished_results(self):
        policy = read_skill_resource('shared-resources/safety-and-permissions.md')
        bullets = policy_bullets(policy)
        unfinished_examples = parse_unfinished_completion_examples(policy)
        confirmation_lines = confirmation_policy_lines(policy)

        self.assertIn(
            'Execute safe reads, searches, calculations, preparation, exact '
            'matching, and other unambiguous safe steps immediately.',
            bullets,
        )
        self.assertIn(
            'Ask only when required data is genuinely ambiguous or missing, an '
            'action is irreversible, a write outcome is unknown, fresh mutable '
            'state conflicts, or another material risk requires a user decision.',
            bullets,
        )
        self.assertEqual(
            unfinished_examples,
            {
                'частично': 'Reason: <concrete reason>. Next safe step: <smallest safe next step>.',
                'не завершено': 'Reason: <concrete reason>. Next safe step: <smallest safe next step>.',
            },
        )
        self.assertEqual(len(confirmation_lines), 1)
        self.assertEqual(
            confirmation_lines[0],
            'if the user explicitly and unambiguously requests a financial event '
            'and every required value and entity is known, do not add a '
            'conversational confirmation. use only the central mcp confirmation '
            'when the runtime requires it.',
        )

    def test_shared_event_queue_is_owned_once_and_referenced_by_financial_skills(self):
        events_resource = read_skill_resource('shared-resources/events-and-positions.md')
        report_skill = read_skill_resource('report-management/SKILL.md')
        estimate_skill = read_skill_resource('estimate-management/SKILL.md')

        self.assertIn('Create multiple events as sequential single-event create calls.', events_resource)
        self.assertIn('If a known issue exists anywhere in the queue, create nothing yet.', events_resource)
        self.assertIn('Immediately before each item, rerun a fresh `write-preflight` and make exactly one create call.', events_resource)
        self.assertIn('A local data error blocks only that item.', events_resource)
        self.assertIn('A system error, lost permission, contract change, or uncertain write outcome stops the remaining tail.', events_resource)

        for skill in (report_skill, estimate_skill):
            self.assertIn('Follow the shared sequential queue contract in `events-and-positions.md`.', skill)
            self.assertNotIn('A bulk request is a sequence of individual', skill)
            self.assertNotIn('Repeat a fresh `write-preflight` before each item', skill)

    def test_complete_financial_writes_rely_on_central_confirmation_only(self):
        report_skill = read_skill_resource('report-management/SKILL.md')
        estimate_skill = read_skill_resource('estimate-management/SKILL.md')
        settlements_skill = read_skill_resource('settlements-and-transfers/SKILL.md')
        preflight_skill = read_skill_resource('write-preflight/SKILL.md')

        self.assertIn(
            'When the user explicitly requests a complete report and every required '
            'field is known, proceed after fresh `write-preflight` under the central '
            'MCP policy without a second chat confirmation.',
            report_skill,
        )
        self.assertIn(
            'When the user explicitly requests a complete estimate and every required '
            'field is known, proceed after fresh `write-preflight` under the central '
            'MCP policy without a second chat confirmation.',
            estimate_skill,
        )
        self.assertIn(
            'Use only central MCP confirmation policy; do not add another layer or '
            'bypass the standard flow.',
            settlements_skill,
        )
        self.assertIn(
            'When the user explicitly requests the complete linked pair and every '
            'required field is known, proceed after fresh `write-preflight` under '
            'the central MCP policy without a second chat confirmation.',
            settlements_skill,
        )
        self.assertIn(
            'Apply the central MCP confirmation and risk policy. Do not add a separate '
            'confirmation layer or weaken the standard one.',
            preflight_skill,
        )

    def test_helper_boundaries_remove_duplicate_preflight_and_direct_task_uploads(self):
        event_positions_path = SKILLS / 'event-positions/SKILL.md'
        event_positions_skill = event_positions_path.read_text(encoding='utf-8')
        events_resource = read_skill_resource('shared-resources/events-and-positions.md')
        task_management_path = SKILLS / 'task-management/SKILL.md'
        task_management_skill = task_management_path.read_text(encoding='utf-8')

        self.assertNotIn('write-preflight', depends_on(event_positions_path))
        self.assertNotIn('pass the result to `write-preflight`', event_positions_skill)
        self.assertNotIn('Take `startDate` and `endDate` only', event_positions_skill)
        self.assertIn(
            'Take `startDate` and `endDate` only from explicit user data or an '
            'existing position.',
            events_resource,
        )

        self.assertIn('file-handling', depends_on(task_management_path))
        self.assertNotIn('upload_files', optional_tools(task_management_path))
        self.assertIn(
            'When the user attaches files outside the widget, route them through '
            '`file-handling` and pass only server identifiers to a tool that '
            'supports attachments.',
            task_management_skill,
        )


if __name__ == '__main__':
    unittest.main()
