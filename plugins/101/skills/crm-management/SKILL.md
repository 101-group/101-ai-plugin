---
name: crm-management
description: Use when an internal 101 goal must manage CRM pipelines, stages, deals, or distribution rules through the current CRM API.
version: "1.0.0"
role: primary
invocation: internal
intents:
  - crm.pipeline.manage
  - crm.funnel.manage
  - crm.deal.manage
  - crm.distribution.manage
depends_on:
  - entity-resolution
  - write-preflight
required_tools:
  - whoami
  - list_crm_pipelines
  - create_crm_pipeline
  - reorder_crm_pipelines
  - get_crm_pipeline
  - edit_crm_pipeline
  - delete_crm_pipeline
  - create_crm_funnel
  - reorder_crm_funnels
  - edit_crm_funnel
  - delete_crm_funnel
  - create_crm_deal
  - get_crm_deal
  - edit_crm_deal
  - delete_crm_deal
  - move_crm_deal
  - list_crm_distribution_rules
  - create_crm_distribution_rule
  - get_crm_distribution_rule_schema
  - reorder_crm_distribution_rules
  - edit_crm_distribution_rule
  - delete_crm_distribution_rule
  - list_contractors
  - search_users
optional_tools: []
resources:
  - path: ../shared-resources/context-and-identity.md
    kind: semantic-guide
    required: true
  - path: ../shared-resources/safety-and-permissions.md
    kind: semantic-guide
    required: true
  - path: references/crm-orchestration.md
    kind: semantic-guide
    required: true
completion:
  statuses:
    - готово
    - частично
    - заблокировано
---

# Управление CRM

Работай только как главный внутренний скилл, назначенный `101-index`. Веди сценарии воронок, этапов, сделок и правил распределения через 21 канонический MCP-инструмент. Не создавай второй диспетчер, CRM-виджет или параллельный CRM-контракт.

До выбора конкретного инструмента прочитай обязательный CRM-контракт оркестрации `references/crm-orchestration.md`. Он определяет безопасные чтения, смысловые развилки, минимальные вопросы и квитанцию для каждой из 21 операции. Схему аргументов всегда бери из текущей machine schema инструмента, а не из примеров ресурса.

## Чтение и разрешение сущностей

1. Закрепи пользователя и компанию через `whoami` и общий контекст.
2. Найди воронку через `list_crm_pipelines`; при нескольких совпадениях попроси выбрать по человеческому названию.
3. Читай `get_crm_pipeline` как каноническую деталку: из неё бери этапы, сделки, источники и пользовательские поля. Не создавай отдельные lookup-вызовы для этих сущностей.
4. Для контакта сделки переиспользуй `list_contractors` или `search_users`. Не угадывай `contractorGuid` и не показывай GUID без прямого запроса.
5. Перед настройкой распределения вызови `get_crm_distribution_rule_schema`; кандидатов, условия и стратегии бери только из этого ответа.

Сначала получай всё, что можно однозначно доказать безопасным чтением. Если для выбранного действия недостаёт обязательного пользовательского смысла или найдено несколько сущностей, задай один минимальный вопрос с человеческими вариантами. Объединяй тесно связанные недостающие параметры в один компактный блок, когда по отдельности ответ не позволяет выполнить действие. До ответа не вызывай write-инструмент и не подставляй API default, если он заметно меняет пользовательский результат.

## Контракт записи

Перед записью применяй `entity-resolution` и `write-preflight`. Передавай аргумент `payload` один в один с body текущего CRM REST API: не переименовывай поля, не вычисляй права и не исправляй payload вместо API. Path-параметры идентифицируют существующую сущность, а `payload` содержит только тело соответствующего REST-запроса.

Обычные create, edit, move и reorder выполняются одним вызовом после полного preflight без дополнительного подтверждения. Узкое исключение — AI-generated правила распределения: перед create, edit или reorder покажи краткую человеческую интерпретацию итоговой логики и проверок и получи явное подтверждение пользователя. Это разговорный гейт, а не `_confirmation_token`. Только delete использует центральное двухшаговое подтверждение MCP с `_confirmation_token`; не подменяй разговорным согласием второй delete-вызов и не добавляй токен к другим операциям.

Ответ, ошибки, бизнес-валидацию и доменные права считай результатом CRM API. После записи назови изменённую сущность человеческим именем и используй свежий payload ответа как квитанцию; если он не содержит нужной деталки, перечитай сущность каноническим read-инструментом.

## Границы пакета

Не создавай инструменты участников воронки, конструктора и удаления значений полей, CRM-страниц и блоков или CRUD источников: они не входят в текущий пакет. Не подменяй их составными действиями через другие API. Текущий пакет работает без виджета и без feature flags.

## Завершение

Верни `готово`, `частично` или `заблокировано`; назови воронку, этап, сделку или правило человеческим именем, перечисли проверенные или изменённые данные, результат API и минимальный следующий шаг.
