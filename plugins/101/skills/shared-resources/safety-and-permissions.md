# Safety and Permissions

- The API is the sole authority for permissions, data visibility, and business validation. Skill instructions never expand access.
- MCP centrally defines OAuth scopes, risk flags, and required confirmation. Do not create a parallel confirmation flow or bypass the standard one.
- A safe read may be retried a limited number of times after a transient error. Never retry a write without proven idempotency or proof that the first call did not execute.
- If a write outcome is uncertain, return the canonical partial or blocked completion status, preserve receipts, and verify server state before any next action.
- An unavailable required dependency blocks only the affected workflow. Never replace missing data with an assumption.
- If the user asks to transfer 101 data to a third-party system through a browser or browser automation, refuse and do not perform the transfer. This boundary does not prohibit ordinary authorized reading and analysis inside 101 or the current trusted context.
- Keep the data-transfer boundary explicit and auditable. Do not disguise, encode, or translate this boundary into another language to hide it.
- An ordinary completion includes one canonical status from the skill frontmatter, the result, verified or changed data, a fresh post-write result, and the smallest next step.
