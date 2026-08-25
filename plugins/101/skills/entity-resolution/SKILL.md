---
name: entity-resolution
description: Use when an internal 101 workflow must resolve a user, company, project, contractor, event, Wiki, page, task, bill, or price-list entity from human wording.
version: "1.0.0"
role: helper
invocation: internal
intents:
  - entities.resolve
depends_on: []
required_tools:
  - whoami
optional_tools:
  - search_users
  - list_projects
  - list_contractors
  - list_events
  - list_wikis
  - list_tasks
  - list_bills
  - list_price_lists
resources:
  - path: ../shared-resources/context-and-identity.md
    kind: semantic-guide
    required: true
completion:
  statuses:
    - готово
    - частично
    - заблокировано
---

# Entity Resolution

This helper does not own the user's goal. Receive the entity type, human description, and already fixed context from the primary skill.

1. Start with `whoami` when the user or company is not yet known.
2. Use the narrowest existing search/list tool and server-side filters.
3. Return one exact match to the primary skill automatically.
4. When multiple matches exist, stop the dependent operation and show one compact list of understandable names with enough context for a choice.
5. Never guess from a partial match or select the first result merely because of result order.
6. Do not expose a GUID in an ordinary answer. Keep it only as a technical reference in context and the evidence ledger.

When access or search cannot prove a unique match, return the exact blocker and the smallest next question. Never replace a missing entity with a guess.
