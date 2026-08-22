---
name: entity-resolution
description: Use when an internal 101 workflow must resolve a user, company, project, contractor, event, Wiki, page, task, bill, or price-list entity from human wording.
version: "1.0.0"
role: helper
invocation: internal
intents:
  - entities.resolve
depends_on: []
required_tools:
  - whoami
optional_tools:
  - search_users
  - list_projects
  - list_contractors
  - list_events
  - list_wikis
  - list_tasks
  - list_bills
  - list_price_lists
resources:
  - path: ../shared-resources/context-and-identity.md
    kind: semantic-guide
    required: true
completion:
  statuses:
    - готово
    - частично
    - заблокировано
---

# Разрешение сущностей

Этот helper не владеет пользовательской целью. Получи от главного скилла тип сущности, человеческое описание и уже закреплённый контекст.

1. Начни с `whoami`, если пользователь и компания ещё не известны.
2. Используй самый узкий существующий search/list инструмент и серверные фильтры.
3. Если найдено единственное точное совпадение, верни его главному скиллу автоматически.
4. Если совпадений несколько, останови зависимую операцию и покажи один компактный список понятных названий с достаточным контекстом для выбора.
5. Не угадывай по частичному совпадению и не выбирай первый результат только из-за порядка выдачи.
6. Не показывай GUID в обычном ответе. Сохрани его как техническую ссылку в контексте и evidence ledger.

Если доступ или поиск не позволяют доказать однозначность, верни точный блокер и минимальный следующий вопрос. Не подменяй отсутствующую сущность догадкой.
