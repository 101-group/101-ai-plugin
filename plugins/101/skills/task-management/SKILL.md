---
name: task-management
description: Use when an internal 101 goal must list, read, open, update, or comment on tasks, including the interactive task detail widget.
version: "1.0.0"
role: primary
invocation: internal
intents:
  - tasks.list
  - tasks.read
  - tasks.open
  - tasks.update
  - tasks.comment
depends_on:
  - entity-resolution
  - write-preflight
required_tools:
  - whoami
  - list_tasks
  - get_task
  - show_result
optional_tools:
  - update_task
  - list_task_comments
  - add_task_comment
  - list_contractors
  - upload_files
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

# Управление задачами

Работай только как главный скилл, назначенный `101-index`. Сохраняй явное намерение пользователя: текстовый ответ, список, открытие интерактивной деталки или запись — разные маршруты.

## Список и чтение

Для списка вызови `list_tasks` с серверными фильтрами. Если пользователь просит показать список, используй presentation token (токен показа) и ровно один `show_result`; не собирай отдельную таблицу или новый UI.

Для одной задачи сначала разреши её через `entity-resolution`, затем вызови `get_task`. При просьбе «открой», «покажи детали» или явном желании работать с задачей возьми `structuredContent.presentation.token` и вызови ровно один `show_result({token})`. Должен открыться `task_detail` в `ui://101/widget/app-2.0.7.html` с теми же секциями, размерами и отступами, что в приложении 101.

## Интерактивная деталка

Внутри виджета пользователь может:

- сменить статус;
- выбрать или снять исполнителя;
- отправить комментарий;
- приложить файлы к комментарию.

`set_task_assignee` и `submit_task_comment` — app-only действия (доступны только виджету). Не вызывай их из обычного разговора и не проси модель подменять клики пользователя. Виджет сам использует их через Apps bridge (мост приложения), сохраняет черновик и после записи перечитывает авторитетные данные.

## Запись из разговора

Явную текстовую просьбу изменить статус или другое поле выполняй через `update_task` после свежего чтения и `write-preflight`. Явную просьбу отправить комментарий без открытия виджета выполняй через `add_task_comment`. Не превращай чтение или рекомендацию в запись.

Если пользователь прикладывает файлы вне виджета, сначала используй `upload_files`, затем передай серверные идентификаторы только в инструмент, который поддерживает вложения. Не вставляй локальные пути, временные URL или содержимое файла вместо серверного идентификатора.

После записи покажи подтверждённый сервером статус, исполнителя или комментарий человеческими названиями. Не показывай GUID без прямого запроса.
