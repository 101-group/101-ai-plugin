---
name: analytics-visualization
description: Internal helper for canonical OpenAI Data Analytics charts and composite 101 reports after analytics, comparison, trend, risk, financial-state, or audit intent.
version: "2.0.1"
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
    kind: contract-example
    required: true
  - path: references/artifact-payload-example.json
    kind: contract-example
    required: true
completion:
  statuses:
    - готово
    - частично
    - заблокировано
---

# OpenAI Data Analytics в 101

Этот helper (помощник) вызывается после положительного аналитического или визуального намерения, уже определённого главным workflow (сценарием). Сам не запрашивает бизнес-данные, не исследует источники и не превращает одиночное скалярное чтение в график.

1. Прочитай `references/chart-design.md`, token snapshot (снимок токенов) и оба канонических JSON-примера перед сборкой графика или составного отчёта.
2. Сформулируй аналитический вопрос и выбери простейший из 18 canonical типов: `line`, `area`, `stackedArea`, `bar`, `horizontalBar`, `stackedBar`, `stackedBar100`, `horizontalStackedBar`, `horizontalStackedBar100`, `histogram`, `scatter`, `heatmap`, `pie`, `leaderboard`, `sparkline`, `funnel`, `waterfall`, `boxPlot`.
3. Проверь единицы, знак, зерно, период, bounded table/snapshot (ограниченную таблицу/снимок) и честный 101 `source`: `engine=101-mcp`, `language=mcp`, строгий `executedAt`, фактический `tool`, безопасные filters/metrics без GUID, URL, SQL и credentials (секретов). Каждый `source.filters` value (значение фильтра) — только непустой string, number или boolean; массивы, объекты и null запрещены. Если фактический MCP-аргумент был массивом, сериализуй его для provenance (описания источника) в одну короткую строку через запятую, как `status: "partner_verified,client_accepted"` в точном примере.
4. Для одного графика вызывай `render_chart({title, source, table, chart, display})`: все пять полей находятся на верхнем уровне аргументов. Не оборачивай всю модель в дополнительный `payload` или `data`. `table.columns` объявляет все поля, каждая row (строка) содержит ровно их. Каждый `chart.fields.x/y/color/size/label/facet/lineStyle` — объект вида `{"field":"month","type":"temporal"}`, а не строка; `field` ссылается только на объявленную колонку.
5. Для аудита или многокомпонентного анализа копируй структуру точного JSON-примера, а не достраивай её по памяти: верхний уровень содержит только `surface`, `manifest`, `snapshot`. `manifest` обязательно содержит только `version`, `surface`, `title`, `generatedAt`, `blocks`, `sources` и при необходимости `description`, `filters`, `cards`, `charts`, `tables`. `snapshot` обязательно содержит только `version`, `generatedAt`, `status`, `datasets` и при необходимости `accessIssues`. Никогда не добавляй `manifest.scope`, `snapshot.scope`, произвольные metadata (метаданные) или поля из старых chart-примеров. Собери текст, `metric-strip`, ровно три `chart` и `table`; `snapshot.status` использует только `ready|partial|blocked|fixture`.
6. Соблюдай вложенные ссылки примера: `blocks[].chartId/tableId/cardIds` указывают только на объявленные assets (элементы отчёта), chart encoding (привязка графика) — только на поля своего dataset (набора данных), `tables[].columns[].field` — только на поля строк своего dataset. Если используешь `tables[].defaultSort`, он содержит ровно `field` и `direction`; `field` обязан дословно совпадать с одним `tables[].columns[].field`, а `direction` — только `asc|desc`. Для стандартного аудита не добавляй структурные ключи, которых нет в точном примере.
7. Сначала вызови `validate_artifact({surface, manifest, snapshot})`. При успехе передай ровно тот же объект без добавления, удаления или переименования полей в один `render_artifact({surface, manifest, snapshot})`.
8. После успеха не повторяй presentation call. При `failed`, `INVALID_ARGUMENT` или `invalid_analytics_payload` остановись и честно верни ошибку без повторного вызова. При ошибке источника не выдумывай rows; для `partial`/`blocked` добавь объект `accessIssues[]` с обязательными `id` в `lower_snake_case` и понятным `message`.

Виджет обязан сохранять hover/focus tooltip (подсказку мышью и клавиатурой), legend toggle (переключатель рядов), доступную таблицу, mobile layout (мобильную раскладку) и явные empty/sparse/error states (пустое/разреженное/ошибочное состояния). Не заявляй об отрисовке, если вызов не был успешным.
