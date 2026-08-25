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

# Task Management

Run only as the primary skill selected by `101-index`. Preserve the user's explicit intent: plain text, a list, opening interactive details, and a mutation are different routes.

## Lists and reads

For a list, call `list_tasks` with server-side filters. When the user asks to show the list, use the presentation token and exactly one `show_result` call; do not build a separate table or new UI.

For one task, first resolve it through `entity-resolution`, then call `get_task`. When the user asks to open or show details, or clearly wants to work with the task, take `structuredContent.presentation.token` and call `show_result({token})` exactly once. This must open `task_detail` in `ui://101/widget/app-2.0.7.html` with the same sections, dimensions, and spacing as the 101 application.

## Interactive detail

Inside the widget, the user may:

- change status;
- assign or remove an assignee;
- submit a comment;
- attach files to a comment.

`set_task_assignee` and `submit_task_comment` are app-only actions available only to the widget. Do not call them from ordinary conversation or have the model imitate user clicks. The widget invokes them through the Apps bridge, preserves its draft, and rereads authoritative data after the write.

## Conversational writes

Handle an explicit conversational request to change status or another field through `update_task` after a fresh read and `write-preflight`. Handle an explicit request to submit a comment without opening the widget through `add_task_comment`. Never turn a read or recommendation into a write.

When the user attaches files outside the widget, call `upload_files` first, then pass server identifiers only to a tool that supports attachments. Never substitute local paths, temporary URLs, or file contents for a server identifier.

After a write, report the server-confirmed status, assignee, or comment using human-readable names. Do not expose GUIDs without an explicit request.
