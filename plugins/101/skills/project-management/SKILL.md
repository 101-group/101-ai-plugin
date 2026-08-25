---
name: project-management
description: Use when an internal 101 goal must create or edit a project, select its customer or price list, manage project expense categories, or copy category settings from another project.
version: "1.0.0"
role: primary
invocation: internal
intents:
  - project.create
  - project.edit
  - project.bill.manage
  - project.bill.copy
depends_on:
  - entity-resolution
  - write-preflight
required_tools:
  - whoami
  - create_project
  - edit_project
  - create_bill
  - edit_bill
  - list_bill_duplication_sources
  - duplicate_bills
optional_tools:
  - search_users
  - list_projects
  - list_bills
  - list_price_lists
  - get_price_list
resources:
  - path: ../shared-resources/context-and-identity.md
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

# Project Management

Run as the primary internal skill selected by `101-index`. Create and edit projects and their expense articles one-to-one with current REST contracts; always take field names, types, and requirements from the tool's machine schema.

## Project

1. Fix the company through `whoami`. Resolve the customer through `search_users` and an existing project through `list_projects`; never guess a GUID.
2. Select a price list through `list_price_lists` and, when needed, `get_price_list`; pass it as `priceListId` to `create_project` or `edit_project`.
3. Before writing, apply `entity-resolution` and `write-preflight`. Use `create_project` for creation and only `edit_project` for partial changes. Do not simulate the edit GET form.

## Expense articles

- Read current articles through `list_bills`. Create a project article through `create_bill` and edit it through `edit_bill`; company-fund articles and deletion are outside this workflow.
- Copy only after project creation: first call `list_bill_duplication_sources` with the target project GUID, then `duplicate_bills` with the exact legacy payload `{project_guid, bill_guids}`.
- `billGuids` links existing articles to a project, while `duplicate_bills` creates new copies. Do not mix these actions.

Do not create a composite tool, parallel API contract, or duplicate search. Each of the five write calls runs once after complete preflight and without an extra confirmation layer; normal OAuth scopes, domain validation, and central policy remain mandatory.

Use the canonical completion contract from `safety-and-permissions.md`; return the human project name, selected customer and price list, changed articles, API receipts, and the smallest next step. Show GUIDs only on explicit request.
