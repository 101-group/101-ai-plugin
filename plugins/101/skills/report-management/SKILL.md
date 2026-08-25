---
name: report-management
description: Use when an internal 101 goal must find, read, create, or edit one or many expense reports through the existing event API, including sourced or manual positions and their dates.
version: "1.0.0"
role: primary
invocation: internal
intents:
  - reports.list
  - reports.read
  - reports.create
  - reports.edit
depends_on:
  - entity-resolution
  - write-preflight
  - event-positions
required_tools:
  - whoami
  - list_events
  - get_event
  - create_expense
  - edit_expense
optional_tools:
  - list_projects
  - list_bills
  - list_contractors
  - upload_files
resources:
  - path: ../shared-resources/context-and-identity.md
    kind: semantic-guide
    required: true
  - path: ../shared-resources/events-and-positions.md
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

# Expense Report Management

This workflow manages financial events whose product label is `Отчёт`. Send a request for company or project management analytics to `company-analytics`; do not create an event merely because the user said “report.”

Run only as the primary skill selected by `101-index`. `Отчёт` uses existing expense tools and their original API contract; never create another event type or MCP-only payload.

Do not render charts for report CRUD. Return an explicit analytical request to the dispatcher for routing to `company-analytics`.

## Search and read

Resolve the company, project, and other named entities through `entity-resolution`. Use `list_events` with server filters and pagination for a list and `get_event` for details. Never treat the first page as the complete set or expose GUIDs without an explicit request.

## One record

For creation, prepare positions through `event-positions`, preserve their sources, `startDate`, and `endDate`, pass the exact create payload to `write-preflight`, and call `create_expense`.

When the user explicitly requests a complete report and every required field is known, proceed after fresh `write-preflight` under the central MCP policy without a second chat confirmation.

For an edit, first call `get_event`. Convert a targeted position change through `event-positions` into the complete resulting list while preserving neighboring rows and dates. After a fresh `write-preflight`, call `edit_expense`. Stop and show a conflict on a concurrent change.

## Report series

A bulk request still uses one `create_expense` call per item, never a new batch payload. Follow the shared sequential queue contract in `events-and-positions.md`.

Use the canonical completion contract from `safety-and-permissions.md`; list created, not created, and not started reports by human name, show fresh data, and give the smallest next step.
