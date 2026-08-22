# OpenAI Data Analytics upstream

Vendored from `openai/role-specific-plugins`, package
`plugins/data-analytics` at commit
`fe5608d2512a7d6a7b9821ce8a88c48464ecd6e4` (`datascience-mcp-widgets@0.2.6`).

The pinned upstream snapshot is stored under `src/upstream`. Product-specific
101 adapters, contracts, entrypoints, and token overrides live under `src/101`.
The approved adaptations inside `src/upstream` are limited to the patch ledger
below so a future upstream diff remains reviewable.

Excluded from the snapshot:

- prebuilt and compressed assets;
- the demonstration MCP server and connector configuration;
- Data Analytics skills and demonstration data;
- upstream `node_modules`.

The local `npm test` command runs the applicable frontend contract, transform,
renderer, markdown, table, and layout tests. Upstream tests that require the
excluded MCP server, Data Analytics skills, connector manifests, report-build
Python scripts, or prebuilt demo assets remain available under `tests/` for
audit comparison but are intentionally outside the local test command.

## 101 patch ledger

Only these product adaptations are approved:

- **Currency-neutral numeric presentation.** The `src/101` contract and shared
  numeric formatter accept raw numbers without a currency unit. The 101 build
  paths through chart, tooltip, table, KPI, markdown-copy, and image-copy
  presentation use that formatter; generic upstream presentation remains
  available outside the 101 entrypoints. There is no currency-string sanitizer.
- **Eight-locale 101 catalog.** The 101 presentation boundary resolves
  `ru`, `en`, `es`, `uz`, `ka`, `id`, `hi`, and `ar` from host context, with
  Russian fallback and Arabic RTL. Catalog values are generated from the WEB
  product localization source; authored report content is not translated.
- **Canonical horizontalBar semantics.** The chart transform and Recharts
  renderer preserve `x` as the category field and `y` as the numeric measure,
  including diverging values and one zero reference line.
- **MCP-only source provenance.** The 101 report and chart entrypoints expose
  the real MCP tool, dataset snapshot, filters, metric definitions, and data
  preview. SQL/query-file UI, tables-used metadata, handlers, and styles are
  excluded from the 101 bundles while the generic upstream entrypoints retain
  their original query workflow.
- **Listed chart detail resource.** The report reads exactly
  `ui://101/analytics/chart-v2.html`, validates its MCP App media type and HTML,
  mounts it in an isolated `allow-scripts` iframe with a session-bound readiness
  handshake, and falls back to the same bounded embedded chart data when the
  host resource read or mount fails.
- **Unsupported export and share actions.** The five unavailable 101 actions
  (Sites, HTML, PDF, Google Docs, and Google Slides) and their dedicated runtime,
  strings, handlers, and styles are absent from both 101 bundles. Local card
  copy remains available and generic upstream export behavior is unchanged.
Applicable test imports are rebased from `src/` to `src/upstream/` to match the
isolated package layout. Strict TypeScript checking does not own the historical
mixed JS/TS runtime. It does own the 101 bridge and contracts; Vite compilation
owns the two entrypoints and their upstream dependency graph. Any later upstream
adaptation must be approved and added to this ledger with its affected boundary
and reason.

## Review command

```bash
git diff --no-index \
  /path/to/role-specific-plugins/plugins/data-analytics/src \
  packages/chatgpt-data-analytics/src/upstream
```
