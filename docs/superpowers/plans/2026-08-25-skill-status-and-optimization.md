# 101 Skill Status and Optimization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish a smaller, unambiguous 101 skill package whose user-facing completion status is `не завершено`, whose safe steps do not pause for redundant questions, and whose explicit financial writes rely only on central MCP confirmation.

**Architecture:** Keep `safety-and-permissions.md` as the common policy owner and `events-and-positions.md` as the shared financial-event queue owner. Primary skills retain only routing and domain-specific payload rules; helper dependencies are removed where they no longer own a write. Contract tests validate all frontmatter and resource edges, while independent pressure tests validate the instruction behavior.

**Tech Stack:** Markdown Agent Skills, JSON/YAML plugin metadata, Python `unittest`, ZIP release archive, Codex Marketplace CLI.

**Spec:** `docs/superpowers/specs/2026-08-25-skill-status-and-optimization.md`

## Global Constraints

- User-facing statuses are exactly `готово|частично|не завершено`; the next line after `частично` or `не завершено` states the reason and smallest safe next step.
- Preserve technical `snapshot.status=ready|partial|blocked|fixture` exactly.
- Safe reads, searches, calculations, preparation, exact matching, and unambiguous steps run without a conversational gate.
- An explicit complete financial-event request receives no extra chat confirmation; only central MCP confirmation may apply.
- Preserve OAuth, scopes, risk flags, idempotency, unknown-outcome handling, fresh-state conflict checks, receipts, and no-blind-retry protection.
- Do not combine distinct domain contracts merely to reduce words.
- Do not change backend code or create financial data/events.
- Public plugin name and IDs remain unchanged; release version advances from `2.2.1` to `2.2.2` only after verification.

---

### Task 1: Canonical completion and safe-action policy

**Files:**
- Create: `tests/test_skill_behavior_contract.py`
- Modify: `plugins/101/skills/*/SKILL.md`
- Modify: `plugins/101/skills/shared-resources/safety-and-permissions.md`
- Modify: `plugins/101/skills/101-index/SKILL.md`
- Modify: `plugins/101/skills/company-analytics/SKILL.md`
- Modify: `tests/test_analytics_skills.py`

**Interfaces:**
- Consumes: all 16 current skill frontmatters and the technical analytics contract.
- Produces: one shared user-facing completion and safe-action policy used by later task-specific instructions.

- [ ] **Step 1: Add failing frontmatter and technical-boundary tests**

```python
def test_every_skill_uses_the_user_completion_contract():
    for skill_path in SKILLS.glob('*/SKILL.md'):
        assert completion_statuses(skill_path) == (
            'готово', 'частично', 'не завершено'
        )

def test_analytics_blocked_status_remains_technical():
    assert 'ready|partial|blocked|fixture' in analytics_skill
    assert 'ready|partial|blocked|fixture' in chart_design
```

- [ ] **Step 2: Add failing policy-shape tests**

```python
def test_shared_policy_runs_safe_steps_and_formats_unfinished_results():
    policy = read_skill_resource('safety-and-permissions.md')
    assert safe_action_contract(policy)
    assert immediate_follow_up_contract(policy)
    assert central_financial_confirmation_contract(policy)
```

- [ ] **Step 3: Run RED**

Run: `python3 -m unittest tests.test_skill_behavior_contract tests.test_analytics_skills -v`

Expected: failures name the old `заблокировано` statuses, optional technical-audit question, and missing immediately-following-line rule.

- [ ] **Step 4: Implement the minimal shared contract**

Update every completion list; centralize safe-action, question, financial-confirmation, and result-line rules in `safety-and-permissions.md`. Change full-company technical-integrity work from an optional conversational gate to an immediate safe read owned by `company-analytics`. Preserve the four technical analytics statuses verbatim.

- [ ] **Step 5: Run GREEN**

Run: `python3 -m unittest tests.test_skill_behavior_contract tests.test_analytics_skills -v`

Expected: all Task 1 tests pass.

- [ ] **Step 6: Commit**

```bash
git add tests plugins/101/skills docs/superpowers
git commit -m "Обновить итоговые статусы и безопасные шаги 101"
```

### Task 2: Financial-event and helper context optimization

**Files:**
- Modify: `tests/test_skill_behavior_contract.py`
- Modify: `plugins/101/skills/shared-resources/events-and-positions.md`
- Modify: `plugins/101/skills/report-management/SKILL.md`
- Modify: `plugins/101/skills/estimate-management/SKILL.md`
- Modify: `plugins/101/skills/event-positions/SKILL.md`
- Modify: `plugins/101/skills/settlements-and-transfers/SKILL.md`
- Modify: `plugins/101/skills/write-preflight/SKILL.md`
- Modify: `plugins/101/skills/task-management/SKILL.md`

**Interfaces:**
- Consumes: Task 1 central confirmation and completion policy.
- Produces: one shared sequential-event queue contract, one preflight per write, and helper-owned attachment routing.

- [ ] **Step 1: Add failing ownership and no-extra-confirmation tests**

```python
def test_event_queue_has_one_shared_owner():
    assert shared_event_queue_contract(events_resource)
    assert report_references_shared_queue_once(report_skill)
    assert estimate_references_shared_queue_once(estimate_skill)

def test_complete_financial_writes_do_not_add_chat_confirmation():
    for source in (report_skill, estimate_skill, settlements_skill, preflight_skill):
        assert no_parallel_confirmation_gate(source)

def test_position_helper_does_not_repeat_write_preflight():
    assert 'write-preflight' not in depends_on(event_positions_skill)
```

- [ ] **Step 2: Run RED**

Run: `python3 -m unittest tests.test_skill_behavior_contract -v`

Expected: failures show duplicated report/estimate queues, the position helper's duplicate preflight dependency, and ambiguous transfer confirmation wording.

- [ ] **Step 3: Consolidate shared event execution**

Move queue-wide validation, per-item fresh preflight, one-call writes, local/system failure branches, receipts, continuation, and unknown-outcome protection into `events-and-positions.md`. Replace both primary copies with their exact create-tool specialization.

- [ ] **Step 4: Remove duplicate helper work**

Keep position source/date/full-list semantics in the shared event resource; leave only tool-specific price-list and estimate resolution in `event-positions`. Remove its `write-preflight` dependency and second preflight instruction. Route conversational task attachments through `file-handling` rather than declaring a direct upload transport.

- [ ] **Step 5: Clarify financial writes**

State that an explicit complete report, estimate, or transfer instruction proceeds after fresh preflight under central MCP policy. Preserve questions for missing/ambiguous fields, fresh-state conflicts, irreversible effects, unknown outcomes, and material choices not already made by the user.

- [ ] **Step 6: Run GREEN and full skill tests**

Run: `python3 -m unittest tests.test_skill_behavior_contract tests.test_analytics_skills tests.test_plugin_manifest -v`

Expected: all tests pass.

- [ ] **Step 7: Commit**

```bash
git add tests plugins/101/skills
git commit -m "Сократить инструкции финансовых событий 101"
```

### Task 3: Full audit, package, and patch release candidate

**Files:**
- Create: `docs/audits/2026-08-25-skill-status-and-optimization.md`
- Modify: `tests/test_skill_behavior_contract.py`
- Modify: `tests/test_plugin_manifest.py`
- Modify: `plugins/101/.codex-plugin/plugin.json`
- Modify: `README.md`
- Modify: `downloads/101-skills.zip`

**Interfaces:**
- Consumes: Tasks 1-2 final skill tree and baseline size `14,679 words / 1,632 lines` across skill Markdown.
- Produces: audited `2.2.2` Marketplace package and exact before/after evidence.

- [ ] **Step 1: Add failing graph and version tests**

```python
def test_all_dependencies_and_resources_resolve():
    assert dependency_graph_errors() == []
    assert resource_link_errors() == []

def test_patch_release_is_222():
    assert manifest_version() == '2.2.2'
    assert readme_version() == '2.2.2'
```

- [ ] **Step 2: Run RED**

Run: `python3 -m unittest tests.test_skill_behavior_contract tests.test_plugin_manifest -v`

Expected: version assertions fail at `2.2.1`; any stale dependency edge fails with its exact skill name.

- [ ] **Step 3: Complete the audit and version update**

Audit all 16 frontmatters, 16 bodies, 9 shared resources, explicit completion phrases, dependency edges, and resource links. Record removed duplication, retained protections, baseline and final word/line totals, and behavioral RED→GREEN evidence. Update only the public patch version and README references.

- [ ] **Step 4: Rebuild the canonical archive**

Run from `plugins/101/skills`: `zip -q -r -FS -X ../../../downloads/101-skills.zip .`

- [ ] **Step 5: Run full verification**

Run: `python3 -m unittest discover -s tests -p 'test_*.py'`

Run: `git diff --check`

Expected: all tests and archive-mirror checks pass; both worktrees remain free of temporary files.

- [ ] **Step 6: Run independent behavioral and diff review**

Pressure-test a full safe financial analysis, an explicit complete financial write, an ambiguous write, an unknown outcome, and an unfinished result. Require explicit confirmation that technical `blocked`, authorization, risk flags, fresh-state checks, receipts, and no-blind-retry rules remain intact.

- [ ] **Step 7: Commit**

```bash
git add README.md downloads/101-skills.zip plugins/101/.codex-plugin/plugin.json tests docs
git commit -m "Подготовить публичный плагин 101 версии 2.2.2"
```

### Task 4: Public delivery and read-only smoke

**Files:**
- No product-file changes expected after the release candidate passes review.

**Interfaces:**
- Consumes: reviewed `2.2.2` commit and exact rollback `v2.2.1` / `9f06171e54a25aab02c355e1e802ca3a1e02dd06`.
- Produces: merged PR, public tag/release, clean local installation, and a read-only fresh-session proof.

- [ ] **Step 1: Push the feature branch and create a Russian PR**

Run: `git push -u origin holop/skill-status-optimization-20260825`

Create a PR to `main` with audit metrics, RED→GREEN evidence, safety boundaries, and rollback SHA.

- [ ] **Step 2: Verify checks and merge through the normal GitHub process**

Confirm PR mergeability and all available checks. Merge only the reviewed branch; do not force-push `main`.

- [ ] **Step 3: Publish `v2.2.2`**

Create a lightweight tag at the merge commit and a public GitHub release. Preserve `v2.2.1` unchanged as rollback.

- [ ] **Step 4: Clean install and read-only smoke**

Remove only `101@101-marketplace`, upgrade `101-marketplace`, install 101 again, and confirm version `2.2.2`. In a fresh Codex task, perform no 101 MCP calls; ask the installed skill package to state the user-facing statuses, safe-read rule, and explicit-complete-financial-write confirmation rule.

- [ ] **Step 5: Report exact evidence**

Send the coordinator the PR/release URLs, commit/tag, installed version, test counts, before/after size, read-only smoke result, retained protections, and any blockers.
