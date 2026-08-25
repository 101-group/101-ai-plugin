---
name: file-handling
description: Use when an internal 101 workflow must upload user-provided files through the hosted-file or Codex inline-image API and normalize the returned media references for a caller.
version: "1.1.0"
role: helper
invocation: internal
intents:
  - files.upload
depends_on:
  - write-preflight
required_tools:
  - upload_files
  - upload_image_content
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
    - не завершено
---

# File Uploads

This helper does not own the user's goal. It receives files and their purpose from the primary skill, runs `write-preflight`, calls the matching upload tool, and returns the API result without a parallel format.

1. When the host provides a temporary HTTPS `download_url` and real `file_id`, call `upload_files` unchanged.
2. When Codex exposes an attached PNG, JPEG, or WebP image as an absolute local path, read that exact file locally, encode its bytes as base64 without a data URL, and call `upload_image_content` with the original file name and real MIME type. Never send the local path to the 101 server.
3. Do not use the inline tool for other MIME types or images above 18 MiB. Report the limit instead of truncating or converting the file.
4. Never infer type, size, URL, or identifier; use the attachment metadata, local file inspection, and only API result values.
5. Normalize successful items and errors so the caller can place every proven upload and report a partial result.
6. When the outcome is uncertain, do not retry automatically without proof that no upload was created.

Physical deletion from storage is unsupported and must not be simulated. Removing a file from a Wiki page belongs to `wiki-management`, which removes the relevant block rather than using this helper.
