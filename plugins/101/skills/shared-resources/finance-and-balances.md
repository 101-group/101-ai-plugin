# Finance and Balances

- Build financial findings and totals from confirmed events. Show unconfirmed events separately as drafts that may change the picture.
- Keep project cash, a member’s own balance, accountable balance, counterparty settlements, and the company fund separate.
- When reading project members, always read `/members/` through `list_project_members` and `/fund-settlements/` through `get_project_fund_settlements` with the same `project_guid`. Never substitute `ownBalance` from WOHOM or any other balance for `settlementBalance`. Successful zero values mean a zero settlement, not proven absence of fund participation. If the fund read fails, return members as a partial result and name the unavailable source.
- `settlementBalance > 0`: the project owes the company fund. `settlementBalance < 0`: the company fund owes the project. `settlementBalance = 0`: the settlement is closed.
- A positive or negative closing balance does not by itself prove solvency or insolvency. First show confirmed obligations and available cash.
- An estimate is a plan; a report is an actual expense. Do not mix them in one total without an explicit explanation.
- A confirmed report may have a customer price of 0 and a non-zero contractor amount. That produces zero revenue, a direct cost, and a project loss; the distribution allocates the loss with the opposite sign.
- A direct Company Fund Inflow is external financing or investment for company expenses, never revenue or profit.
- Project ↔ fund transfers are internal movements and do not create income or expense again in a consolidated view.
- A read-only recommendation does not authorize a transfer, report, permission change, or any other mutation. A write starts only after an explicit user instruction and a permissions check.
- After a financial write, reread the affected balance through the API. Never present a calculated expectation as a verified result.
