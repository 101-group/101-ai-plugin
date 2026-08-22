---
name: company-analytics
description: Use for source-backed company or project analytics, standalone charts, and composite Data Analytics audits from known 101 aggregates.
version: "2.0.0"
role: primary
invocation: internal
intents:
  - analytics.company
  - analytics.project
  - analytics.report
depends_on:
  - entity-resolution
required_tools:
  - whoami
  - get_company_closing_balance
  - list_projects
  - list_events
  - list_contractor_project_balances
optional_tools:
  - list_contractors
  - list_project_members
  - list_project_bill_balances
  - list_project_estimate_positions
  - list_bills
  - list_tasks
  - render_chart
  - validate_artifact
  - render_artifact
resources:
  - path: ../shared-resources/context-and-identity.md
    kind: semantic-guide
    required: true
  - path: ../shared-resources/finance-and-balances.md
    kind: semantic-guide
    required: true
  - path: ../shared-resources/safety-and-permissions.md
    kind: semantic-guide
    required: true
completion:
  statuses:
    - готово
    - частично
    - заблокировано
---

# Аналитика и составные аудиты 101

Работай только на чтение и используй известный контракт 101. Не исследуй базу и схему заново, не строй новый слой метрик, не запускай внешнюю вычислительную среду и не выгружай сырые события ради уже доступных агрегатов.

## Gate (правило) результата

Классифицируй запрос до чтения данных:

- простые данные, список или аналитика только текстом — верни проверенные данные и сделай 0 вызовов presentation tools (инструментов показа);
- один явный «график», «диаграмма», «визуализируй», «покажи динамику» или «интерактивно» — собери один `render_chart`;
- явный аудит, аналитический отчёт или просьба показать результат «как Data Analytics» — собери один составной artifact (отчёт), вызови один `validate_artifact`, затем один `render_artifact`;
- «без графика», «только данные», «только текст» или «только таблица» — запрет сильнее любого разрешающего слова.

При разрешённой визуализации прочитай `analytics-visualization` через `resources/read` и следуй ему. До этого не загружай его chart-design (правила дизайна графика).

## Данные без лишней разведки

1. Используй закреплённую компанию; вызывай `whoami` и `entity-resolution` только когда контекст её не определяет или название неоднозначно.
2. Текущий управленческий баланс бери из `get_company_closing_balance`.
3. Активные проекты и их доступные сводные поля бери из `list_projects`; углубляйся только в показатель, нужный для вопроса.
4. Суммы событий получай через `list_events` с `with_totals=true`, `per_page=0`, точным `company_guid`, периодом и `status=[partner_verified, client_accepted]`. Не выгружай сырые события и не пагинируй их, если вопрос отвечает блок `totals`/`balanceTotals`.
5. Для динамики разбей период на непересекающиеся интервалы и сделай один агрегирующий вызов на интервал. Используй запрошенное зерно; без него выбери самое крупное честное зерно, но не более 12 интервалов. Границы дат считай в заданном часовом поясе, по умолчанию Europe/Moscow.
6. Не смешивай подтверждённые и неподтверждённые события. Если пользователь явно просит только подтверждённые, фильтры `partner_verified` и `client_accepted` обязательны.

Сверяй единицы, период, знак и одинаковое зерно сравниваемых рядов. Причину движения называй причиной только при прямом доказательстве; иначе это гипотеза.

## Визуальный вызов

Один `render_chart` показывает один ограниченный график. Для аудита не делай четыре независимых `render_chart`: один составной `render_artifact` обязан содержать текст + KPI + 3 графика + таблица. Базовый финансовый аудит включает месячные поступления/расходы, чистый денежный поток и остатки проектов либо воронку по этапам — выбирай третий график по фактическим доступным данным.

Передавай только агрегированные bounded datasets (ограниченные наборы), честные `source`/`manifest.sources[]` со строгим `executedAt` и безопасными `filters` фактического MCP-вызова без GUID. Сначала вызови `validate_artifact` с тем же `{surface, manifest, snapshot}`. Если validation (проверка) успешна, вызови `render_artifact` ровно один раз с неизменённым payload (набором). Не повторяй успешный presentation call (вызов показа).

Локальная смена типа графика, группировки, фильтра уже загруженных строк, раскладки, подписей и режима таблицы выполняется внутри React runtime (движка) без нового MCP-вызова. Новый период, компания, метрика или данные требуют повторного business fetch (получения данных), нового snapshot (снимка) и новой проверки.

## Ответ

Начни с ответа на вопрос. Затем дай ключевые числа, выводы/риски и конкретные действия. Для простого запроса данных не навязывай аналитику. Для явного аудита отдели факты от гипотез и укажи ограничения. Не показывай GUID без прямого запроса и не заявляй, что график или отчёт отрисован, если presentation tool (инструмент показа) завершился ошибкой.
