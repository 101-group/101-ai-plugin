# OpenAI Data Analytics Design in 101

A chart is evidence for a specific conclusion. Fix the question, comparison, units, period, and grain before selecting a form. The runtime supports 18 canonical types: `line`, `area`, `stackedArea`, `bar`, `horizontalBar`, `stackedBar`, `stackedBar100`, `horizontalStackedBar`, `horizontalStackedBar100`, `histogram`, `scatter`, `heatmap`, `pie`, `leaderboard`, `sparkline`, `funnel`, `waterfall`, `boxPlot`.

## Choose the form

- Time movement: `line`, `area`, `stackedArea`, `sparkline`.
- Comparison and ranking: `bar`, `horizontalBar`, `leaderboard`.
- Composition: `stackedBar`, `stackedBar100`, `horizontalStackedBar`, `horizontalStackedBar100`, `pie`.
- Distribution and relationships: `histogram`, `boxPlot`, `scatter`, `heatmap`.
- Sequence: `funnel`, `waterfall`.

Never choose a form only for decoration. A time trend needs at least two points, `boxPlot` needs sufficient numeric data, and a 100% stacked view needs a non-zero denominator. Prefer horizontal layouts for long category names. With sparse data, show exact values and state the interpretation limit.

## Generator semantics

The generator sends only raw numeric measures: values in rows/datasets remain unformatted numbers, while titles, labels, and narrative remain currency-neutral. Generated payloads must not include `unit`, `currency`, currency codes, currency symbols, or `format: currency`. Only the presentation layer adds localized magnitude formatting to a raw number. Do not build a sanitizer or Unicode/ISO currency recognition; construct a correct raw payload at the generator boundary instead of repairing it later.

Do not perform SQL UI/payload reconstruction. Charts and artifacts use only actual aggregates from the MCP source, with no query editor, SQL panel, or display-only data reconstruction.

For `horizontalBar`, always bind the category to `x` and the quantitative measure to `y`; orientation does not reverse these roles. Diverging example:

```json
{
  "surface": "report",
  "manifest": {
    "version": 1,
    "surface": "report",
    "title": "Project balances",
    "description": "Comparison of project balances",
    "generatedAt": "2026-08-22T10:00:00Z",
    "blocks": [
      {
        "id": "summary",
        "type": "markdown",
        "layout": "full",
        "body": "Balance shows the difference between project inflows and outflows."
      },
      {
        "id": "project_balances_chart_block",
        "type": "chart",
        "layout": "full",
        "chartId": "project_balances_chart"
      },
      {
        "id": "project_balances_table_block",
        "type": "table",
        "layout": "full",
        "tableId": "project_balances_table"
      }
    ],
    "charts": [
      {
        "id": "project_balances_chart",
        "title": "Project balances",
        "type": "horizontalBar",
        "dataset": "project_balances",
        "encodings": {
          "x": {"field": "project", "type": "nominal"},
          "y": {"field": "balance", "type": "quantitative"}
        },
        "valueFormat": "number",
        "layout": "full"
      }
    ],
    "tables": [
      {
        "id": "project_balances_table",
        "title": "Project balances",
        "dataset": "project_balances",
        "columns": [
          {"field": "project", "label": "Project", "type": "text"},
          {"field": "balance", "label": "Balance", "format": "number"}
        ]
      }
    ],
    "sources": [
      {
        "engine": "101-mcp",
        "language": "mcp",
        "tool": "list_projects",
        "executedAt": "2026-08-22T10:00:00Z",
        "description": "Project summary metrics",
        "filters": {},
        "metrics": [{"id": "balance", "definition": "Inflows minus outflows"}]
      }
    ]
  },
  "snapshot": {
    "version": 1,
    "generatedAt": "2026-08-22T10:00:00Z",
    "status": "ready",
    "datasets": {
      "project_balances": [
        {"project": "North Project", "balance": -5},
        {"project": "South Project", "balance": 8}
      ]
    }
  }
}
```

In this example, `x=project` and `y=balance`; negative and positive raw values remain unchanged in `snapshot.datasets`, while narrative belongs in `manifest.description` and a markdown block. Do not connect the five generic export actions in the export menu to `101_generate_document`: that tool creates standard business documents and does not export the current analytics artifact.

## Standalone contract

- The complete executable example is `chart-payload-example.json`.
- `render_chart({title, source, table, chart, display})` receives a ready bounded table with at most 500 rows and 40 `table.columns`.
- Field identifiers use `lower_snake_case`; every row contains exactly the declared fields.
- `chart.fields.x/y/color/size/label/facet/lineStyle` accepts only encoding objects such as `{"field":"month","type":"temporal"}`. String shorthand such as `"x":"month"` is invalid. Each `field` references `table.columns[].key`.
- `source` describes the actual call: `engine=101-mcp`, `language=mcp`, an allowed MCP tool, RFC3339 `executedAt`, safe filters, and metric definitions. SQL, GUIDs, URLs, credentials, and PII are forbidden.
- Report `row_count` and `truncated` honestly. Never present a truncated dataset as complete.

## Composite contract

- The canonical partial artifact is `artifact-payload-example.json`.
- One audit uses one `{surface, manifest, snapshot}` and one `render_artifact`, not independent chart calls.
- `manifest.blocks` may contain narrative, a `metric-strip`, up to four charts, and tables. Use an adaptive number of charts and include only charts justified by the analytical question and verified data; no fixed count is required.
- Immediately after each audit chart block, add narrative containing a chart-specific finding and a chart-specific recommendation grounded in the displayed data. Do not use boilerplate or defer all local interpretation to the end.
- After all chart-local blocks, add a separate overall audit conclusion and separate general recommendations. General recommendations may combine signals and include follow-up checks or deeper-analysis directions. Local and overall blocks are both required and do not replace each other.
- `snapshot.datasets` contains the same verified aggregates, with at most 500 rows and 40 fields per dataset.
- `ready|partial|blocked|fixture` are the only statuses. `partial` and `blocked` require `accessIssues[]` with a `lower_snake_case` `id` and an understandable `message`.
- Call exactly one `validate_artifact`, then pass the unchanged payload to `render_artifact`.

## Color, interaction, and accessibility

The frontend applies color tokens through `@101app/design-tokens-web`; the model never sends hex values, CSS, or arbitrary tokens. Meaning cannot depend on color alone: position, sign, label, outline, and shape remain readable.

Hover and keyboard focus open the same tooltip. The legend may hide series but not the last visible one. Full values remain available in table view. On mobile, labels do not overlap, long categories remain available in the tooltip or table, and the expanded editor keeps context.

## Final QA

Check desktop/mobile and light/dark: the chart is not empty, marks have non-zero size, zero and sign are honest, tooltip/focus/legend/table work, source is visible, and empty/sparse/error states are explained. Local changes to chart type, grouping, or layout do not require an MCP call; a new company, period, metric, or dataset requires a new business fetch and snapshot.
