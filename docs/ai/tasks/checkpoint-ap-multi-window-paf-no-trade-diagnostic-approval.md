# Checkpoint AP: Multi-Window PAF No-Trade Diagnostic Approval

## Objective

Create an approval package for a future Checkpoint AQ multi-window `GOLD#` H1 Price Action / Fibo no-trade diagnostic run.

This checkpoint does not execute MT5.

## Scope

In scope:

- Define future multi-window diagnostic constraints.
- Require concrete user-approved date ranges.
- Require each window to be 1 month or shorter.
- Define effective config assertions.
- Define stop conditions.
- Define required artifacts.
- Define post-run decision gates before any PAF implementation work.

Out of scope:

- MT5 execution.
- Strategy Tester execution.
- EA/source changes.
- Preset changes.
- Script/tool changes.
- Optimization.
- Market orders.
- Pending orders.
- Position modification.
- Profitability interpretation.

## Proposed Future Checkpoint AQ

Future Checkpoint AQ may run exactly three no-trade diagnostic windows only after explicit user approval.

Required run scope:

- Symbol: `GOLD#`
- Timeframe: `H1`
- Strategy Tester only
- Diagnostic-only
- Each date window <= 1 month
- No optimization
- No demo/live/forward test
- No market orders
- No pending orders
- No position modification
- No lot/risk increase
- No profitability interpretation

## Date Window Placeholders

| Window | Date Range |
|---|---|
| AQ-W1 | `NEED_USER_APPROVAL_1_FROM` to `NEED_USER_APPROVAL_1_TO` |
| AQ-W2 | `NEED_USER_APPROVAL_2_FROM` to `NEED_USER_APPROVAL_2_TO` |
| AQ-W3 | `NEED_USER_APPROVAL_3_FROM` to `NEED_USER_APPROVAL_3_TO` |

Codex must not invent the dates. The user must provide concrete dates in `YYYY-MM-DD to YYYY-MM-DD` format.

## Required Effective Config Assertions

- `InpLiveTradingEnabled=true`
- `InpDemoSafeMode=true`
- `InpRequireStrategyTester=true`
- `InpEnablePriceActionFibo=true`
- `InpPriceActionFiboDiagnosticsOnly=true`
- `InpPAFUsePendingOrders=false`
- `InpPAFMaxPendingOrders=0`
- `InpPAFLogOnlyOnNewBar=true`
- `InpManageExistingPositions=false`
- `InpAllowedSymbolsCsv=GOLD#`
- `InpCanonicalSymbolName=GOLD`
- `InpBrokerGoldSymbolName=GOLD#`
- Optimization disabled
- Strategy Tester only

`InpLiveTradingEnabled=true` is allowed only inside Strategy Tester to pass the internal tester gate. It is not demo/live approval.

## Stop Conditions

Stop immediately if any of these appear:

- Config mismatch.
- Any date window is longer than 1 month.
- Unknown terminal path.
- Unknown MT5 data folder.
- Report folder is not writable.
- Uncontrolled already-running MT5 terminal may intercept `/config`.
- Stale artifact reuse.
- Optimization enabled.
- Demo/live/forward environment detected.
- Market order attempt.
- Pending order attempt.
- Position modification attempt.
- Baseline strategy fallback.
- Missing report artifact.
- Missing EA mirror log.
- Missing PAF diagnostics summary.

## Required Artifacts Per Window

- RunId
- `generated_tester.ini`
- effective config snapshot
- `process_info.json`
- `runner.log`
- `status.json`
- `mt5_report.htm`
- companion report files if generated
- `parsed_result.json`
- `ea_mirror.log`
- `tester_log_excerpt.log`
- `paf_diagnostics.json`
- `paf_diagnostics_summary.md`
- forbidden action grep/check summary
- post-run guardrail summary
- no-trade confirmation
- no baseline fallback confirmation

## Required Aggregate Review

After future AQ completes, aggregate:

- PAF classification distribution by window.
- Regime distribution by window.
- No-trade reason distribution by window.
- Spread statistics by window.
- Setup density by window.
- Comparison to Checkpoint AM.
- Whether PAF diagnostics justify an implementation-spec checkpoint.

## Future Approval Phrase

Execution remains blocked until the user provides this phrase with concrete dates:

```text
Approved to execute Checkpoint AQ multi-window PAF no-trade diagnostics for GOLD# H1 with windows YYYY-MM-DD to YYYY-MM-DD, YYYY-MM-DD to YYYY-MM-DD, and YYYY-MM-DD to YYYY-MM-DD using official AK runner/parser workflow.
```

## Recommendation

Merge this approval package only if it remains docs-only and does not alter EA/source, presets, scripts, tools, or research execution behavior.

Next safe checkpoint after merge: wait for explicit user approval for Checkpoint AQ or choose another docs-only planning checkpoint.
