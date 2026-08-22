---
name: file-handling
description: Use when an internal 101 workflow must upload user-provided files through the existing upload_files API and normalize the returned media references for a caller.
version: "1.0.0"
role: helper
invocation: internal
intents:
  - files.upload
depends_on:
  - write-preflight
required_tools:
  - upload_files
optional_tools: []
resources:
  - path: ../shared-resources/wiki-content-and-files.md
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

# Загрузка файлов

Этот helper не владеет пользовательской целью. Он принимает от главного скилла файлы и назначение, проводит `write-preflight`, вызывает `upload_files` и возвращает результат API без параллельного формата.

1. Проверь, что вход содержит поддерживаемые текущим инструментом файлы и все обязательные метаданные.
2. Не восстанавливай тип, размер, URL или идентификатор догадкой: используй значения результата API.
3. Нормализуй успешные элементы и ошибки так, чтобы вызывающий скилл мог разместить каждый подтверждённо загруженный файл и показать частичный результат.
4. При неопределённом исходе не повторяй загрузку автоматически без доказательства отсутствия результата.

Физическое удаление файла из хранилища не поддерживается и не имитируется. Удаление файла со страницы Wiki выполняет `wiki-management` удалением соответствующего блока, а не этим helper.
