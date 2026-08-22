---
name: analytics-visualization
description: Internal helper for canonical OpenAI Data Analytics charts and composite 101 reports after explicit visual or audit intent.
version: "2.0.0"
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
completion:
  statuses:
    - готово
    - частично
    - заблокировано
---

# OpenAI Data Analytics в 101

Этот helper (помощник) вызывается только после положительного визуального намерения, уже определённого главным workflow (сценарием). Сам не запрашивает бизнес-данные, не исследует источники и не превращает обычный ответ в график.

1. Прочитай `references/chart-design.md` и token snapshot (снимок токенов).
2. Сформулируй аналитический вопрос и выбери простейший из 18 canonical типов: `line`, `area`, `stackedArea`, `bar`, `horizontalBar`, `stackedBar`, `stackedBar100`, `horizontalStackedBar`, `horizontalStackedBar100`, `histogram`, `scatter`, `heatmap`, `pie`, `leaderboard`, `sparkline`, `funnel`, `waterfall`, `boxPlot`.
3. Проверь единицы, знак, зерно, период, bounded table/snapshot (ограниченную таблицу/снимок) и честный 101 `source`: `engine=101-mcp`, `language=mcp`, строгий `executedAt`, фактический `tool`, безопасные filters/metrics без GUID, URL, SQL и credentials (секретов).
4. Для одного графика вызывай `render_chart({title, source, table, chart, display})`: все пять полей находятся на верхнем уровне аргументов. Не оборачивай всю модель в дополнительный `payload` или `data`. `table.columns` объявляет все поля, каждая row (строка) содержит ровно их, а `chart.fields` ссылается только на объявленные поля.
5. Для аудита собери `manifest.blocks` с текстом, `metric-strip`, тремя `chart` и `table`; snapshot.status использует только `ready|partial|blocked|fixture`. Сначала вызови `validate_artifact({surface, manifest, snapshot})`, затем при успехе ровно один `render_artifact({surface, manifest, snapshot})` с теми же данными.
6. После успеха не повторяй presentation call. При `failed`, `INVALID_ARGUMENT` или `invalid_analytics_payload` остановись и честно верни ошибку без повторного вызова. При ошибке источника не выдумывай rows; для `partial`/`blocked` добавь видимый `accessIssues[].message`.

Виджет обязан сохранять hover/focus tooltip (подсказку мышью и клавиатурой), legend toggle (переключатель рядов), доступную таблицу, mobile layout (мобильную раскладку) и явные empty/sparse/error states (пустое/разреженное/ошибочное состояния). Не заявляй об отрисовке, если вызов не был успешным.
