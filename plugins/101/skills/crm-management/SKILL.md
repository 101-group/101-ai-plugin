---
name: crm-management
description: Use when an internal 101 goal must manage CRM pipelines, stages, deals, or distribution rules through the current CRM API.
version: "1.0.0"
role: primary
invocation: internal
intents:
  - crm.pipeline.manage
  - crm.funnel.manage
  - crm.deal.manage
  - crm.distribution.manage
depends_on:
  - entity-resolution
  - write-preflight
required_tools:
  - whoami
  - list_crm_pipelines
  - create_crm_pipeline
  - reorder_crm_pipelines
  - get_crm_pipeline
  - edit_crm_pipeline
  - delete_crm_pipeline
  - create_crm_funnel
  - reorder_crm_funnels
  - edit_crm_funnel
  - delete_crm_funnel
  - create_crm_deal
  - get_crm_deal
  - edit_crm_deal
  - delete_crm_deal
  - move_crm_deal
  - list_crm_distribution_rules
  - create_crm_distribution_rule
  - get_crm_distribution_rule_schema
  - reorder_crm_distribution_rules
  - edit_crm_distribution_rule
  - delete_crm_distribution_rule
  - list_contractors
  - search_users
optional_tools: []
resources:
  - path: ../shared-resources/context-and-identity.md
    kind: semantic-guide
    required: true
  - path: ../shared-resources/safety-and-permissions.md
    kind: semantic-guide
    required: true
  - path: references/crm-orchestration.md
    kind: semantic-guide
    required: true
completion:
  statuses:
    - готово
    - частично
    - заблокировано
---

# CRM Management

Run only as the primary internal skill selected by `101-index`. Handle pipelines, stages, deals, and distribution rules through the 21 canonical MCP tools. Never create a second dispatcher, CRM widget, or parallel CRM contract.

Before selecting a tool, read the required orchestration contract in `references/crm-orchestration.md`. It defines safe reads, semantic branches, minimal questions, and receipts for all 21 operations. Always take the argument schema from the current tool machine schema rather than examples in the resource.

## Reads and entity resolution

1. Fix the user and company through `whoami` and shared context.
2. Find the pipeline through `list_crm_pipelines`; when several match, ask the user to choose by human name.
3. Treat `get_crm_pipeline` as the canonical detail response for stages, deals, sources, and custom fields. Do not create separate lookup calls for those entities.
4. Reuse `list_contractors` or `search_users` for a deal contact. Never guess `contractorGuid` or expose a GUID without an explicit request.
5. Call `get_crm_distribution_rule_schema` before configuring distribution; take candidates, conditions, and strategies only from this result.

First gather everything that safe reads can prove uniquely. If a required user decision is missing or several entities match, ask one minimal question with understandable choices. Combine tightly related missing parameters into one compact block when separate answers would not enable the action. Before the answer, do not call a write tool or apply an API default that materially changes the result.

## Write contract

Apply `entity-resolution` and `write-preflight`. Pass `payload` one-to-one with the current CRM REST body: do not rename fields, compute permissions, or correct the payload on behalf of the API. Path parameters identify an existing entity; `payload` contains only the corresponding request body.

Ordinary create, edit, move, and reorder operations use one call after complete preflight with no extra confirmation. The narrow exception is AI-generated distribution rules: before create, edit, or reorder, show a short human interpretation of the final logic and checks and obtain explicit user confirmation. This is a conversational gate, not `_confirmation_token`. Only delete uses central two-step MCP confirmation with `_confirmation_token`; conversational consent never replaces the second delete call, and other operations never receive the token.

Treat the CRM API response, errors, business validation, and domain permissions as authoritative. After a write, name the changed entity in human terms and use the fresh response payload as the receipt; reread with the canonical read tool when details are missing.

## Package boundaries

Do not create tools for pipeline members, field value builders/deletion, CRM pages/blocks, or source CRUD; they are outside this package. Do not emulate them with composite actions through other APIs. The package uses no widget and no feature flags.

## Completion

Return `готово`, `частично`, or `заблокировано`; name the pipeline, stage, deal, or rule in human terms, list verified or changed data, include the API result, and provide the smallest next step.
