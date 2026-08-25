---
name: settlements-and-transfers
description: Use when the user asks to settle a person, pay a debt, transfer money, or close a balance on a project.
version: "1.0.0"
role: primary
invocation: internal
intents:
  - settlements.calculate
  - transfers.create
depends_on:
  - entity-resolution
  - write-preflight
required_tools:
  - whoami
  - list_projects
  - list_contractors
  - list_contractor_project_balances
  - create_payment
optional_tools:
  - search_users
  - list_project_members
  - get_project_fund_settlements
  - get_event
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
completion:
  statuses:
    - готово
    - частично
    - не завершено
---

# Settlements and Transfers

Use this skill only for a direct action request such as “settle Alex,” “transfer money,” or “close the debt.” Do not run it for a general financial audit.

## Before proposing an action

1. Resolve the user and access through `whoami`.
2. Find the participant and project. If either is ambiguous, show options and ask the user to choose; never guess.
3. Read confirmed participant balances on the selected project. Keep own and accountable balances separate. Call `list_project_members` only together with `get_project_fund_settlements` for the same `project_guid`; follow `finance-and-balances.md` for signs, zeros, and partial results.
4. Ask a precise question when required event data is missing. Do not create a draft or substitute values.
5. Before creation, apply `write-preflight`: check the current create-tool schema and use the original API contract, camelCase fields, required data, and `fileList` when attachments exist.

## Proposing a participant settlement

- For a negative own balance, propose an external transfer for the amount owed to the participant.
- For a negative accountable balance, propose a separate accountable transfer.
- When both are negative, show two separate transfers but request one explicit confirmation for the linked pair.
- When accountable balance is positive and own balance is negative, calculate available self-coverage. Explain the amount the participant should transfer internally, and propose only the remaining external transfer. Do not create a self-transfer for another participant.
- Insufficient project cash does not automatically block an external transfer. Warn that it creates or increases a deficit, require explicit confirmation, then recommend collecting money from the customer. Do not create a collection request because no such API exists.

## Plan and create

A read-only recommendation is not write authorization. Start creation only after an explicit action instruction.

For multiple linked transfers, first show a clear plan: recipient, project, amounts, balances closed, and deficit consequence. After successful `write-preflight`, make sequential individual API calls. Use only central MCP confirmation policy; do not add another layer or bypass the standard flow.

When the user explicitly requests the complete linked pair and every required field is known, proceed after fresh `write-preflight` under the central MCP policy without a second chat confirmation.

Preserve the API receipt after every creation and reread balances after a series. On an error or uncertain outcome, do not claim creation and do not retry automatically.

Use the canonical completion contract from `safety-and-permissions.md`; list created and not-created events by human name, show the fresh balance, and give the smallest next step.
