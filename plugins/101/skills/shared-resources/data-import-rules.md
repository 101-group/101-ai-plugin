# One-off Data Import Rules

## Authority and scope

- Only the company owner may start any import. Pin one current target company from `whoami` and require `is_owner=true`; do not switch companies within a run.
- Start only from an explicit import request. This is a one-off import, never background synchronization. The offer does not authorize a write, and absence from the source never authorizes deletion from 101.
- Apply the current API permissions, machine schema, `entity-resolution`, `write-preflight`, and central MCP confirmation policy before every write.

## Sources and tables

- Use chat files, permitted connected applications, official exports, or authorized APIs. When none is available, ask for an export or attachment.
- Do not use browser automation to control a third-party website for data transfer.
- Parse a simple CSV directly. Use the separately installed Spreadsheets skill to read and normalize a complex Excel or other complex table. Do not copy that skill into 101; if unavailable, offer installation.
- Use the source file only as input. Do not upload it into 101, and do not analyze or import nested legacy attachments.

## Entity routing and dependency blocks

- Recognize any 101 entity. Route it to the current profile skill and exact existing MCP/REST tool. If no supported write tool exists, explain the limitation and do not simulate a successful import.
- Build a numbered dependency plan. The default project block contains one project plus its expense articles, counterparties, and events. Resolve shared company entities once and reuse them across project blocks.
- Independent unambiguous blocks may proceed after their own complete preflight and confirmation. Hold any dependent block whose meaning, relationships, or content could change after an unresolved choice.

## Matching and existing records

- Accept automatically only an exact unambiguous match in the target company. When no match exists, offer creation. For partial, similar, or multiple matches, show human context and ask the company owner to choose.
- Reuse or skip a proven identical record. Never update an existing record automatically. Show every difference and require separate explicit confirmation before an update.
- A repeated import is a new run with new matching, comparison, and confirmations.

## Estimates, reports, and positions

- Resolve the target project for an imported estimate from the file and fixed context. Ask when missing or ambiguous.
- Classify rows by headings and meaning, match expense articles, and split logical stages. Preview the structure, then create separate estimates through sequential single-record calls to `create_estimate`; never invent a batch payload.
- Preserve available dates, amounts, units, and valid sources. Create historical report positions as manual positions without artificial `sources`, estimates, or price lists. Explicit import of an estimate or price list is a separate route.
- If a complete position list disagrees with the source total, show the source total, recomputed total, and correction; save only after confirmation. If completeness is not proven, stop instead of adding a synthetic adjustment row.

## Dates, starting balances, and company fund

- Use the operation date from the source. Never substitute the import date, file date, or current date. Resolve a missing or ambiguous date with the company owner before writing.
- Never invent missing history for a starting balance or debt. Offer either a reference-only note or a separately agreed starting event with explicit type, date, counterparty, and relationships.
- Put semantically general company expenses and inflows in a separate company fund block after explaining the classification. When project versus company fund is ambiguous, stop and ask. A project to fund or fund to project transfer requires both sides to be resolved.

## Unsupported fields, people, and tags

- For each unsupported field, show examples and the affected block, then offer: preserve important meaning in a description, map it to another 101 entity, or skip it. Do not choose automatically.
- Never auto-invite people, assign roles, or change permissions. A financial counterparty does not automatically become an invited member.
- Offer an existing or new `Import` tag once, and apply it only after consent and through an available normal operation. Otherwise do not add technical markers to record content.

## Preview, confirmation, and verification status

- Keep each preview minimal but sufficient: target company/project, affected counts, key amounts, every correction, conflict, ambiguity, and consequence.
- Obtain explicit confirmation for the complete dependent block before writes. This does not replace central MCP confirmation where the tool requires it.
- Current financial create tools create `NOT_VERIFIED` events and do not accept a verification status. No bulk confirmation operation exists. State that imported events are **not verified**, must follow the ordinary 101 confirmation process, and do not yet belong in confirmed balances or financial audits.

## Receipts, recovery, and completion

- After each API call, record one status: `created`, `not created`, `not started`, or `outcome unknown`, and preserve successful receipts.
- Continue from the ledger within the same conversation. After context loss, request the source again and reread 101: skip proven identical records, create proven missing records, and show similar, changed, or unknown-outcome items before any retry.
- Finish with a project-block ledger covering created, confirmed changes, reused/skipped, not created, not started, and unknown outcomes.
- There is no automatic rollback. Corrections after a write use separate ordinary 101 actions.
