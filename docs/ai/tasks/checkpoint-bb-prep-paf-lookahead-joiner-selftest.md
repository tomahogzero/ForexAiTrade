# Checkpoint BB-Prep: PAF Lookahead Joiner Self-Test

Date: 2026-07-07

## Scope

Self-test the offline PAF lookahead joiner with synthetic fixtures.

No MT5 run.
No Strategy Tester run.
No EA/source changes.
No preset changes.
No optimization.
No lot/risk increase.
No profitability claim.

## Purpose

Validate that `tools/paf_lookahead_joiner.py` can classify controlled fixture rows before using it on real `GOLD#` diagnostic artifacts.

This checkpoint does not replace the future Checkpoint BB real offline join approval.

## Fixture Cases

- `BUY_TP_FIRST` should produce `TP_FIRST`.
- `SELL_SL_FIRST` should produce `SL_FIRST`.
- `BUY_AMBIGUOUS` should produce `AMBIGUOUS_SAME_BAR`.
- `DIRECTION_UNKNOWN` should remain `DIRECTION_MISSING`.

## Result

Self-test output:

- `JOINED`: 3
- `DIRECTION_MISSING`: 1
- `TP_FIRST`: 1
- `SL_FIRST`: 1
- `AMBIGUOUS_SAME_BAR`: 1

Status: `PASS`

## Guardrails

The fixture is synthetic and must not be interpreted as market evidence.

No order path is approved.

## Next Safe Step

Prepare or provide a verified real `paf_lookahead_bars.csv`, then use the Checkpoint BA approval phrase for the real Checkpoint BB offline join.
