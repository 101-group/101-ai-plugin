# Дизайн OpenAI Data Analytics в 101

График — доказательство конкретного вывода. Зафиксируй вопрос, сравнение, единицы, период и зерно до выбора формы. Runtime (движок) поддерживает 18 canonical типов: `line`, `area`, `stackedArea`, `bar`, `horizontalBar`, `stackedBar`, `stackedBar100`, `horizontalStackedBar`, `horizontalStackedBar100`, `histogram`, `scatter`, `heatmap`, `pie`, `leaderboard`, `sparkline`, `funnel`, `waterfall`, `boxPlot`.

## Выбор формы

- Динамика: `line`, `area`, `stackedArea`, `sparkline`.
- Сравнение и рейтинг: `bar`, `horizontalBar`, `leaderboard`.
- Состав: `stackedBar`, `stackedBar100`, `horizontalStackedBar`, `horizontalStackedBar100`, `pie`.
- Распределение и связи: `histogram`, `boxPlot`, `scatter`, `heatmap`.
- Последовательность: `funnel`, `waterfall`.

Не выбирай форму только ради красоты. Временной тренд требует хотя бы две точки, `boxPlot` — достаточные числовые поля, а 100%-stacked (нормированный состав) — ненулевой знаменатель. Для длинных названий предпочитай горизонтальную форму. При редких данных покажи точные значения и ограничение интерпретации.

## Standalone contract (контракт одного графика)

- `render_chart({title, source, table, chart, display})` получает готовую bounded table (ограниченную таблицу), максимум 500 rows и 40 `table.columns`.
- Идентификаторы полей — `lower_snake_case`; каждая row содержит ровно объявленные поля.
- `chart.fields.x/y/color/size/label` ссылаются только на `table.columns[].key`.
- `source` описывает реальный вызов: `engine=101-mcp`, `language=mcp`, разрешённый MCP tool, RFC3339 `executedAt`, безопасные filters и определения metrics. SQL, GUID, URL, credentials и PII запрещены.
- Значения `source.filters` — только непустые scalar (простые) `string|number|boolean`. Массив фактического MCP-аргумента отражается одной короткой строкой через запятую; массивы, объекты и `null` в payload запрещены.
- Честно передавай `row_count` и `truncated`; не выдавай обрезанный набор за полный.

## Composite contract (контракт составного отчёта)

- Один аудит — один `{surface, manifest, snapshot}` и один `render_artifact`, а не четыре независимых графика.
- Перед сборкой прочитай `artifact-payload-example.json`: это точный валидный production-пример для `validate_artifact` и `render_artifact`.
- Верхний уровень разрешает только `surface`, `manifest`, `snapshot`. В `manifest` обязательны `version`, `surface`, `title`, `generatedAt`, `blocks`, `sources`; опциональны только `description`, `filters`, `cards`, `charts`, `tables`. В `snapshot` обязательны `version`, `generatedAt`, `status`, `datasets`; опционален только `accessIssues`.
- `manifest.scope` и `snapshot.scope` запрещены. Не переносить `scope`, `provenance`, `subtitle`, `rows`, `chart`, `display` или другие поля старого standalone-контракта на уровень `manifest`/`snapshot`.
- `manifest.blocks` задаёт внутренний текст, `metric-strip`, до четырёх charts и таблицы; стандарт аудита 101 — текст + KPI + 3 графика + таблица.
- В стандартном аудите структурные ключи копируются из точного примера. Все ссылки обязаны разрешаться внутри payload (набора данных): `chartId`, `tableId`, `cardIds`, поля chart encodings (привязок графика) и поля таблицы. Опциональный `tables[].defaultSort` содержит только `field` и `direction`; `field` дословно совпадает с одним объявленным `tables[].columns[].field`, `direction` равен только `asc` или `desc`.
- `snapshot.datasets` содержит те же проверенные агрегаты, максимум 500 rows и 40 полей на dataset.
- `ready|partial|blocked|fixture` — единственные статусы. `partial` и `blocked` обязаны иметь понятный `accessIssues[].message`.
- Сначала `validate_artifact`, затем неизменённый payload передаётся в `render_artifact`.

## Цвет, интерактивность и доступность

Цветовые токены накладывает frontend через `@101app/design-tokens-web`; модель не передаёт hex, CSS и произвольные токены. Смысл не должен держаться только на цвете: положение, знак, подпись, контур и форма остаются читаемыми.

Hover и keyboard focus открывают одинаковый tooltip. Legend позволяет выключать серии, но не последнюю видимую. Полные значения доступны в table view. На mobile подписи не пересекаются, длинные категории сохраняются в tooltip/таблице, а expanded editor (расширенный режим) не теряет контекст.

## Финальный QA

Проверь desktop/mobile и light/dark: chart не пуст, marks (элементы) имеют ненулевой размер, ноль и знак честны, tooltip/focus/legend/table работают, source видим, empty/sparse/error состояния объяснены. Локальные изменения типа, группировки и layout (раскладки) не требуют MCP-вызова; новая компания, период, метрика или данные требуют нового business fetch и snapshot.
