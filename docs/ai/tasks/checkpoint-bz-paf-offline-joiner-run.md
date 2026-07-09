# Checkpoint BZ: PAF Offline Joiner Run

## Status

`DONE_WITH_LIMITATIONS`

## Approval

User approved:

`Approved to execute Checkpoint BZ offline PAF joiner for GOLD# H1 using BX PASS gap policy and offline files only.`

## Scope

Checkpoint BZ ran offline normalization and offline joiner only.

It did not:

- run MT5
- run Strategy Tester
- change EA/source code
- change presets
- change production validator
- send orders
- modify positions
- optimize
- claim profitability

## Outputs

`research/results/checkpoint_bz_offline_joiner_run/`

Key files:

- `paf_lookahead_bars.csv`
- `paf_bars_schema_normalization_summary.json`
- `paf_bars_schema_normalization_summary.md`
- `paf_shadow_outcomes_enriched.csv`
- `paf_lookahead_join_summary.json`
- `paf_lookahead_join_summary.md`
- `joiner_run_guardrail_summary.md`

## Result

- Normalization: `PASS`
- Rows normalized: `230`
- Shadow rows: `33`
- Joined rows: `19`
- Direction missing rows: `14`
- Outcome labels: still `DATA_MISSING`
- Limitation: `atr is missing or invalid`

## Decision

- `BZ_OFFLINE_JOINER_EXECUTED`
- `NORMALIZATION_PASS`
- `JOINER_OUTPUT_CREATED`
- `JOINED_ROWS_19`
- `DIRECTION_MISSING_ROWS_14`
- `ATR_MISSING_LIMITATION`
- `FIRST_TOUCH_LABELS_NOT_AVAILABLE_YET`
- `MFE_MAE_CONTEXT_AVAILABLE`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`

## Next Safe Step

Checkpoint CA should plan ATR enrichment or data-completeness handling before any outcome interpretation.
