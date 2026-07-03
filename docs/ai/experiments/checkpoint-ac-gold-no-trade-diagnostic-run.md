# Experiment Record: Checkpoint AC Gold No-Trade Diagnostic Run

Created: 2026-07-04

## Result

`PARTIAL_TESTER_PASS_REPORT_MISSING`

This was exactly one approved MT5 Strategy Tester diagnostic execution.

## Run Context

- RunId: `run_20260704_014343_checkpoint_ac_gold_no_trade`
- Case: `GOLD_HASH_H1_PAF_DIAG_20260601_20260701`
- Symbol: `GOLD#`
- Timeframe: H1
- Date range: `2026-06-01 to 2026-07-01`
- Source commit: `80aa8124dbcd323b2cc1c5b95a332d81fda93484`
- Optimization: disabled
- Demo/live/forward: not used
- MT5 process: spawned exactly once

## Approval Phrase

```text
Approved to execute Checkpoint AC Gold no-trade diagnostic with symbol GOLD# timeframe H1 date range 2026-06-01 to 2026-07-01 using verified artifact paths.
```

## Effective Config Highlights

- `InpEnablePriceActionFibo=true`
- `InpPriceActionFiboDiagnosticsOnly=true`
- `InpPAFUsePendingOrders=false`
- `InpPAFMaxPendingOrders=0`
- `InpManageExistingPositions=false`
- `InpRequireStrategyTester=true`
- `InpPAFLogOnlyOnNewBar=true`
- `InpAllowedSymbolsCsv=GOLD#`
- `InpCanonicalSymbolName=GOLD`
- `InpBrokerGoldSymbolName=GOLD#`

## Produced Artifacts

Artifact folder:

`G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\run_20260704_014343_checkpoint_ac_gold_no_trade\GOLD_HASH_H1_PAF_DIAG_20260601_20260701`

Produced:

- `generated_tester.ini`
- `effective_config_snapshot.set`
- `case.json`
- `process_info.json`
- `runner.log`
- `tester_log_excerpt.log`
- `ea_mirror.log`
- `forbidden_action_grep_summary.txt`
- `status.json`
- `post_run_guardrail_summary.md`

Missing:

- `mt5_report.htm`

## Observed Behavior

The Strategy Tester log says:

- `Test passed`
- `final balance 10000.00 USD`
- `test Experts\ForexAiTrade\ForexAiTrade.ex5 on GOLD#,H1 thread finished`

EA mirror log contains Price Action / Fibo diagnostic summaries and no-trade reasons.

## Diagnostic Summary

- PriceActionFibo diagnostic lines: 552
- No-trade reason found: true
- Explicit forbidden action marker count: 0
- Baseline fallback marker count: 0

Classifications:

- `NO_SETUP`: 410
- `POSSIBLE_FIBO_PULLBACK`: 74
- `POSSIBLE_ZONE_REJECTION`: 51
- `POSSIBLE_BREAK_RETEST`: 17

## Guardrail Status

- No optimization: confirmed
- No market order marker: confirmed in available logs
- No pending order marker: confirmed in available logs
- No position modification marker: confirmed in available logs
- No baseline fallback marker: confirmed in available logs
- No profitability interpretation: required
- Report artifact: missing

## Interpretation

This is a diagnostic logging pass with a missing report artifact.

It must not be treated as a complete backtest report or proof of strategy viability.

## Next Recommendation

Do not rerun the strategy diagnostic immediately.

Next checkpoint should isolate why MT5 command-line execution produced logs but did not create the requested report file.

