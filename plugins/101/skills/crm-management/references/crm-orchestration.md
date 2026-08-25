# CRM: Orchestration for 21 Operations

This resource defines decisions before a tool call. Always read the exact argument JSON Schema from the current tool catalog. Resolve entities by human name, keep technical identifiers only in call context, and never expose GUIDs in ordinary answers.

## Common sequence

1. Resolve the user and company through `whoami` when context is not fixed.
2. Identify the domain and explicit action: read, create, edit, move, reorder, or delete. Discussion and recommendations do not authorize writes.
3. Make the safe reads from the table. Select one exact match automatically; show human names and distinguishing context for multiple matches.
4. Ask one minimal question when required meaning is missing. Before the answer, call no write tool. Never ask for a GUID or make the user repeat data already read.
5. Reread mutable state immediately before a write. For a full-list payload, compare the fresh snapshot with the baseline; a conflict blocks the write.
6. Treat the write response as the receipt and make the specified verification read. Report human names and the actual result.

## Operation matrix

| Tool | Mode | Resolve before call | Missing user input | Freshness and guard | Receipt |
|---|---|---|---|---|---|
| `list_crm_pipelines` | read | User and current company from `whoami` | Clarify company only when context is genuinely ambiguous | Do not filter access locally; the API decides permissions | Name available pipelines and company without GUIDs |
| `create_crm_pipeline` | write | Company via `whoami`; existing pipelines via `list_crm_pipelines` | Name; whether to create base stages; position only when material | Check same-name matches and refresh the list before the call | Name the pipeline and created stages; refresh the list when needed |
| `reorder_crm_pipelines` | write | Company and current order via `list_crm_pipelines` | Desired relative order by name | Send the complete fresh active list; snapshot conflict blocks | Verify response order and fresh list |
| `get_crm_pipeline` | read | One pipeline via `list_crm_pipelines` | For duplicates, ask by company and counters | Never guess UUID from a partial match | Return stages, deals, sources, fields, and permissions in human terms |
| `edit_crm_pipeline` | write | Pipeline via list and fresh detail | Exact new name; use reorder for relative order | Send no empty patch; reread changed values | Name changed fields and use fresh response payload |
| `delete_crm_pipeline` | delete | Pipeline, company, and active deals via list/detail | With deals, ask whether to move or delete them; never promise a cascade | Show name/consequences; first call preview, second only with `_confirmation_token` | Verify returned list and name deleted pipeline |
| `create_crm_funnel` | write | Pipeline and stages via `get_crm_pipeline` | Stage name; position only when append is wrong | Check same-name stages and fresh detail | Find the new stage in response and name its position |
| `reorder_crm_funnels` | write | Pipeline and both named stages via detail | Desired placement when wording permits several | Send complete fresh active stage list; snapshot conflict blocks | Verify stage order in response |
| `edit_crm_funnel` | write | Pipeline and one stage via detail | Exact new name; use reorder for movement | Send no empty patch; reread stage | Name changed stage and fresh value |
| `delete_crm_funnel` | delete | Stage, active deals, and active-rule references via detail/rules | With dependencies, ask for a safe action first | Show name/consequences; preview then `_confirmation_token` | Reread pipeline and report absence or API rejection |
| `create_crm_deal` | write | Pipeline, stages, sources, fields via detail; contact via lookup | At least one of `contractorGuid` or `preLead`; material stage/source/manual owner | Without `responsibleGuid`, inspect active rules first; invent no required fields | Find deal in response and name stage and actual owner |
| `get_crm_deal` | read | Pipeline and unique deal via detail | For duplicates, show name, contact, stage, source, and owner | Current `funnelId` is part of the deal address | Return a human description without technical GUIDs |
| `edit_crm_deal` | write | Fresh deal via `get_crm_deal`; fields/sources via detail | Exact changed fields; use move for pure movement | Preserve final `contractorGuid` or `preLead` and required fields; no empty patch | Verify response deal; find new ID after stage change |
| `delete_crm_deal` | delete | Unique deal via detail and `get_crm_deal` | For duplicates, ask using human context | Show name/consequences; preview then `_confirmation_token` | Reread pipeline and report absence |
| `move_crm_deal` | write | Deal, current stage, target stage via detail, then `get_crm_deal` | Unambiguous target stage and required field values | Reread deal/stages; never use target ID as current path parameter | Find new deal ID in target stage and report position |
| `list_crm_distribution_rules` | read | Pipeline via `list_crm_pipelines` | Clarify when several pipelines match | Response is complete order of all non-deleted active/inactive rules | Name rules by order, status, condition, and strategy without GUIDs |
| `get_crm_distribution_rule_schema` | read | Pipeline via `list_crm_pipelines` | Invent nothing when schema is unavailable | Treat response as sole source of fields, operators, strategies, candidates, defaults, and limits | Explain human choices without exposing GUIDs |
| `create_crm_distribution_rule` | write | Fresh schema/rules; candidates only from schema | Name, condition meaning, timezone, strategy, candidates, weights, fallback | Check format, references, overlap, coverage, priority; show interpretation and obtain confirmation | Verify rule and order through fresh `list_crm_distribution_rules` |
| `reorder_crm_distribution_rules` | write | Fresh schema/rules; identify rule by name/condition | Desired priority and overlap impact | Send complete fresh non-deleted list; snapshot conflict blocks; interpret and confirm | Verify full fresh order through `list_crm_distribution_rules` |
| `edit_crm_distribution_rule` | write | Fresh schema/rules and current rule | Every changed part and fallback/priority impact | Validate complete final rule; interpret and confirm | Verify rule and order through fresh `list_crm_distribution_rules` |
| `delete_crm_distribution_rule` | delete | Fresh rules and post-delete coverage | Resulting fallback when coverage changes | Show name/order/consequences; preview then `_confirmation_token` | Verify absence and new order through fresh `list_crm_distribution_rules` |

## AI-generated rules: actual format

Rules apply only when creating a deal without `responsibleGuid`. The backend scans active rules by `sortOrder` and selects the first matching active rule with an available candidate. Explicit `responsibleGuid` is manual assignment and bypasses rules. If no rule/candidate matches, creation fails and leaves no partial deal.

`condition` has exactly `version` and `expression`. `expression` uses `op`; logical nodes are `always`, `and` with non-empty `items`, `or` with non-empty `items`, or `not` with `item`. A predicate has `field` and `op`; `value` is required only when `valueKind` is not `none`. `in` and `notIn` require a non-empty array. Take fields, allowed operators, types, options, and limits only from fresh `get_crm_distribution_rule_schema`.

Current logical codes are `always`, `and`, `or`, `not`; predicate codes are `eq`, `notEq`, `in`, `notIn`, `contains`, `notContains`, `startsWith`, `endsWith`, `gt`, `gte`, `lt`, `lte`, `exists`, `notExists`. Use only operators declared for the specific field. Built-in paths currently include `source.uuid`, `source.type`, `source.name`, `source.isActive`, `funnel.id`, `deal.name`, `deal.preLead`, `deal.hasContact`, `contact.guid`, `createdBy.guid`, `createdAt.hour`, `createdAt.weekday`, `createdAt.isWeekend`; custom fields use `customField.<code>`. This explains the format but never replaces fresh schema.

`assignment` contains `strategy` and non-empty `candidates`. Current strategy codes are `fixed`, `roundRobin`, `weightedRoundRobin`, `leastActive`. Every candidate uses a `responsibleGuid` from `availableCandidates`; `weight` is allowed only when fresh schema says the strategy supports weights. Never infer a GUID by name or use someone absent from `availableCandidates`.

## Mandatory AI-rule preflight

Before create, edit, or reorder:

1. Call `get_crm_distribution_rule_schema` for the selected pipeline.
2. Call `list_crm_distribution_rules` and preserve the full current order.
3. Translate the request into a candidate rule using only fresh schema.
4. Ask one compact question block for every material gap. Before the answer, call no mutating tool.
5. Check syntax/types, fields/options/stages/candidates, timezone, limits, candidate uniqueness, weight support, and final order.
6. Compare with every higher- and lower-priority active rule. Flag obvious overlap, unreachable branches, and rules shadowed by an earlier `always` or provably broader condition.
7. Prove coverage. If not provable, require an explicit final `always` fallback. Without it, do not write because unmatched unassigned deals would fail.
8. Show a human interpretation: “first check …; on match assign … using …; otherwise continue …; fallback …,” plus check results and proof limits.
9. Obtain explicit confirmation of that exact interpretation, then call the relevant create/edit/reorder tool.
10. Use the write response, then call `list_crm_distribution_rules` again to verify round-trip fields and actual order.

A fallback is a separate `always` rule, not a field. When no suitable fallback exists, creating it and configuring the target rule is non-atomic because there is no shared transaction endpoint. Show exact call order, each payload, and temporary assignment impact; get one confirmation for that exact plan. After each write, reread rules and rerun the next-step preflight. Stop on any mismatch/error, report the partial result, and promise no automatic rollback.

The backend validates DSL structure/version, fields/operators/types, limits, timezone, candidates, and pipeline references. No separate validate, dry-run, or simulation endpoint exists. It does not prove mutual exclusivity, reachability, or complete coverage. Perform conservative static review; label anything unprovable as uncertain and ask. Never promise simulation with real deals.

## Prompting example

“Assign deals to Mark before noon” is incomplete. Ask one compact block covering timezone, behavior after noon and fallback, weekdays, which Mark in `availableCandidates`, behavior when unavailable, applicable sources/stages/deal types, and priority against overlapping rules.

For multiple candidates, also ask for the strategy in plain language: fixed owner, round robin, weighted round robin, or least active. Ask weights only when fresh schema supports them.
