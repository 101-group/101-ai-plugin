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


def safe_action_contract(policy: str) -> bool:
    normalized = policy.lower()
    required_fragments = (
        'safe reads, searches, calculations, preparation, exact matching',
        'immediately',
        'ask only when required data is genuinely ambiguous or missing',
        'an action is irreversible',
        'a write outcome is unknown',
        'fresh mutable state conflicts',
        'another material risk requires a user decision',
    )
    return all(fragment in normalized for fragment in required_fragments)


def immediate_follow_up_contract(policy: str) -> bool:
    normalized = policy.lower()
    required_fragments = (
        'canonical user-facing completion status',
        '`частично` or `не завершено`',
        'immediately following line',
        'concrete reason',
        'smallest safe next step',
    )
    return all(fragment in normalized for fragment in required_fragments)


def central_financial_confirmation_contract(policy: str) -> bool:
    normalized = policy.lower()
    required_fragments = (
        'explicitly and unambiguously requests a financial event',
        'every required value and entity is known',
        'do not add a conversational confirmation',
        'use only the central mcp confirmation',
    )
    return all(fragment in normalized for fragment in required_fragments)


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

        self.assertTrue(safe_action_contract(policy))
        self.assertTrue(immediate_follow_up_contract(policy))
        self.assertTrue(central_financial_confirmation_contract(policy))


if __name__ == '__main__':
    unittest.main()
