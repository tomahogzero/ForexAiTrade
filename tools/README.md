# ForexAiTrade Tools

Phase 2 focuses on the MT5 EA skeleton and Risk Manager. Python research tooling from earlier phases can remain in this folder, but no optimizer automation is required for Phase 2.

Expected later workflow:

- Parse MT5 strategy tester reports.
- Preserve actual broker symbols such as `GOLD#` or `USDJPY#` alongside canonical reporting names.
- Rank parameter sets by robustness.
- Generate markdown summaries.
- Penalize fragile optimization neighborhoods.

Keep all scoring survival-first: drawdown, trade count, losing streak, and validation stability matter more than maximum historical profit.
