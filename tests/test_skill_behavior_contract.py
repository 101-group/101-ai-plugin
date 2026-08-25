import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / 'plugins/101/skills'

USER_COMPLETION_STATUSES = (
    'готово',
    'частично',
    'не завершено',
)


def read_frontmatter(skill_path: Path) -> str:
    return skill_path.read_text(encoding='utf-8').split('---', 2)[1]


def frontmatter_list(skill_path: Path, key: str) -> tuple[str, ...]:
    frontmatter = read_frontmatter(skill_path)
    match = re.search(
        rf'{re.escape(key)}:\n((?:  - .+\n)+)',
        frontmatter,
    )
    if match is None:
        raise AssertionError(f'{key} missing in {skill_path}')

    return tuple(
        line.removeprefix('  - ').strip()
        for line in match.group(1).splitlines()
    )


def completion_statuses(skill_path: Path) -> tuple[str, ...]:
    frontmatter = read_frontmatter(skill_path)
    match = re.search(
        r'completion:\n  statuses:\n((?:    - .+\n)+)',
        frontmatter,
    )
    if match is None:
        raise AssertionError(f'completion.statuses missing in {skill_path}')

    return tuple(
        line.removeprefix('    - ').strip()
        for line in match.group(1).splitlines()
    )


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


class SkillBehaviorContractTest(unittest.TestCase):
    def test_every_skill_uses_the_user_completion_contract(self):
        skill_paths = sorted(
            path
            for path in SKILLS.glob('*/SKILL.md')
            if path.parent.name != 'shared-resources'
        )

        self.assertEqual(len(skill_paths), 16)
        for skill_path in skill_paths:
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
