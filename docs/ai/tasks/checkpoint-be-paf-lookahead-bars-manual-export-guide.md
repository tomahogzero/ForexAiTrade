# Checkpoint BE: PAF Lookahead Bars Manual Export Guide

Date: 2026-07-08

## Scope

Create a documentation-only guide for manual `GOLD#` H1 OHLC bar export.

No MT5 run by Codex.
No Strategy Tester run.
No EA/source changes.
No preset changes.
No optimization.
No lot/risk increase.
No profitability claim.

## Target Artifact

`paf_lookahead_bars.csv`

Target context:

- RunId: `run_20260707_172236`
- Symbol: `GOLD#`
- Timeframe: `H1`
- Diagnostic range: `2026-03-01` to `2026-03-08`
- Required coverage: `2026-03-01 00:00:00` through at least `2026-03-10 23:59:59`
- Lookahead horizon: `48` H1 bars

## Manual Export Intent

The user may manually export bars from XM MT5 history if desired.

Codex does not open MT5 in this checkpoint.

The guide records:

- how to select `GOLD#`
- how to select `H1`
- required date coverage
- target filename
- schema expectations
- evidence to save
- stop conditions
- what not to do

## Required Evidence After Manual Export

The user should provide:

- absolute path to `paf_lookahead_bars.csv`
- evidence that symbol is `GOLD#`
- evidence that timeframe is `H1`
- evidence that date coverage reaches at least `2026-03-10 23:59:59`
- note that the data came from XM MT5 history
- note that Strategy Tester was not run for this export

## Future Offline Join Approval Phrase

`Approved to execute Checkpoint BB offline PAF lookahead join with bars CSV <absolute_path_to_csv> for RunId run_20260707_172236.`

This phrase approves only offline validation/joining. It does not approve MT5, Strategy Tester, order execution, optimization, risk increase, or profitability interpretation.

## Decision

- `MANUAL_EXPORT_GUIDE_DEFINED`
- `REAL_MARKET_LOOKAHEAD_CSV_STILL_MISSING`
- `OFFLINE_JOIN_NOT_RUN`
- `MT5_NOT_RUN_BY_CODEX`
- `ORDER_PATH_STILL_BLOCKED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`
