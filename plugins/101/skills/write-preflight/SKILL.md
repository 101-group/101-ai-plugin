---
name: write-preflight
description: Use when an internal 101 write workflow must validate the current tool schema, required data, entity references, mutable state, and central policy before one API-backed mutation.
version: "1.0.0"
role: helper
invocation: internal
intents:
  - writes.preflight
depends_on:
  - entity-resolution
required_tools:
  - whoami
optional_tools: []
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

# Проверка перед записью

Этот helper не владеет пользовательской целью и не авторизует действие. Его результат — точный payload существующего MCP/API-инструмента либо конкретный блокер.

## Вход

Получи от главного скилла явное намерение пользователя, имя write-инструмента, выбранные сущности, базовый снимок изменяемых данных и предполагаемые поля.

## Проверка

1. Возьми свежую machine schema выбранного инструмента и используй её исходные имена полей, типы и обязательность. Не создавай MCP-only формат.
2. Проверь, что пользователь явно приказал выполнить эту запись. Read-only рекомендация не является разрешением.
3. Через `entity-resolution` проверь обязательные ссылки и их доступность в текущей компании.
4. Перечитай только затрагиваемое изменяемое состояние и актуальные права непосредственно перед вызовом.
5. Если payload построен на полном списке, сравни свежий снимок с базовым. При конфликте ничего не перезаписывай.
6. Примени центральную MCP policy подтверждений и риска. Не добавляй собственное подтверждение и не ослабляй штатное.

## Выход

При успехе верни главному скиллу имя инструмента, точный payload, прочитанные свежие значения и основание готовности. При любой недостающей или неоднозначной обязательной части верни `заблокировано`, точную причину и минимальный следующий шаг. Не подставляй значения ради прохождения API.
