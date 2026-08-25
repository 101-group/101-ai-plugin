---
name: project-management
description: Use when an internal 101 goal must create or edit a project, select its customer or price list, manage project expense categories, or copy category settings from another project.
version: "1.0.0"
role: primary
invocation: internal
intents:
  - project.create
  - project.edit
  - project.bill.manage
  - project.bill.copy
depends_on:
  - entity-resolution
  - write-preflight
required_tools:
  - whoami
  - create_project
  - edit_project
  - create_bill
  - edit_bill
  - list_bill_duplication_sources
  - duplicate_bills
optional_tools:
  - search_users
  - list_projects
  - list_bills
  - list_price_lists
  - get_price_list
resources:
  - path: ../shared-resources/context-and-identity.md
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

# Управление проектами

Работай как главный внутренний скилл `101-index`. Создавай и изменяй проекты и их статьи один в один с текущими REST-контрактами; имена, типы и обязательность полей всегда бери из machine schema (машинной схемы) инструмента.

## Проект

1. Закрепи компанию через `whoami`. Заказчика разрешай через `search_users`, существующий проект — через `list_projects`, не угадывай GUID.
2. Прайс-лист выбирай через `list_price_lists` и при необходимости `get_price_list`; передавай его как `priceListId` в `create_project` или `edit_project`.
3. Перед записью примени `entity-resolution` и `write-preflight`. Для создания вызови `create_project`; для частичного изменения — только `edit_project`. GET-форму редактирования не имитируй.

## Статьи расходов

- Текущие статьи читай через `list_bills`. Создавай проектную статью через `create_bill`, меняй через `edit_bill`; статьи фонда компании и удаление не входят в этот workflow (сценарий).
- Копирование выполняй только после создания проекта: сначала `list_bill_duplication_sources` с GUID целевого проекта, затем `duplicate_bills` с точным legacy payload (старым телом запроса) `{project_guid, bill_guids}`.
- `billGuids` в проекте связывает существующие статьи; `duplicate_bills` создаёт новые копии. Не смешивай эти действия.

Не создавай составной инструмент, параллельный API-контракт или дублирующий поиск. Все пять write-вызовов (операций записи) выполняются после полного preflight (проверки перед записью) одним вызовом и без собственного подтверждения; штатные OAuth scopes (права доступа), доменная валидация и центральная policy (политика) остаются обязательными.

Верни `готово`, `частично` или `заблокировано`, человеческое название проекта, выбранных заказчика и прайс-листа, изменённые статьи, API-квитанции и минимальный следующий шаг. GUID показывай только по прямому запросу.
