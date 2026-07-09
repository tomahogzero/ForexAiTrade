# Checkpoint CA: PAF ATR Enrichment / Data Completeness Plan

## Status

`DONE_FOR_REVIEW`

## Scope

Checkpoint CA plans ATR enrichment after Checkpoint BZ showed that first-touch labels remain unavailable.

This checkpoint does not:

- run MT5
- run Strategy Tester
- change EA/source code
- change presets
- change production validator
- run joiner
- compute new outcomes
- optimize
- claim profitability

## BZ Limitation

- Shadow rows: `33`
- Joined rows: `19`
- Direction missing rows: `14`
- MFE/MAE context: available
- First-touch labels: unavailable
- Limitation: `atr is missing or invalid`

## Recommended Next Approach

Use offline ATR enrichment first:

- calculate ATR from normalized `GOLD#` H1 bars
- use a fixed diagnostic ATR period such as 14
- do not optimize ATR period
- do not use future bars for event ATR
- label output as offline-computed ATR
- keep data-missing labels when required fields are absent

## Decision

- `ATR_ENRICHMENT_PLAN_CREATED`
- `BZ_LIMITATION_CONFIRMED`
- `FIRST_TOUCH_LABELS_STILL_BLOCKED`
- `OFFLINE_ATR_OPTION_RECOMMENDED`
- `NO_ATR_OPTIMIZATION_APPROVED`
- `JOINER_NOT_RERUN`
- `MT5_NOT_RUN`
- `STRATEGY_TESTER_NOT_RUN`
- `EA_SOURCE_NOT_CHANGED`
- `PRESETS_NOT_CHANGED`
- `NO_PROFITABILITY_CLAIM`

## Next Safe Step

Checkpoint CB should be an approval package for offline ATR enrichment. It should not run MT5 or Strategy Tester and should not interpret profitability.
