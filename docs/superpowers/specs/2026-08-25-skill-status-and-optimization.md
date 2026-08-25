# 101 Skill Status and Optimization Specification

Approved discovery source: `/Users/office/.codex/worktrees/101-ai-plugin-upload-wrapper-20260825/docs/discovery/skill-status-and-optimization-rules.md`.

The source discovery contains no unanswered or deferred records. The exact phrase `дискавери завершено` authorized implementation.

## User-facing completion contract

- Every public 101 skill uses exactly `готово`, `частично`, or `не завершено` for user-facing completion.
- `заблокировано` is not a user-facing completion status.
- After `частично` or `не завершено`, the immediately following line gives the concrete reason and the smallest safe next step.
- The analytics data contract remains unchanged: `snapshot.status=ready|partial|blocked|fixture`.

## Questions and execution

- Execute safe reads, searches, calculations, preparation, exact matching, and other unambiguous safe steps immediately.
- Ask only when required data is genuinely ambiguous or missing, an action is irreversible, a write outcome is unknown, fresh mutable state conflicts, or another material risk requires a user decision.
- When the user explicitly and unambiguously requests a financial event and every required value and entity is known, do not add conversational confirmation. Use only central MCP confirmation when the runtime requires it.

## Optimization and safety

- Remove repeated instructions when a required shared resource already owns the same rule.
- Preserve OAuth authorization, central scopes and risk flags, idempotency and unknown-outcome protection, fresh mutable-state checks, receipts, and the prohibition on blind write retries.
- Keep domain-specific contracts separate when merging them would weaken routing accuracy.
- Minimize the instruction set loaded for each route; remove unused dependencies and direct tool declarations when a helper owns the operation.

## Delivery

- Audit every `SKILL.md`, every shared resource, frontmatter completion status, `depends_on`, resource link, and explicit completion phrase.
- Record before/after instruction size and enumerate removed duplication and retained protections.
- Use RED→GREEN tests and independent behavioral review.
- Publish the next patch release of the public 101 Marketplace plugin, install it cleanly, and run a read-only fresh-session smoke test.
- Do not modify backend code or create financial records or events.
