# Technical Integrity Audit

This audit checks only structural and arithmetic integrity. Offer it briefly before a full company financial analysis, including professional cash flow, P&L/income statement, EBITDA, or management balance work, and run it only after the user agrees. Do not offer or run it automatically before a narrow request.

## Complete reads

- Read every page of events for the selected company and every necessary event detail.
- If any page or necessary detail cannot be read, the technical audit has not passed.
- Never replace unread data with an assumption, an aggregate, or an active-project-only sample.

## Recipients and required relations

Every event must have a valid recipient. Check both the identifier and the existence and non-deleted state of the recipient, project, expense article, and related counterparties.

| Event subtype | Required relations |
| --- | --- |
| Project event | Existing, non-deleted project |
| Project report | Existing, non-deleted project and expense article |
| Company fund report | Existing, non-deleted expense article; no project required |
| Project transfer | Existing, non-deleted project |
| Project ↔ fund transfer | Existing, non-deleted project; the company and transfer direction determine the fund |
| Fund-only event | No project required |

A missing project on a fund-only event is not an error. An identifier without a live entity is not a valid relation.

## Distributions and arithmetic

- Reports and commission/agency inflows must contain the required profit and markup distributions.
- Every distribution entry must reference an existing, non-deleted counterparty.
- Every required distribution must total exactly 100%.
- A report total must equal the sum of its positions.

## Check result

When the user accepted this check, any structural or arithmetic error stops the following full financial analysis until it is corrected. Return a list containing the affected event or entity, the broken rule, and a correction recommendation. Change nothing automatically.

Unconfirmed operations, probable duplicates, and semantically generic counterparty names are not technical-audit failures. Evaluate them later as financial warnings.

## Common mistakes

| Mistake | Why the gate has not passed |
| --- | --- |
| Reading only the first event page | Completeness is unproven |
| Accepting an identifier for a deleted entity | The required relation is not valid |
| Flagging a fund report because it has no project | Fund-only events do not require a project |
| Accepting 99.99% or 100.01% | The required total is exactly 100% |
| Ignoring a mismatch between report total and positions | Arithmetic integrity is broken |
| Treating a probable duplicate as a technical error | It is a financial warning |
