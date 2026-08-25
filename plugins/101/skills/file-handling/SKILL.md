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

# File Uploads

This helper does not own the user's goal. It receives files and their purpose from the primary skill, runs `write-preflight`, calls `upload_files`, and returns the API result without a parallel format.

1. Verify that the input contains files supported by the current tool and every required metadata field.
2. Never infer type, size, URL, or identifier; use only API result values.
3. Normalize successful items and errors so the caller can place every proven upload and report a partial result.
4. When the outcome is uncertain, do not retry automatically without proof that no upload was created.

Physical deletion from storage is unsupported and must not be simulated. Removing a file from a Wiki page belongs to `wiki-management`, which removes the relevant block rather than using this helper.
