# GPT Review Request: Checkpoint AE MT5 Report Path Compatibility Preflight

Please review Checkpoint AE for ForexAiTrade.

## Scope

Checkpoint AE is documentation / runner-plan only.

It must not:

- run MT5
- run Strategy Tester
- spawn `terminal64.exe`
- change EA/source code
- change presets
- optimize parameters
- increase lot/risk
- claim profitability
- approve demo/live trading

## Files To Review

- `docs/44_Checkpoint_AE_MT5_Report_Path_Compatibility_Preflight_TH.md`
- `docs/ai/tasks/checkpoint-ae-mt5-report-path-compatibility-preflight-and-runner-plan.md`
- `docs/ai/current-status.md`

## Context

Checkpoint AC:

- RunId: `run_20260704_014343_checkpoint_ac_gold_no_trade`
- Result: `PARTIAL_TESTER_PASS_REPORT_MISSING`
- Strategy Tester log existed
- EA mirror log existed
- MT5 report artifact was missing

Checkpoint AD narrowed the issue to MT5 command-line report generation / report path behavior.

Checkpoint AE compares checked-in historical report patterns and proposes a safer runner/report path plan.

## Review Checks

Please check that:

1. Checkpoint AE does not approve MT5 retry.
2. Checkpoint AE does not overstate Checkpoint AC as a full pass.
3. The report-path conclusion is cautious and evidence-based.
4. The plan correctly prefers terminal-data-folder-relative `Report=ForexAiTradeResearch\\...\\mt5_report` based on historical PASS examples.
5. The plan avoids using absolute `G:\\...\\mt5_artifacts` report paths as the default.
6. The plan includes stale artifact guards.
7. The plan includes search for `.htm`, `.html`, `.xml`, no-extension base file, and companion graph images.
8. Missing report with tester/EA logs remains `PARTIAL_TESTER_PASS_REPORT_MISSING`.
9. Missing tester/EA logs and missing report remains `FAILED_NO_TESTER_ARTIFACTS`.
10. No strategy tuning, optimization, lot/risk increase, or profitability claim is present.
11. No EA/source or preset changes are included.

## Expected Output

Return:

`PASS` or `NEEDS_FIX`

If `NEEDS_FIX`, list exact issues and files/sections to improve.

