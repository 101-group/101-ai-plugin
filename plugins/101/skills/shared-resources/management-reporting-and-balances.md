# Management Reporting and Balances

Use these rules in professional full-account mode: projects plus the company fund. Cash flow, P&L/income statement, and the management balance are the classic three-statement set; P&L and income statement are the same report.

## Accrual P&L

- Include only confirmed events that entered the 101 balance.
- Recognize an event in the period of its confirmation date or the available latest signature date, not its creation or payment date. An unconfirmed event remains a draft.
- A confirmed report for completed work creates revenue even without payment. The unpaid amount becomes a receivable.
- A customer advance is an operating cash inflow and a balance-sheet liability, but not revenue until confirmed reports recognize the work.
- Invariant: a 1 million advance, a confirmed 600 thousand report, and 400 thousand of direct costs produce 600 thousand of revenue, 400 thousand of direct costs, and 200 thousand of gross profit; the remaining 400 thousand remains an advance.
- A confirmed report with customer price 0 and contractor payment 200 thousand produces revenue 0, direct costs 200 thousand, and a gross loss of 200 thousand.

## Company-owner and participant compensation

- By default, treat project profit or markup distributions to participants, including the company owner, as direct production or variable compensation.
- The company-fund share is the company’s gross or contribution profit after direct costs. Fund expenses and taxes reduce it to net profit.
- If the company owner takes a large project share, show the company result after that compensation separately from the owner’s personal earnings. The company may earn 0 while the owner earns a substantial amount.
- For a classical P&L, recommend directing profit to the fund, paying the owner fixed compensation from the fund, and distributing dividends only after net profit.
- Build the owner’s personal report from the existing 101 own balance: earnings for the selected period beside the current own balance for all history. Call it personal earnings or financial result, never company net profit.
- Salary or fixed compensation for the company owner is an operating expense that reduces EBITDA and net profit.

## Dividends, taxes, and EBITDA

- A fund article named “dividends” is technically a 101 expense event, but analytically it distributes already-earned net profit. It is a financing cash outflow, not an operating expense, and must not reduce EBITDA, operating profit, or net profit a second time.
- Tax articles do not reduce EBITDA but are required for net profit.
- EBITDA is a management metric. Always show the formula used, article classification, and data limitations.

## Cash flow and internal transfers

Separate operating, investing, and financing activities. Exclude project ↔ fund transfers from consolidation so they do not create income or expense again.

The company-fund balance is not net profit or dividends available for distribution. It may contain investments, advances, and prior-period balances.

## Company-fund expense classification

Classify in this order:

1. Start with the expense article name.
2. For an unclear article, read only its linked event list and short descriptions, not every event detail.
3. If uncertainty remains, ask the user and offer choices. Never guess.

Categories: direct production; operating; interest/financing; tax; depreciation; dividends; investing/capital; other.

After the user answers, apply the classification to the current report and offer to rename the article or add context. Make the actual change only after explicit confirmation and a permissions check.

## Large purchases

- Do not expense a long-lived asset immediately in OPEX. Treat it as an investing cash outflow, an asset on the balance sheet, and depreciation in P&L. Exclude the purchase from EBITDA.
- Never invent a useful life; ask the user.
- Until useful life and depreciation are set, show EBITDA without the purchase, label net profit provisional, and offer to configure the useful life.

## Management settlement balance

Use `get_company_closing_balance` as the primary view of how much the company must receive or return if it closes today. Call it the management settlement balance. It is not a full accounting balance with property, bank accounts, loans, and external liabilities.

Show customer receipts or refunds, payments to counterparties, participant accountable balances, the fund settlement, and the closing total.

- Include archived projects automatically when they retain debt, accountable balances, or fund settlements. Fully closed archived projects may be omitted.
- Build the primary figure only from confirmed data and show drafts separately.
- In a general audit, show the total, main components, and the three largest drivers of deviation, then offer deeper analysis.
- Show the fund balance as the current state of settlements inside the fund beside the closing balance after all confirmed obligations are settled. Explain the reasons for a large gap.

## Common mistakes

| Mistake | Correct interpretation |
| --- | --- |
| Recognizing an advance as revenue | It remains a liability until a confirmed report |
| Using payment date for revenue | Use confirmation or the latest available signature date |
| Subtracting dividends from profit again | Show a financing outflow after net profit |
| Expensing a long-lived asset immediately | Investing outflow, asset, then depreciation |
| Inventing a useful life | Ask the user |
| Calling closing balance a full balance sheet | It is a settlement balance for closing today |
| Equating fund balance with profit | Separate investments, advances, and prior balances |
