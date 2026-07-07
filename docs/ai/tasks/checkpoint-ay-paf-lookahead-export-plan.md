# Checkpoint AY: PAF OHLC/Tick Lookahead Export Plan

Date: 2026-07-07

## Scope

Checkpoint AY is documentation / research-plan only.

No EA/source code changes.
No preset changes.
No MT5 run.
No Strategy Tester run.
No optimization.
No lot/risk increase.
No profitability claim.
No demo/live approval.

## Background

Checkpoint AX verified that the new PAF diagnostic fields are emitted in no-trade Strategy Tester diagnostics.

AX RunId: `run_20260707_172236`

AX produced:

- total trades: `0`
- PAF diagnostics: `97`
- possible setup rows: `33`
- `DATA_MISSING`: `19`
- `DIRECTION_MISSING`: `14`
- readiness: `BLOCKED_BY_MISSING_LOOKAHEAD_DATA`

The next blocker is not order execution. The next blocker is missing OHLC/tick lookahead data for offline shadow outcome labeling.

## Required Principle

Lookahead data must never be used by the EA to make trading decisions.

Lookahead data is allowed only after a diagnostic run is complete, for offline research and parser analysis.

## Recommended Next Implementation Direction

Prefer Option A:

Export a bar-series artifact for the diagnostic period, then match diagnostic events to future bars offline.

This is safer than adding future-aware logic to the EA because it reduces the risk of future data leaking into `Evaluate()`.

## Pre-registered Data Fields

Per diagnostic event:

- `run_id`
- `case_id`
- `phase`
- `actual_symbol`
- `canonical_symbol`
- `timeframe`
- `event_time`
- `classification`
- `direction_context`
- `direction_reason`
- `entry_reference_price`
- `spread_points`
- `regime`
- `session_bucket`
- diagnostic bar OHLC
- `atr`
- `ema_fast`
- `ema_slow`
- `bb_width_percent`

Lookahead fields:

- horizon bars
- future high
- future low
- future close
- MFE
- MAE
- first hypothetical TP/SL touch side if pre-registered
- same-bar ambiguity flag
- missing-data flag

## Pre-registered Horizons

Initial horizons for H1 diagnostic analysis:

- 6 bars
- 12 bars
- 24 bars
- 48 bars

These horizons must not be changed after seeing results to make the outcome look better.

## Stop Conditions For Future Work

Stop and require a new reviewed checkpoint if:

- source code would affect entry/exit behavior
- a market order path is introduced
- a pending order path is introduced
- position modification is introduced
- optimization is proposed
- lot/risk increase is proposed
- future data would be available to trading decisions
- output is interpreted as profitability proof

## Acceptance Criteria For A Future Checkpoint

A future implementation checkpoint should produce:

- OHLC or tick lookahead artifact
- enriched shadow outcome rows
- clear `DATA_MISSING` / `DIRECTION_MISSING` / `AMBIGUOUS_SAME_BAR` handling
- bucketed summaries by classification, session, spread, regime, and window
- explicit confirmation that no orders were sent
- explicit confirmation that no trading behavior changed

## Decision

- `LOOKAHEAD_EXPORT_PLAN_DEFINED`
- `ORDER_PATH_STILL_BLOCKED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`

## Next Safe Step

Prepare Checkpoint AZ as a narrow implementation or approval package for exporting OHLC bar-series artifacts and joining them to existing diagnostic events offline.
