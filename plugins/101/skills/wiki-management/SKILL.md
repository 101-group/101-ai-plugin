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

# Wiki and File Management

Run only as the primary skill selected by `101-index`. Own the user's goal for Wiki spaces, pages, blocks, publication, permissions, and placed media. Never create a parallel Wiki contract.

## Reads and resolution

Use `entity-resolution` to find a Wiki and page by human name. Use `list_wikis`, `get_wiki_page`, `list_wiki_blocks`, and the permission and publication read tools. When several matches exist, ask the user to choose and do not expose GUIDs.

## Mutations

Before `create_wiki`, `update_wiki`, `create_wiki_page`, `update_wiki_page`, `mutate_wiki_blocks`, or a permission/publication change, apply `write-preflight` and the exact current payload of that tool. Reread the affected entity after the write.

When editing blocks, preserve order and untouched blocks. Do not replace an entire page when the user asked to change one block.

## Images and files

1. Pass user-provided files to `file-handling`.
2. Use only a proven upload API result; never derive URL, type, size, or identifier from the filename.
3. Create or update the relevant media block through the existing block API.
4. When the user removes media from a page, delete only the Wiki block through `delete_wiki_media_block`.

Physical deletion from storage is unsupported and must not be simulated. A successful upload followed by failed placement returns `частично` with the exact uploaded file and unfinished block.

## Completion

Return `готово`, `частично`, or `заблокировано`; name the Wiki and page in human terms, list verified or changed blocks, permissions, publication, and media, show the fresh result, and provide the smallest next step.
