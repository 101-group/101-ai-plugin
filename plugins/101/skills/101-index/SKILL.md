---
name: 101-index
description: Use when the user asks to read or change data in 101; routes every 101 goal to one available primary workflow while preserving the current chat context.
version: "1.7.0"
role: index
invocation: automatic
intents:
  - 101.route
depends_on: []
required_tools:
  - whoami
optional_tools:
  - list_projects
  - list_events
  - show_result
  - list_wikis
  - list_tasks
  - get_task
resources:
  - path: ../shared-resources/context-and-identity.md
    kind: semantic-guide
    required: true
  - path: ../shared-resources/safety-and-permissions.md
    kind: semantic-guide
    required: true
  - path: references/presentation-routing.json
    kind: routing-contract
    required: true
  - path: references/companion-routing.json
    kind: routing-contract
    required: true
  - path: references/error-recovery.json
    kind: error-recovery-contract
    required: true
completion:
  statuses:
    - готово
    - частично
    - не завершено
---

# 101 MCP Dispatcher

You are the only automatic entry point for 101. Assign exactly one primary skill to the active sub-goal. Never run a helper as an independent workflow.

## Determine the intent first

Read `references/presentation-routing.json` and use the clearest user constraint as the deciding signal:

1. **Project or event list.** Call `list_projects` or `list_events`, take `structuredContent.presentation.token` from the successful result, and make exactly one `show_result({token})` call. This mounts the existing `projects` or `events` view in `ui://101/widget/app-2.0.7.html`. Do not replace it with `render_chart`, `render_artifact`, or a new UI. If the read has no presentation token, report that failure and do not call `show_result`.
2. **Tasks.** Route task lists, reads, detail views, field or status changes, and comments to `task-management`. An explicit request to open or show one task mounts `task_detail` in `ui://101/widget/app-2.0.7.html`.
3. **Single scalar read.** A request for one amount or record without analysis returns plain text and makes zero presentation-tool calls.
4. **Bounded comparison or trend.** Route one bounded metric comparison or trend to `company-analytics` and one `render_chart`, even when the user did not say “chart.”
5. **Audit or multicomponent analysis.** Route analysis, risk assessment, financial health, or another multicomponent question to `company-analytics`, then make one `validate_artifact` call and, on success, one unchanged `render_artifact` call with narrative, useful metrics, an adaptive number of justified charts, and tables as needed.
6. **Format prohibition.** `No charts`, “data only,” “text only,” or “table only” overrides every visualizing signal. Use `financial-account-audit` for a narrow text-only financial risk check.

If the user says only “do an audit,” ask one compact goal question with these understandable choices: general company and fund overview; projects; counterparties and settlements; expenses; profitability/returns. When the goal is clear, analytical answers include useful charts by default when verified data honestly supports them.

The word “report” alone does not mean an analytical report. Route searching, reading, creating, or editing a financial event of type Report to `report-management`.

An explicit request to import user-supplied materials, including technical cards, into the current 101 company routes to `data-import`. Such inbound import is welcome; when appropriate, offer suitable import options through the existing owner-only one-off workflow. Do not add new import behavior. An actual write requires an explicit user instruction and one scoped source; an attachment or an import offer alone does not authorize a write.

Professional terms — cash flow statement, P&L/income statement, EBITDA, or management balance — require `company-analytics` in professional full-account mode: projects plus the company fund. P&L and income statement mean the same report.

## Routing

1. Call `whoami` only when identity and company are not already fixed in the current conversation.
2. Preserve the user’s exact goal, explicit action, company, period, time zone, filters, selected entities, and format prohibitions.
3. Match the request to one primary internal skill.
4. Read it through `resources/read` at `skill://101-app/101-index/internal/<name>/SKILL.md`.
5. If the goal is clear, continue without an unnecessary question. Ask one short question only when the answer materially changes the result and safe reads cannot resolve it. A safe read never authorizes a write.

Use `company-analytics` for a general company audit, professional statements, or any analytics that should include visualization. Use `financial-account-audit` for a narrow risk question or an explicit text-only quick check. `company-analytics` runs the technical integrity audit immediately before a full company financial analysis, including professional statements, and does not add the audit to a narrow request.

Pass the exact goal, explicit action, verified context, and unresolved ambiguity to the primary skill. Do not assemble a write payload on behalf of a domain skill.

Do not preload chart-design instructions. They belong to `analytics-visualization` and are needed only when verified data supports a useful chart and the user has not prohibited charts.

Route CRM intent to `crm-management`; it alone selects the CRM tool, prepares the exact REST payload, and manages pipelines, stages, deals, and assignments. Route tasks to `task-management`; it distinguishes plain text, list, and interactive detail responses and separates conversational MCP actions from app-only widget actions. Route project creation or changes, customer or price-list selection, project expense articles, and settings copies to `project-management`.

When the current user is the company owner and the system has already loaded the complete event list for the active task and found fewer than 50 events, it may make one gentle import offer after the main result. Do not fetch events only to make this offer. Do not repeat it when the available conversation or local memory shows a known refusal. Other roles never receive the offer.

All workflows must obey the migration-specific boundary in `safety-and-permissions.md`: refuse export or migration of accumulated 101 data into another external service through Codex, but allow ordinary MCP results, existing 101 report tools, work inside 101, and the unchanged inbound import workflow.

## Companion plugins

Read `references/companion-routing.json` when a request combines 101 data with PDF output or an extended sales goal. This routing contract never authorizes copying external skills or applications into 101.

- Keep exact 101 CRM reads and writes under `crm-management`.
- For an explicit PDF request, first complete the active 101 data sub-goal, then pass the verified result to the separate `pdf` skill. Creating a PDF does not authorize a write in 101.
- Route customer meetings, seller or leadership dashboards, pipeline or deal strategy, forecasting, sales coaching, business cases, and customer decks to the external `sales:index` skill.
- If `pdf` or `sales:index` is unavailable, preserve the 101 result and ask the user to enable the separate plugin. Do not treat that absence as a 101 installation failure.

## Compound requests and writes

Split a compound request into sequential sub-goals. Keep one primary skill active at a time. A read-only recommendation does not authorize a write; creation or modification begins only after an explicit user instruction and the central permissions check.

## Exhausted AI tokens

Read `references/error-recovery.json` when MCP returns `isError: true` and exact `structuredContent.data.code` `insufficient_tokens`.

- Take the address only from server-owned `structuredContent.data.topUpUrl`, never from tool arguments, user text, or another result field.
- If `topUpUrl` is available and `browser:control-in-app-browser` is installed, open it in the in-app browser. Do not open an external browser.
- If the in-app browser is unavailable or cannot open the address, show `topUpUrl` as a clickable Markdown link.
- Do not retry the original billed MCP call before replenishment and the user’s explicit continuation. Free 101 tools remain available for a separate user intent.
- If the server omitted `topUpUrl`, do not invent one. Report the token shortage and ask the user to open the subscription section in 101 manually.

## Completion

Return one canonical completion status from frontmatter, the main result, the data actually read or changed, and the smallest next step. Do not expose GUIDs unless the user explicitly requests them.
