---
name: company-analytics
description: Use when the user requests source-backed company or project analytics, financial statements, useful charts, or a general 101 audit.
version: "2.2.0"
role: primary
invocation: internal
intents:
  - analytics.company
  - analytics.project
  - analytics.report
depends_on:
  - entity-resolution
required_tools:
  - whoami
  - get_company_closing_balance
  - list_projects
  - list_events
  - list_contractor_project_balances
optional_tools:
  - get_event
  - list_contractors
  - list_project_members
  - get_project_fund_settlements
  - list_company_fund_projects
  - list_company_fund_members
  - list_company_fund_expenses_by_bill
  - list_project_bill_balances
  - list_project_estimate_positions
  - list_bills
  - list_tasks
  - render_chart
  - validate_artifact
  - render_artifact
resources:
  - path: ../shared-resources/context-and-identity.md
    kind: semantic-guide
    required: true
  - path: ../shared-resources/finance-and-balances.md
    kind: semantic-guide
    required: true
  - path: ../shared-resources/safety-and-permissions.md
    kind: semantic-guide
    required: true
  - path: ../shared-resources/technical-integrity-audit.md
    kind: semantic-guide
    required: true
  - path: ../shared-resources/financial-risks-and-project-controls.md
    kind: semantic-guide
    required: true
  - path: ../shared-resources/management-reporting-and-balances.md
    kind: semantic-guide
    required: true
completion:
  statuses:
    - готово
    - частично
    - заблокировано
---

# 101 Company Analytics and Audits

Work read-only against the known 101 contract. Do not rediscover the database or schema, create a parallel metric layer, run an external compute environment, or export raw events when an available aggregate answers the question. Obey `safety-and-permissions.md`; in particular, refuse any request to transfer 101 data to a third-party system through browser automation.

## Goal and mode gate

- If the user says only “do an audit,” ask one compact goal question: general company and fund overview; projects; counterparties and settlements; expenses; profitability/returns.
- If the goal is clear, analyze immediately.
- Plain data or a list uses zero presentation-tool calls.
- Analytics includes useful charts by default when verified data honestly supports them. An explicit “chart,” “visualize,” “show the trend,” or “interactive” request also enables visualization.
- Explicit format prohibition overrides every visualization signal: `No charts`, “data only,” “text only,” or “table only” disables visualization.
- Professional terms — cash flow statement, P&L/income statement, EBITDA, or management balance — require professional full-account analysis: projects plus the company fund. Cash flow, P&L, and the management balance form the classic three-statement set; P&L and income statement are the same report.
- Give a non-professional user an ordinary management overview from the same data. Change the presentation, not the evidence.
- If a standard metric cannot be calculated honestly, name the available management analogue, show its formula, and state its limitations.

## Optional technical integrity check

Before a full company financial analysis, briefly explain the value of structural and arithmetic validation and offer the technical integrity audit. This includes a general audit, a full management overview, and professional cash flow, P&L/income statement, EBITDA, or management balance work. Do not start technical reads before the user agrees. Do not make this offer before a narrow request about one project, counterparty, expense class, or metric.

If the user agrees, read `technical-integrity-audit.md`, fully read all event pages plus every necessary event detail, and apply its blocking rules. If a page, detail, structural link, distribution, or arithmetic check fails, stop the full financial analysis and return the issues and recommendations without changing data.

If the user declines, continue the financial analysis immediately from the available data. State in the result that technical integrity was not checked, so the conclusions may inherit errors in the underlying records.

After the gate passes, read only the references required by the selected mode:

- `financial-risks-and-project-controls.md` for drafts, duplicate warnings, contractor quality, and manual service positions;
- `management-reporting-and-balances.md` for accrual P&L, cash flow, EBITDA, fund expense classification, large purchases, owner reporting, and the management settlement balance.

For a superficial general audit, show a short company/fund overview and the project portfolio. Drill into settlements or expenses only when a risk warrants it, and offer deeper analysis before adding detail.

## Data access without unnecessary discovery

1. Use the fixed company. Call `whoami` and `entity-resolution` only when context is missing or ambiguous.
2. Use `get_company_closing_balance` for the current management settlement balance, following `management-reporting-and-balances.md`.
3. Use `list_projects` for the project portfolio and drill into only the metric needed for the goal. Call `list_project_members` only together with `get_project_fund_settlements` for the same `project_guid`; use `finance-and-balances.md` for signs, successful zeros, and partial results.
4. For ordinary aggregate metrics, use `list_events` with `with_totals=true`, `per_page=0`, exact `company_guid`, period, and `status=[partner_verified, client_accepted]`. Do not export raw events when `totals` or `balanceTotals` answers the question. Full event pagination is required only when the user accepts the optional technical integrity check before a full company financial analysis.
5. For a time series, split the period into non-overlapping intervals and make one aggregate call per interval. Use the requested grain; otherwise choose the coarsest honest grain with at most 12 intervals. Use the requested time zone, defaulting to Europe/Moscow.
6. Never mix confirmed and unconfirmed events. Keep drafts outside the primary totals and offer a separate impact scenario.

Keep projects and the company fund as separate contours. A direct Company Fund Inflow is external financing or investment for company expenses, never revenue or profit. Project ↔ fund transfers are internal and do not create income or expense again when consolidated.

Compare like units, periods, signs, and grains. Call a movement a cause only with direct evidence; otherwise label it a hypothesis. In user-facing text say “company owner,” not “founder”; the technical role may remain `owner`. Express amounts as rubles, thousands, millions, and similar worded magnitudes without currency codes or symbols.

## Visualization contract

Read `analytics-visualization` only after the mode gate allows visualization. One `render_chart` serves a focused standalone chart. A broader audit uses one composite artifact; do not split one audit into independent `render_chart` calls.

Adapt the number and type of charts to the question and the available honest data. Include only useful charts; no fixed chart count is a success criterion. Pass bounded aggregated datasets and truthful `source`/`manifest.sources[]` metadata with strict `executedAt` and safe filters from the actual MCP call, without GUIDs. Call one `validate_artifact` and, on success, pass the unchanged payload to one `render_artifact`. Do not repeat a successful presentation call.

Immediately after each audit chart, add a short chart-specific finding and a concrete chart-specific recommendation grounded in that chart's data. After all charts, add a separate overall audit conclusion and separate general recommendations, including useful follow-up checks and directions for deeper analysis. Local chart guidance and the overall blocks are both required and do not replace each other.

Local changes to chart type, grouping, filters over already loaded rows, layout, labels, or table mode run inside the React runtime without a new MCP call. A new company, period, metric, or dataset requires a new business fetch, snapshot, and validation.

## Response

Lead with the answer, then give key numbers, findings or risks, limitations, and concrete actions. Separate facts from hypotheses. Include useful charts by default when the data supports them and no format prohibition applies. After every analytical answer, offer relevant directions for deeper analysis based on the observed data and risks.

Do not expose GUIDs unless explicitly requested. Do not claim a chart or report rendered if the presentation tool failed. Any mutation requires explicit confirmation and the permissions check.
