# Checkpoint CF: PAF First-Touch Diagnostic Interpretation

## Status

`DONE_FOR_REVIEW`

## Scope

Checkpoint CF interprets Checkpoint CE first-touch label distribution as diagnostics only.

This checkpoint does not:

- run MT5
- run Strategy Tester
- change EA/source code
- change presets
- add tools
- rerun relabeling
- optimize parameters
- add order logic
- claim profitability

## Source Evidence

Checkpoint CE result:

- Rows read: `33`
- Relabel-ready rows: `17`
- Data-missing rows: `2`
- Direction-missing rows: `14`

## Diagnostic Findings

- `SL_FIRST` is greater than `TP_FIRST` in every horizon.
- `DIRECTION_MISSING` remains a major blocker at `14/33` rows.
- `ATR_MISSING` remains at `2/33` rows.
- `AMBIGUOUS_SAME_BAR` exists and must remain conservative.
- H12/H24/H48 distributions are identical, suggesting most first-touch decisions happened within 12 bars.

## Interpretation

The current PAF diagnostic set is useful for further offline diagnosis, but not sufficient for order implementation or strategy approval.

## Decision

- `FIRST_TOUCH_DIAGNOSTIC_INTERPRETATION_CREATED`
- `SL_FIRST_DOMINATES_CURRENT_READY_ROWS`
- `DIRECTION_MISSING_REMAINS_MAJOR_BLOCKER`
- `SAMPLE_SIZE_TOO_SMALL_FOR_STRATEGY_DECISION`
- `ORDER_LOGIC_NOT_APPROVED`
- `OPTIMIZATION_NOT_APPROVED`
- `MT5_NOT_RUN`
- `STRATEGY_TESTER_NOT_RUN`
- `EA_SOURCE_NOT_CHANGED`
- `PRESETS_NOT_CHANGED`
- `NO_PROFITABILITY_CLAIM`

## Next Safe Step

Checkpoint CG should be an approval/planning package for first-touch attribution by classification, session, spread bucket, and regime. It should not optimize or add order logic.
