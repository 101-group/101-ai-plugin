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


if __name__ == '__main__':
    unittest.main()
