# 101 skills: status and optimization audit

Date: 2026-08-25
Release candidate: public Marketplace plugin `2.2.2`

## Scope and method

The audit read the complete bodies and YAML frontmatter of all 16 public
`SKILL.md` files, all nine files in `shared-resources/`, and the two linked
Markdown references that are included by the size measurement. Every declared
dependency and resource is parsed by a stdlib-only parser for the actual YAML
subset: block maps, block lists, booleans, quoted scalars, and inline empty
lists. This matters because the plugin uses valid inline lists such as
`depends_on: []` and `optional_tools: []`.

The automated inventory is deliberately exact: it expects all 16 skill names
and all nine shared-resource paths. A new skill or shared resource therefore
cannot disappear from the audit because a broad glob silently skipped it.

## Audited inventory

| Kind | Files checked |
| --- | --- |
| Skills: frontmatter and body | `101-index`, `analytics-visualization`, `company-analytics`, `crm-management`, `data-import`, `entity-resolution`, `estimate-management`, `event-positions`, `file-handling`, `financial-account-audit`, `project-management`, `report-management`, `settlements-and-transfers`, `task-management`, `wiki-management`, `write-preflight` |
| Shared resources | `context-and-identity`, `data-import-rules`, `events-and-positions`, `finance-and-balances`, `financial-risks-and-project-controls`, `management-reporting-and-balances`, `safety-and-permissions`, `technical-integrity-audit`, `wiki-content-and-files` |
| Included Markdown references | `analytics-visualization/references/chart-design.md`, `crm-management/references/crm-orchestration.md` |

All 16 frontmatters declare exactly the user-facing completion statuses
`готово`, `частично`, and `не завершено`. The audit also checked the bodies
and the central completion template: a user result after `частично` or `не
завершено` must put its concrete reason and smallest safe next step on the
immediately following line. Technical analytics retains the distinct
`snapshot.status=ready|partial|blocked|fixture` contract; `blocked` is not a
user-facing completion status.

## Graph and resource proof

The parsed graph contains 16 named nodes and 25 dependency edges. Every edge
resolves to one of those nodes, no skill depends on itself, and depth-first
cycle detection found no cycle. The resource audit found 51 declared resource
links; every one declares `required: true`, uses an allowed resource kind,
resolves to a file, and remains within `plugins/101/skills/`.

Notable dependency boundaries after the audit:

- `event-positions` depends only on `entity-resolution`; it owns neither
  `write-preflight` nor confirmation.
- `task-management` and `wiki-management` use `file-handling` for attachments;
  task management no longer declares a direct `upload_files` tool.
- `report-management` and `estimate-management` retain their domain-specific
  event contracts but reference the shared queue contract instead of carrying a
  second copy of it.

## Removed duplication and questions

- Centralized the safe-step / ask-only policy in
  `safety-and-permissions.md`. Safe reads, search, calculations, preparation,
  and exact matching proceed without an extra chat question; questions remain
  for missing or ambiguous data, irreversible action, unknown outcome, fresh
  mutable-state conflict, or another material risk.
- Removed the repeated six-step queue, fresh-preflight, receipt, continuation,
  and unknown-outcome text from both report and estimate series. The canonical
  wording now lives once in `events-and-positions.md`.
- Removed `write-preflight` ownership and duplicated date/full-list conflict
  text from `event-positions`; the shared event resource owns the position
  invariants and the primary skill owns the write preflight.
- Replaced direct task-file upload instructions and the direct optional upload
  tool with the `file-handling` helper boundary.
- Removed redundant conversational confirmation for an explicit, complete,
  unambiguous report, estimate, or linked transfer. The central MCP policy is
  the only confirmation layer when the runtime requires one.
- Replaced the former user-facing `заблокировано` completion wording with the
  canonical completion contract. This did not rename the analytics data field
  `snapshot.status=blocked`.

## Protections retained

The consolidation did not relax OAuth authorization, API-owned permissions,
central scopes, risk flags, or central confirmation. The final shared safety
policy still requires idempotency or proof before retrying a write, preserves
receipts, treats an unknown write outcome as a stop-and-verify condition, and
forbids blind write retries. `write-preflight` still rereads mutable state and
permissions immediately before a mutation and blocks conflicting snapshots.

The event queue still validates the full queue before the first write, makes
exactly one create call after a fresh per-item preflight, permits only a local
error to isolate one item, and stops the remaining tail on a system error,
lost permission, contract change, or uncertain outcome. The technical
integrity audit remains a distinct blocking gate for a full financial analysis:
a structural or arithmetic failure stops the following analysis without making
a mutation.

## Route and context optimization

The dispatcher selects one primary workflow and avoids preloading chart
instructions. `analytics-visualization` is read only after visualization is
allowed; `company-analytics` reads the financial-risk or management-reporting
resource only after the selected analysis mode requires it. Shared safety,
queue, and file-routing instructions are loaded by the owning helper rather
than duplicated in every caller. The domain-specific report, estimate, and
transfer contracts remain separate where merging them would blur REST routing.

This is a routing and duplication optimization only. No unsupported token
saving is claimed.

## Exact size measurement

The authoritative baseline is commit
`9f06171e54a25aab02c355e1e802ca3a1e02dd06` (`origin/main`, `v2.2.1`, before
Tasks 1–3). Both measurements use exactly these 27 Markdown paths; the command
below also verifies that base and current path sets have zero differences.

```text
plugins/101/skills/101-index/SKILL.md
plugins/101/skills/analytics-visualization/SKILL.md
plugins/101/skills/analytics-visualization/references/chart-design.md
plugins/101/skills/company-analytics/SKILL.md
plugins/101/skills/crm-management/SKILL.md
plugins/101/skills/crm-management/references/crm-orchestration.md
plugins/101/skills/data-import/SKILL.md
plugins/101/skills/entity-resolution/SKILL.md
plugins/101/skills/estimate-management/SKILL.md
plugins/101/skills/event-positions/SKILL.md
plugins/101/skills/file-handling/SKILL.md
plugins/101/skills/financial-account-audit/SKILL.md
plugins/101/skills/project-management/SKILL.md
plugins/101/skills/report-management/SKILL.md
plugins/101/skills/settlements-and-transfers/SKILL.md
plugins/101/skills/shared-resources/context-and-identity.md
plugins/101/skills/shared-resources/data-import-rules.md
plugins/101/skills/shared-resources/events-and-positions.md
plugins/101/skills/shared-resources/finance-and-balances.md
plugins/101/skills/shared-resources/financial-risks-and-project-controls.md
plugins/101/skills/shared-resources/management-reporting-and-balances.md
plugins/101/skills/shared-resources/safety-and-permissions.md
plugins/101/skills/shared-resources/technical-integrity-audit.md
plugins/101/skills/shared-resources/wiki-content-and-files.md
plugins/101/skills/task-management/SKILL.md
plugins/101/skills/wiki-management/SKILL.md
plugins/101/skills/write-preflight/SKILL.md
```

Run from the repository root:

```sh
BASE=9f06171e54a25aab02c355e1e802ca3a1e02dd06
git ls-tree -r --name-only "$BASE" -- plugins/101/skills | awk '/\.md$/' |
  while IFS= read -r file; do git show "$BASE:$file"; done | wc -w
git ls-tree -r --name-only "$BASE" -- plugins/101/skills | awk '/\.md$/' |
  while IFS= read -r file; do git show "$BASE:$file"; done | wc -l
find plugins/101/skills -type f -name '*.md' -print0 | sort -z |
  xargs -0 cat | wc -w
find plugins/101/skills -type f -name '*.md' -print0 | sort -z |
  xargs -0 cat | wc -l
comm -3 \
  <(git ls-tree -r --name-only "$BASE" -- plugins/101/skills | awk '/\.md$/' | sort) \
  <(find plugins/101/skills -type f -name '*.md' | sort)
```

Observed output: `14679`, `1632`, `14728`, `1643`, followed by no output from
`comm -3`. Thus both sides contain 27 Markdown files and the final delta is
exactly `+49` words and `+11` lines.

| Measurement | Baseline | Final | Delta |
| --- | ---: | ---: | ---: |
| Words across all `plugins/101/skills/**/*.md` | 14,679 | 14,728 | +49 |
| Lines across all `plugins/101/skills/**/*.md` | 1,632 | 1,643 | +11 |

The small net growth is intentional: central completion wording and queue
ownership replace larger repeated sections while preserving the explicit
safety evidence. The figures are size facts, not a claim about model token
use.

## RED to GREEN evidence

Before the release files changed, the focused command
`python3 -m unittest tests.test_skill_behavior_contract tests.test_plugin_manifest -v`
ran 14 tests and failed exactly two version assertions: both read manifest
version `2.2.1` while the new contract required `2.2.2`. The new graph and
resource test passed in that RED run, establishing that no stale dependency or
resource edge was hidden by the version failure.

After changing only the public release references in the manifest and README,
the same focused suite passed.

Final whole-branch verification was run directly from the repository root:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
Ran 46 tests in 0.117s
OK
```

The final-review regression first failed with the old opt-in resource text,
then passed after the resource became automatic for full company analysis. It
requires `run it automatically and unconditionally`, requires the narrow-route
skip, and rejects `offer`, `user agrees`, and `user accepted` in the technical
integrity resource.

## Stdlib parser and public-boundary regression proof

The graph/status tests now run under `python3 -S`, so no undeclared site-package
dependency is needed. The parser has direct coverage for block mappings, block
lists, boolean `required: true`, and inline empty lists. The resource graph also
checks the allowed kind set: `semantic-guide`, `routing-contract`,
`error-recovery-contract`, `token-snapshot`, and `payload-example`.

The public completion test examines all 16 skill bodies, rejects the Russian
user-facing `заблокировано`, requires the exact frontmatter triplet, and
physically checks the two-line unfinished result template in the central safety
resource. Every completion-bearing skill directly declares that resource with
`required: true`; the dispatcher is not used as a proxy for this ownership. The
separate technical contracts remain exact in analytics and its chart reference:
`ready|partial|blocked|fixture`.

The canonical skills archive was rebuilt from `plugins/101/skills` with
`zip -q -r -FS -X ../../../downloads/101-skills.zip .`. It contains 48 regular
files, byte-for-byte mirrors the skill tree, and has SHA-256
`fa819eee62bae2ed041da75b7a8a03cca254c6e4055f65309e7734798e395696`.
This is a regular-file count, not a claim about ZIP directory entries.

## Independent behavioral boundary review

| Scenario | Expected boundary |
| --- | --- |
| Full safe financial analysis | Read-only analysis uses confirmed data, applies the technical-integrity gate before full analysis, and returns the canonical result without authorizing a mutation. |
| Explicit complete financial write | After a fresh `write-preflight`, report, estimate, and complete linked transfer proceed under central MCP confirmation only; no duplicate chat confirmation is added. |
| Ambiguous write | `entity-resolution` / `write-preflight` return the concrete blocker and smallest safe next step; no values are invented and no write occurs. |
| Unknown write outcome | Preserve any receipt, compare fresh server state before the next action, return `частично` or `не завершено`, and never retry blindly. |
| Unfinished result | The only public labels are `частично` and `не завершено`, each immediately followed by reason and smallest safe next step; technical `blocked` remains only in analytics snapshot data. |

No backend code, financial record, or event was changed by this audit.
