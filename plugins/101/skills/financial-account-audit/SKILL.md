---
name: financial-account-audit
description: Use when the user asks how their finances, account, company, project, or object are doing; including vague questions such as "how are things going?" and requests to review financial risks.
version: "1.1.0"
role: primary
invocation: internal
intents:
  - finance.audit
  - finance.risks.review
depends_on:
  - entity-resolution
required_tools:
  - whoami
  - get_company_closing_balance
  - list_projects
  - list_contractors
  - list_events
  - list_contractor_project_balances
optional_tools:
  - get_event
  - list_project_members
  - get_project_fund_settlements
  - list_company_fund_projects
  - list_company_fund_members
  - list_company_fund_expenses_by_bill
  - list_project_bill_balances
  - list_bills
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
    - не завершено
---

# Financial Risk Check

Use this workflow for a narrow request about financial risks, one project, a counterparty, settlements, or an explicit quick text-only check. Route a general company audit, professional statements, or an answer that warrants charts to `company-analytics` before returning the final result.

Work read-only. The technical integrity audit is not a prerequisite for a narrow request. Do not create reports, transfers, events, contractors, articles, or permission changes. Obey `safety-and-permissions.md`: refuse only export or migration of accumulated 101 data into another external service through Codex. Ordinary MCP results and reports created through existing 101 MCP tools remain allowed.

## Boundaries

- Use only data available to the current user. State when access makes the conclusion partial.
- Start with the named project or risk. Open other projects only when they explain a member or counterparty balance.
- Never request or invent external facts absent from 101.
- Base primary totals only on confirmed events. Show drafts separately and offer to estimate their possible impact.
- Read `financial-risks-and-project-controls.md` for duplicate warnings, generic counterparties, and manual service positions. Read `management-reporting-and-balances.md` when interpreting the closing balance or a professional metric.

## Investigation

1. Call `whoami` only if company context is not fixed.
2. For a company-level risk check, call `get_company_closing_balance` first. Assess `closingBalance`, `customerPayment`, `customerRefund`, `fundClosingBalance`, `accountableBalance`, `ownBalance`, and `hasPendingEvents`.
3. Then use `list_projects` and drill into participants, counterparties, events, or expense articles only to explain a material risk. For one project, start directly with that project.
4. Keep project cash, settlements with people and counterparties, and plan versus actual in separate views.
5. Check active project cash and material risks first. If projects are clean, call `list_contractors`; zero project balances do not prove that contractor debt or accountable imbalances are absent. If both are clean, check whether each active project customer is invited when the API exposes that status.
6. An uninvited customer is not a financial emergency. Recommend inviting the customer for transparency and potentially faster inflows.
7. Judge materiality against the project’s confirmed expenses; classify small residues as P3.
8. For a material risk, use available read tools to inspect members, counterparties, events, and articles. Do not explain a cause from one aggregate. Call `list_project_members` only together with `get_project_fund_settlements` for the same `project_guid`; use `finance-and-balances.md` for signs, successful zeros, and partial results.
9. For a large positive or negative member balance, use `list_contractor_project_balances` to check their other available projects.

## Management settlement balance and liquidity

- `closingBalance < 0`: the company needs to receive `abs(closingBalance)` to close confirmed settlements. Delayed accountable returns or other inflows can create liquidity risk: insufficient available cash for current payments.
- `closingBalance > 0`: the company needs to return that amount.
- A negative value does not by itself prove insolvency or that obligations exceed available funds. Make that conclusion only after detailing confirmed obligations and available cash.
- If `hasPendingEvents=true`, warn separately that drafts are excluded and may change the conclusion.

Call this the management settlement balance, not a full accounting balance. It does not include every asset, bank account, loan, or external liability.

## Priorities

- **P0:** confirmed liquidity deficit; current obligations cannot be met without expected inflows. Show the deficit, required inflows, and a direct collection action. Do not create a system request when no such API exists.
- **P1:** cash is available but advances lack confirmed reports. Collect and confirm reports before recommending another advance.
- **P2:** material overpayment or debt with a counterparty without an immediate project threat. An overpayment needs a report or return; a negative balance needs settlement.
- **P3:** small residues and secondary deviations.

Every material deviation needs an action, owner, and evidence. If projects are healthy but counterparties have material debt or overpayments, state that distinction directly. Do not overload a P0 result with P1–P3; offer to repeat the check after P0 is resolved.

## Partner cross-check

Look for accountable balances that can offset across projects. Recommend the option that reduces the overall imbalance with the fewest cross-project transfers. This is a recommendation only; create nothing.

## Response

Lead with a short summary of material risks, then prioritized actions. Say who should do what, for what confirmed amount, and why. Mark uncertainty instead of presenting a hypothesis as fact.

Maintain an evidence ledger with sources, read times, filters, sample boundaries, and values. Show only understandable evidence without GUIDs. Express amounts as rubles, thousands, millions, and similar words without currency codes or symbols. In user-facing text say “company owner,” not “founder.”

After the analytical answer, offer relevant directions for deeper analysis. End with one canonical completion status from frontmatter, the main finding, verified data, and the smallest next step.
