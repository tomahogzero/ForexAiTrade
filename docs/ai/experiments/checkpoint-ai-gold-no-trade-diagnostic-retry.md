# Experiment Record: Checkpoint AI Gold No-Trade Diagnostic Retry

Created: 2026-07-07

## Result

`PASS_ARTIFACTS_COLLECTED`

This was exactly one approved MT5 Strategy Tester diagnostic execution.

## Run Context

- RunId: `run_20260707_020500_checkpoint_ai_gold_no_trade_retry`
- Case: `GOLD_HASH_H1_PAF_DIAG_RETRY_20260601_20260701`
- Symbol: `GOLD#`
- Timeframe: H1
- Date range: `2026-06-01 to 2026-07-01`
- Source commit: `a56910f`
- Approved runner baseline: `f0d8a6b`
- Optimization: disabled
- Demo/live/forward: not used
- MT5 process: spawned exactly once

## Approval Phrase

```text
Approved to execute Checkpoint AI one-run Gold no-trade diagnostic retry with symbol GOLD# timeframe H1 date range 2026-06-01 to 2026-07-01 using runner-hardened relative MT5 report paths.
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

`G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\run_20260707_020500_checkpoint_ai_gold_no_trade_retry\GOLD_HASH_H1_PAF_DIAG_RETRY_20260601_20260701`

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
- `mt5_report.htm`
- `mt5_report.png`
- `mt5_report-hst.png`
- `mt5_report-mfemae.png`
- `mt5_report-holding.png`

## Report Path

The run used a terminal-data-folder relative report request:

```ini
Report=ForexAiTradeResearch\run_20260707_020500_checkpoint_ai_gold_no_trade_retry\GOLD_HASH_H1_PAF_DIAG_RETRY_20260601_20260701\mt5_report
```

The fresh report was copied back as:

`G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\run_20260707_020500_checkpoint_ai_gold_no_trade_retry\GOLD_HASH_H1_PAF_DIAG_RETRY_20260601_20260701\mt5_report.htm`

## Guardrail Status

- Tester passed: true
- Final balance flat: true
- PAF diagnostic lines: 601
- Forbidden action marker count: 0
- Baseline fallback marker count: 0
- No-trade confirmation: `PASS_FROM_TESTER_AND_EA_LOGS`
- Baseline fallback confirmation: `PASS_FROM_EA_LOGS`

Classification summary:

| Classification | Count |
|---|---:|
| `NO_SETUP` | 444 |
| `POSSIBLE_FIBO_PULLBACK` | 81 |
| `POSSIBLE_ZONE_REJECTION` | 55 |
| `POSSIBLE_BREAK_RETEST` | 21 |

## Interpretation

This is an artifact and diagnostic safety pass only.

It does not prove profitability.
It does not approve demo/live trading.
It does not approve increasing lot or risk.
It does not approve converting diagnostic classifications into trade signals.

## Known Issue

The first post-processing pass had a local regex error after MT5 execution completed. Codex did not rerun MT5. The status and summaries were corrected from already-produced artifacts only.

