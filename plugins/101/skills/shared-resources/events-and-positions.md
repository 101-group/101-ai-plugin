# Events and positions

- An event has two terminology layers. When creating, confirming, and describing the result, use the exact subtype label from the creation form. Use the category label from filters/history only for filtering; never substitute it for the creation subtype.
- Canonical technical `eventSubtype` values live in backend `project/apps/transaction/event_serializers.py` (`EVENT_SUBTYPE_CHOICES`), and create API values also live in `project/apps/transaction/dto_v2.py`. Canonical Russian creation-form labels live in 101-web `src/localization/messages/ru.ts` (`events.subtypes`), with filter labels beside them in `events.filterSubtypes`; mappings to `eventSubtype` are defined in `src/domains/events/presentation/core.ts` and `src/domains/events/filters/config.ts`. If they disagree, reread those sources instead of reconstructing labels from a screenshot.
- Exact labels for the current contract:

| `eventSubtype` | Creation form | Filter/history |
| --- | --- | --- |
| `project_income` | `Поступление по проекту` | `Поступление по проекту` |
| `commission_income` | `Агентское вознаграждение` | `Агентское вознаграждение` |
| `company_income` | `Поступление в фонд компании` | `Поступление в фонд компании` |
| `project_expense` | `Отчёт по проекту` | `Отчёт по проекту` |
| `company_expense` | `Отчёт фонда компании` | `Отчёт фонда компании` |
| `project_own_payment` | `Оплата или аванс по проекту` | `Собственные средства проекта` |
| `project_working_payment` | `Перевод подотчетных средств по проекту` | `Подотчётные средства проекта` |
| `project_to_company_payment` | `Перевод из проекта в Фонд компании` | `Из проекта в фонд компании` |
| `company_to_project_payment` | `Перевод из Фонда компании в проект` | `Из фонда компании в проект` |
| `company_own_payment` | `Оплата или аванс в Фонде компании` | `Собственные средства фонда компании` |
| `company_working_payment` | `Перевод подотчетных средств в Фонде компании` | `Подотчётные средства фонда компании` |
| `project_estimate` | `Смета по проекту` | `Смета по проекту` |
| `company_estimate` | `Смета фонда компании` | `Смета фонда компании` |

- Example wording for a write: create a transfer of type `Оплата или аванс по проекту`. Do not call it type `Собственные средства проекта`: that is the filter-category label.
- `Отчёт` uses the existing expense contract, and `Смета` uses the existing estimate contract. Do not create an MCP-only event type.
- The customer price of an expense report may be zero while the contractor amount is nonzero. This is an expense not charged to the customer and therefore a project loss; allocation distributes that loss among participants as profit with the opposite sign.
- A position may come from a price list, an existing estimate, or manual input. Preserve its source through the current API contract.
- Send `startDate` and `endDate` only from explicit user data or an existing event. When the API permits `null`, do not inherit event dates or invent a schedule.
- For a targeted edit, first read the complete fresh list, change only the target position, and send the full resulting list required by the API contract.
- If the collection or affected positions changed after the baseline read, stop the write and show the conflict without automatic merging.
- Create multiple events as sequential single-event create calls. There is no batch payload.
