# Checkpoint DB: PAF Data Collection Expansion Result

## Status

Executed exactly the approved Checkpoint DB diagnostic-only Strategy Tester scope.

## RunId

`run_20260709_212026`

## Scope

- Symbol: GOLD#
- Timeframe: H1
- Windows:
  - 2026-03-29 to 2026-04-05
  - 2026-04-05 to 2026-04-12
  - 2026-04-12 to 2026-04-19
  - 2026-04-19 to 2026-04-26
- Strategy Tester only
- No optimization
- No market orders
- No pending orders
- No position modification
- No lot/risk increase
- No profitability interpretation

## Result

All four windows produced parseable reports and PAF diagnostics.

| Window | Execution | Report | Trades | Diagnostics | Forbidden | Baseline fallback |
|---|---|---|---:|---:|---:|---:|
| DB-W1 | PASS | FOUND | 0 | 58 | 0 | 0 |
| DB-W2 | PASS | FOUND | 0 | 94 | 0 | 0 |
| DB-W3 | PASS | FOUND | 0 | 82 | 0 | 0 |
| DB-W4 | PASS | FOUND | 0 | 113 | 0 | 0 |

## Data Gate Update

DB added:

- diagnostic rows: 347
- possible setup rows: 83
- usable direction rows: 43

Combined CV + CY + DB:

- diagnostic rows: 621
- possible setup rows: 174
- usable direction rows: 106

Gate result:

- diagnostic interpretation gate 100: PASS_LOW_MARGIN
- rule-candidate gate 300: FAIL

## Boundary

Passing 100 usable direction rows only allows a future artifact review / diagnostic interpretation checkpoint.

It does not approve:

- order logic
- market orders
- pending orders
- position modification
- optimization
- lot/risk increase
- demo/live forward testing
- profitability claims

## Recommended Next Checkpoint

Checkpoint DC: artifact-only diagnostic interpretation review using CV + CY + DB.

DC should not run MT5 and should not change EA/source or presets.
