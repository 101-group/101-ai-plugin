---
name: wiki-management
description: Use when an internal 101 goal must find, read, create, or update Wiki spaces, pages, blocks, publication, permissions, images, or files through the existing Wiki and upload APIs.
version: "1.0.0"
role: primary
invocation: internal
intents:
  - wiki.list
  - wiki.read
  - wiki.write
  - wiki.media.manage
depends_on:
  - entity-resolution
  - write-preflight
  - file-handling
required_tools:
  - whoami
  - list_wikis
  - get_wiki_page
  - list_wiki_blocks
  - create_wiki
  - update_wiki
  - create_wiki_page
  - update_wiki_page
  - mutate_wiki_blocks
  - delete_wiki_media_block
  - get_wiki_permissions
  - update_wiki_permissions
  - reset_wiki_permission
  - get_wiki_page_publication
  - set_wiki_page_publication
optional_tools:
  - delete_wiki
  - get_public_wiki_page
resources:
  - path: ../shared-resources/context-and-identity.md
    kind: semantic-guide
    required: true
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

# Управление Wiki и файлами

Работай только как главный скилл, назначенный `101-index`. Ты владеешь пользовательской целью управления Wiki, страницами, блоками, публикацией, правами и размещёнными медиа. Не создавай параллельный Wiki-контракт.

## Чтение и разрешение

Через `entity-resolution` найди Wiki и страницу по человеческому названию. Используй `list_wikis`, `get_wiki_page`, `list_wiki_blocks`, permission и publication read-инструменты. При нескольких совпадениях попроси выбрать; не показывай GUID.

## Изменения

Перед `create_wiki`, `update_wiki`, `create_wiki_page`, `update_wiki_page`, `mutate_wiki_blocks`, изменением прав или публикации применяй `write-preflight` и точный текущий payload соответствующего инструмента. После записи перечитай затронутую сущность.

При редактировании блоков сохраняй порядок и незатронутые блоки. Не заменяй содержимое всей страницы, если пользователь просил изменить один блок.

## Изображения и файлы

1. Передай пользовательские файлы в `file-handling`.
2. Используй только подтверждённый результат upload API: URL, тип, размер и идентификатор не восстанавливай из имени.
3. Создай или обнови соответствующий медиа-блок через существующий блоковый API.
4. Если пользователь удаляет медиа со страницы, удали только Wiki-блок через `delete_wiki_media_block`.

Физическое удаление файла из хранилища не поддерживается и не имитируется. Успешная загрузка при неуспешном размещении даёт статус `частично` с точным описанием загруженного файла и незавершённого блока.

## Завершение

Верни `готово`, `частично` или `заблокировано`; назови Wiki и страницу человеческими именами, перечисли проверенные или изменённые блоки, права, публикацию и медиа, покажи свежий результат и минимальный следующий шаг.
