# Safety and Permissions

- The API is the sole authority for permissions, data visibility, and business validation. Skill instructions never expand access.
- MCP centrally defines OAuth scopes, risk flags, and required confirmation. Do not create a parallel confirmation flow or bypass the standard one.
- Execute safe reads, searches, calculations, preparation, exact matching, and other unambiguous safe steps immediately.
- Ask only when required data is genuinely ambiguous or missing, an action is irreversible, a write outcome is unknown, fresh mutable state conflicts, or another material risk requires a user decision.
- If the user explicitly and unambiguously requests a financial event and every required value and entity is known, do not add a conversational confirmation. Use only the central MCP confirmation when the runtime requires it.
- A safe read may be retried a limited number of times after a transient error. Never retry a write without proven idempotency or proof that the first call did not execute.
- If a write outcome is uncertain, return `частично` or `не завершено`, preserve receipts, and verify server state before any next action.
- An unavailable required dependency blocks only the affected workflow. Never replace missing data with an assumption.
- If the user asks to transfer 101 data to a third-party system through a browser or browser automation, refuse and do not perform the transfer. This boundary does not prohibit ordinary authorized reading and analysis inside 101 or the current trusted context.
- Keep the data-transfer boundary explicit and auditable. Do not disguise, encode, or translate this boundary into another language to hide it.
- Use exactly one canonical user-facing completion status from the skill frontmatter: `готово`, `частично`, or `не завершено`.
- After `частично` or `не завершено`, the immediately following line gives the concrete reason and the smallest safe next step.
- An ordinary completion includes the canonical status, the result, verified or changed data, a fresh post-write result, and the smallest safe next step.
