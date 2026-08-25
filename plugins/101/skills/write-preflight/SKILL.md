---
name: write-preflight
description: Use when an internal 101 write workflow must validate the current tool schema, required data, entity references, mutable state, and central policy before one API-backed mutation.
version: "1.0.0"
role: helper
invocation: internal
intents:
  - writes.preflight
depends_on:
  - entity-resolution
required_tools:
  - whoami
optional_tools: []
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

# Write Preflight

This helper neither owns the user's goal nor authorizes an action. It returns either the exact payload for an existing MCP/API tool or a concrete blocker.

## Input

Receive the explicit user intent, write-tool name, selected entities, baseline snapshot of mutable data, and proposed fields from the primary skill.

## Checks

1. Read the selected tool's fresh machine schema and preserve its original field names, types, and requirements. Do not create an MCP-only format.
2. Verify that the user explicitly instructed this write. A read-only recommendation is not authorization.
3. Use `entity-resolution` to verify required references and their accessibility in the current company.
4. Reread only the affected mutable state and current permissions immediately before the call.
5. For a full-list payload, compare the fresh snapshot with the baseline. Write nothing on conflict.
6. Apply the central MCP confirmation and risk policy. Do not add a separate confirmation layer or weaken the standard one.

## Output

On success, return the tool name, exact payload, fresh values read, and readiness basis to the primary skill. For any missing or ambiguous required part, return `не завершено`, the exact reason, and the smallest next step. Never substitute values merely to pass API validation.
