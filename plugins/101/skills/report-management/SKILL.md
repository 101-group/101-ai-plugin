---
name: report-management
description: Use when an internal 101 goal must find, read, create, or edit one or many expense reports through the existing event API, including sourced or manual positions and their dates.
version: "1.0.0"
role: primary
invocation: internal
intents:
  - reports.list
  - reports.read
  - reports.create
  - reports.edit
depends_on:
  - entity-resolution
  - write-preflight
  - event-positions
required_tools:
  - whoami
  - list_events
  - get_event
  - create_expense
  - edit_expense
optional_tools:
  - list_projects
  - list_bills
  - list_contractors
  - upload_files
resources:
  - path: ../shared-resources/context-and-identity.md
    kind: semantic-guide
    required: true
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

# Управление отчётами

Этот workflow управляет финансовыми событиями типа «Отчёт». Запрос на управленческую аналитику компании/проекта передавай в `company-analytics`; не создавай событие только из-за слова «отчёт».

Работай только как главный скилл, назначенный `101-index`. «Отчёт» использует существующие expense-инструменты и их исходный API-контракт; не создавай отдельный тип события или MCP-only payload.

Не рисуй график для CRUD-операций (поиска, чтения, создания или изменения) с отчётами. Явный аналитический запрос верни диспетчеру для маршрута в `company-analytics`.

## Поиск и чтение

Разреши компанию, проект и другие названные сущности через `entity-resolution`. Для списка используй `list_events` с серверными фильтрами и пагинацией. Для деталей вызови `get_event`. Не выдавай первую страницу за полный набор и не показывай GUID без прямого запроса.

## Одна запись

Для создания собери позиции через `event-positions`, сохрани их источники, `startDate` и `endDate`, затем передай точный create payload в `write-preflight` и вызови `create_expense`.

Для изменения сначала вызови `get_event`. Точечную правку позиции преврати через `event-positions` в полный результирующий список, сохранив соседние строки и сроки. После свежего `write-preflight` вызови `edit_expense`. При конкурентном изменении остановись и покажи конфликт.

## Серия отчётов

Массовая команда — последовательность одиночных `create_expense`, а не новый batch payload.

1. Собери всю очередь и выполни общий preflight: обязательные поля, сущности, machine schema, позиции и возможность построить точный payload каждого элемента.
2. Если заранее известна хотя бы одна ошибка, не начинай ни одного создания; одним сообщением запроси все исправления и затем перепроверь всю очередь.
3. После успешной общей проверки кратко объяви состав и начни серию без повторного подтверждения, если центральная policy его не требует.
4. Перед каждым элементом повтори свежий `write-preflight` и выполни один API-вызов.
5. Локальная ошибка данных одного элемента помечает его не созданным, но не блокирует следующие независимые элементы.
6. Системная ошибка, потеря прав, изменение контракта или неопределённый исход записи останавливает необработанный хвост.

Сохраняй API-квитанцию каждого успешного вызова. При продолжении пропускай подтверждённо созданное, перепроверяй подтверждённо не запущенное и сначала сверяй серверное состояние элемента с неизвестным исходом. Не повторяй неизвестную запись автоматически.

Заверши статусом `готово`, `частично` или `заблокировано`; перечисли созданные, не созданные и не запущенные отчёты человеческими названиями, покажи свежие данные и минимальный следующий шаг.
