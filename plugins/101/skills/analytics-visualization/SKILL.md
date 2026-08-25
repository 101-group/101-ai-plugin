---
name: analytics-visualization
description: Use when a primary 101 analytical workflow has approved a standalone chart or composite report from verified aggregates.
version: "2.2.0"
role: helper
invocation: internal
intents:
  - analytics.visualize
depends_on: []
required_tools:
  - render_chart
  - validate_artifact
  - render_artifact
optional_tools: []
resources:
  - path: references/chart-design.md
    kind: semantic-guide
    required: true
  - path: references/chart-token-snapshot-1.0.154.json
    kind: token-snapshot
    required: true
  - path: references/chart-payload-example.json
    kind: payload-example
    required: true
  - path: references/artifact-payload-example.json
    kind: payload-example
    required: true
completion:
  statuses:
    - готово
    - частично
    - не завершено
---

# OpenAI Data Analytics in 101

This helper runs only after the primary workflow has allowed visualization through explicit intent or the default analytical rule. It never fetches business data, explores sources, or turns plain data into a chart by itself.

1. Read `references/chart-design.md`, the token snapshot, and both canonical payload examples in `references/`.
2. State the analytical question and select the simplest of the 18 canonical types: `line`, `area`, `stackedArea`, `bar`, `horizontalBar`, `stackedBar`, `stackedBar100`, `horizontalStackedBar`, `horizontalStackedBar100`, `histogram`, `scatter`, `heatmap`, `pie`, `leaderboard`, `sparkline`, `funnel`, `waterfall`, `boxPlot`.
3. Verify sign, grain, period, bounded table or snapshot, and a truthful 101 `source`: `engine=101-mcp`, `language=mcp`, strict `executedAt`, the actual `tool`, and safe filters or metrics without GUIDs, URLs, SQL, or credentials. Only `references/chart-design.md` owns chart and artifact semantics, including raw numeric payloads.
4. For one chart, call `render_chart({title, source, table, chart, display})`; all five fields are top-level arguments. Do not wrap the model in an extra `payload` or `data` field. `table.columns` declares every field and each row contains exactly those fields. Every `chart.fields.x/y/color/size/label/facet/lineStyle` value is an encoding object such as `{"field":"month","type":"temporal"}`, never a string, and references a declared column.
5. For an audit, build one composite artifact whose `manifest.blocks` contains text, useful metrics, an adaptive number of justified charts, and tables as needed. Immediately after each audit chart, place a short chart-specific finding and a concrete chart-specific recommendation based only on that chart's data. After all charts, place a separate overall audit conclusion and separate general recommendations, including follow-up checks and deeper-analysis directions. Local and overall guidance are both required and do not replace each other. `snapshot.status` uses only `ready|partial|blocked|fixture`. Call exactly one `validate_artifact` as `validate_artifact({surface, manifest, snapshot})`, then on success pass the unchanged payload to exactly one `render_artifact` as `render_artifact({surface, manifest, snapshot})`.
6. After success, do not repeat a presentation call. On `failed`, `INVALID_ARGUMENT`, or `invalid_analytics_payload`, stop and return the error honestly without retrying. On source failure, invent no rows; for `partial` or `blocked`, add visible `accessIssues[]` entries with required `lower_snake_case` IDs and understandable messages.

The widget must preserve hover and keyboard-focus tooltips, legend toggles, an accessible table, mobile layout, and explicit empty, sparse, and error states. Never claim rendering succeeded when the call failed.
