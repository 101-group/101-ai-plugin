---
name: estimate-management
description: Use when an internal 101 goal must find, read, create, or edit one or many estimates through the existing event API, including sourced or manual positions and their dates.
version: "1.0.0"
role: primary
invocation: internal
intents:
  - estimates.list
  - estimates.read
  - estimates.create
  - estimates.edit
depends_on:
  - entity-resolution
  - write-preflight
  - event-positions
required_tools:
  - whoami
  - list_events
  - get_event
  - create_estimate
  - edit_estimate
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

# Estimate Management

Run only as the primary skill selected by `101-index`. An estimate uses existing estimate tools and their original API contract; never create another event type or MCP-only payload.

## Search and read

Resolve the company, project, and other named entities through `entity-resolution`. Use `list_events` with server filters and pagination for a list and `get_event` for details. Never treat the first page as the complete set or expose GUIDs without an explicit request.

## One record

For creation, prepare positions through `event-positions`, preserve their sources, `startDate`, and `endDate`, pass the exact create payload to `write-preflight`, and call `create_estimate`.

When the user explicitly requests a complete estimate and every required field is known, proceed after fresh `write-preflight` under the central MCP policy without a second chat confirmation.

For an edit, first call `get_event`. Convert a targeted position change through `event-positions` into the complete resulting list while preserving neighboring rows and dates. After a fresh `write-preflight`, call `edit_estimate`. Stop and show a conflict on a concurrent change.

## Estimate series

A bulk request still uses one `create_estimate` call per item, never a new batch payload. Follow the shared sequential queue contract in `events-and-positions.md`.

Use the canonical completion contract from `safety-and-permissions.md`; list created, not created, and not started estimates by human name, show fresh data, and give the smallest next step.
