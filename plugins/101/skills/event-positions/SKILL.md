---
name: event-positions
description: Use when an internal report or estimate workflow must resolve price-list, estimate-derived, or manual positions through the existing event API.
version: "1.0.0"
role: helper
invocation: internal
intents:
  - events.positions.prepare
  - events.positions.edit
depends_on:
  - entity-resolution
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
    - не завершено
---

# Event Position Preparation

This helper prepares positions for `report-management` and `estimate-management`. It never creates an event itself, and it does not own preflight, shared queue execution, or confirmation policy.

## Sources

- For a price-list position, select a price list through `list_price_lists` when needed, call `get_price_list` with `price_list_id`, and use its complete categories and positions. Do not invent separate category or position search calls.
- For an estimate-derived position, use `list_project_estimate_positions` and preserve its API source.
- For a manual position, pass the explicit name, unit, quantity, price, and all other required fields without an invented price-list reference.

Shared rules for source preservation, `startDate`, `endDate`, full-list edits, conflict handling, and sequential queue execution live in `events-and-positions.md`.

## Create and edit

For a new event, build positions in the exact create-tool format expected by the primary skill. For a targeted edit, first call `get_event`, resolve the requested position changes, and return the exact resulting position data the primary skill must place into the full payload.
