---
name: event-positions
description: Use when an internal report or estimate workflow must resolve price-list, estimate-derived, or manual positions and preserve their startDate and endDate through the existing event API.
version: "1.0.0"
role: helper
invocation: internal
intents:
  - events.positions.prepare
  - events.positions.edit
depends_on:
  - entity-resolution
  - write-preflight
required_tools:
  - get_event
  - list_project_estimate_positions
optional_tools:
  - list_price_lists
  - get_price_list
resources:
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
    - заблокировано
---

# Event Position Preparation

This helper prepares positions for `report-management` and `estimate-management`. It never creates an event itself.

## Sources

- For a price-list position, select a price list through `list_price_lists` when needed, call `get_price_list` with `price_list_id`, and use its complete categories and positions. Do not invent separate category or position search calls.
- For an estimate-derived position, use `list_project_estimate_positions` and preserve its API source.
- For a manual position, pass the explicit name, unit, quantity, price, and all other required fields without an invented price-list reference.

Take `startDate` and `endDate` only from the explicit request or an existing position. When the API allows `null`, do not inherit dates from the event, project, neighboring row, or current day.

## Create and edit

For a new event, build the list in the exact create-tool format. For a targeted edit, first call `get_event`, take the complete fresh list, change only the explicitly named fields of the target position, and build the complete resulting list. Preserve all other positions, sources, and dates.

Immediately before an edit, pass the result to `write-preflight`. If the target position, list composition, or required neighboring data changed from the baseline snapshot, return a conflict and write nothing. Do not auto-merge or send one row as a nonexistent partial patch.
