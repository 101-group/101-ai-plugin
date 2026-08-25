# Context and Entity Resolution

- Start with `whoami`: the current user and their available company define the data boundary.
- Keep the selected company, project, and entities within one conversation until the user explicitly changes the goal.
- Do not show GUIDs in an ordinary response. Keep them only as technical references for tool calls and the evidence ledger.
- One exact available match may be selected automatically. Multiple matches require a human choice based on name and meaningful context.
- Never guess a company, project, member, event, or Wiki from a similar name.
- Before a write, recheck the existence and accessibility of every affected entity through the current API.
