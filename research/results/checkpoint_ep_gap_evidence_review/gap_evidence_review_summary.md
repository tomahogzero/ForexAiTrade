# Checkpoint EP Gap Evidence Review

- execution_status: `PASS`
- input/reviewed gaps: `28/28`
- official holiday context supported: `28`
- exact archived XM GOLD# server hours supported: `0`
- context-only, exact broker hours missing: `28`
- policy gate: `REVIEW_REQUIRED`
- decision: `EP_CONTEXT_SUPPORTED_EXACT_XM_HOURS_MISSING`
- strategy performance: `NOT_EVALUATED`

## Evidence Sources

- `OPM_FEDERAL_HOLIDAYS`: https://www.opm.gov/policy-data-oversight/pay-leave/federal-holidays/
- `CME_GOOD_FRIDAY_2023`: https://www.cmegroup.com/files/good-friday.pdf
- `CME_LABOR_DAY_2023`: https://www.cmegroup.com/trading-hours/files/labor-day-2023.pdf
- `CME_THANKSGIVING_2023`: https://www.cmegroup.com/trading-hours/files/thanksgiving-day-2023.pdf
- `CME_CHRISTMAS_2023`: https://www.cmegroup.com/trading-hours/files/christmas-day-2023.pdf
- `CME_NEW_YEAR_2024`: https://www.cmegroup.com/trading-hours/files/new-years-day-2024.pdf
- `CME_METALS_GUIDE_2024`: https://www.cmegroup.com/trading/metals/files/metals-prod-guide-2024.pdf
- `CME_CHRISTMAS_2024`: https://www.cmegroup.com/tools-information/holiday-calendar/files/2024-christmas-advisory.pdf
- `CME_HOLIDAY_CALENDAR`: https://www.cmegroup.com/trading-hours.html
- `XM_TRADING_HOURS_CONTEXT`: https://www.xm.com/help-center/trading-conditions/faq-what-are-your-trading-hours

OPM confirms public-holiday dates but not market hours. CME confirms exchange/metals holiday context but not XM's broker-specific `GOLD#` server-time schedule. XM's public help states that displayed times use GMT+2 with DST possibly applying, but no accessible year-specific archive found in this review proves the exact 2023-2025 `GOLD#` close/reopen times. Therefore no row is approved for policy expansion.
