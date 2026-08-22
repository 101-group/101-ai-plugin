---
name: event-positions
description: Use when an internal report or estimate workflow must resolve price-list, estimate-derived, or manual positions and preserve their startDate and endDate through the existing event API.
version: "1.0.0"
role: helper
invocation: internal
intents:
  - events.positions.prepare
  - events.positions.edit
depends_on:
  - entity-resolution
  - write-preflight
required_tools:
  - get_event
  - list_project_estimate_positions
optional_tools:
  - list_price_lists
  - list_price_list_categories
  - list_price_list_positions
  - search_price_list_positions
  - get_price_list
resources:
  - path: ../shared-resources/events-and-positions.md
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

# Подготовка позиций событий

Этот helper собирает позиции для `report-management` и `estimate-management`. Он не создаёт событие самостоятельно.

## Источники

- Для позиции из прайса используй серверный поиск и верни действующую ссылку и значения API.
- Для позиции из сметы используй `list_project_estimate_positions` и сохрани её источник в форме API.
- Для ручной позиции передай явные название, единицу, количество, цену и остальные обязательные поля без выдуманной ссылки на прайс.

`startDate` и `endDate` бери только из явного запроса или существующей позиции. Если API разрешает `null`, не наследуй даты события, проекта, соседней строки или текущий день.

## Создание и изменение

Для нового события собери список в точном формате create-инструмента. Для точечного изменения сначала вызови `get_event`, возьми полный свежий список, измени только явно названные поля целевой позиции и собери полный результирующий список. Остальные позиции, источники и сроки сохрани.

Непосредственно перед edit передай результат в `write-preflight`. Если целевая позиция, состав списка или необходимые соседние данные изменились относительно базового снимка, верни конфликт и ничего не записывай. Не выполняй автоматическое слияние и не отправляй одну строку как несуществующий частичный patch.
