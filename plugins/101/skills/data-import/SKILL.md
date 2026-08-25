---
name: data-import
description: Use when a company owner explicitly asks to import one-off external data into the current 101 company from files, exports, connected apps, or permitted APIs.
version: "1.0.0"
role: primary
invocation: internal
intents:
  - data.import
depends_on:
  - entity-resolution
  - write-preflight
required_tools:
  - whoami
optional_tools:
  - list_events
  - list_projects
  - list_contractors
  - list_bills
  - list_price_lists
  - get_price_list
  - search_users
resources:
  - path: ../shared-resources/context-and-identity.md
    kind: semantic-guide
    required: true
  - path: ../shared-resources/safety-and-permissions.md
    kind: semantic-guide
    required: true
  - path: ../shared-resources/data-import-rules.md
    kind: semantic-guide
    required: true
completion:
  statuses:
    - готово
    - частично
    - не завершено
---

# One-off Data Import to 101

Run only as the primary skill selected by `101-index` for an explicit import request. This is a conversational one-off import into one current target company, never background synchronization. The offer does not authorize a write. Neither does an attached file or completed parsing.

## Eligibility and source

1. Call `whoami`, pin exactly one current company, and require its returned `is_owner=true`. The user-facing role is **company owner**; do not substitute another role label. Other roles are blocked from every import, including project-only imports, even if an individual write tool would otherwise allow them.
2. Read `data-import-rules.md` before parsing or planning. Select the most direct permitted source: a chat attachment, connected application, official export, or authorized API. Never transfer data by controlling a third-party website through browser automation.
3. A simple CSV may be parsed directly. A complex spreadsheet requires the separately installed Spreadsheets skill for reading and normalization. Do not copy Spreadsheets instructions or assets into 101. If it is unavailable, ask the user to install it and preserve the import state already established.

## Classify and route

Recognize the meaning of every supported 101 entity, construct dependency-ordered company and project blocks, and route every recognized 101 entity to an existing primary skill when one covers it. Use its exact profile MCP tool and REST payload. If no dedicated primary skill covers an entity but a current exact profile tool does, apply `entity-resolution`, `write-preflight`, and the same block confirmation rules before using that tool. If no supported write tool exists, state the limitation and do not simulate a successful import.

Typical routes include:

- projects, project expense articles, and project settings to `project-management`;
- estimates and their positions to `estimate-management`;
- expense reports and their positions to `report-management`;
- transfers and settlement actions to `settlements-and-transfers`;
- CRM entities to `crm-management`;
- Wiki data to `wiki-management`;
- any other entity to its current internal primary skill or, only when no skill exists, its exact available profile tool under the same safety gates.

Never invent a batch endpoint, composite payload, missing record, date, relationship, starting-balance history, or rollback operation.

## Conversational execution

Prepare exact unambiguous matches automatically. Ask only about missing, partial, similar, conflicting, unsupported, or irreversible choices. Show a compact preview for each independent block, including the target, affected counts, key amounts, corrections, conflicts, and write consequences. Begin that block only after the company owner explicitly confirms the import preview; then run sequential single-record calls through the selected profile workflow.

Keep a receipt ledger after every call. Never blind-retry an unknown write outcome. Imported financial events remain `NOT_VERIFIED`; do not claim they affect confirmed balances or audits, and disclose that no bulk confirmation contract exists.

Finish with one canonical completion status, a block-by-block ledger, the data created, changed after confirmation, reused, skipped, not created, not started, or left with an unknown outcome, and the smallest safe next step. There is no automatic rollback.
