# Checkpoint CG: PAF First-Touch Attribution

## Status

`DONE_FOR_REVIEW`

## Scope

Checkpoint CG adds and runs an offline attribution tool for Checkpoint CE first-touch labels.

This checkpoint does not:

- run MT5
- run Strategy Tester
- change EA/source code
- change presets
- rerun first-touch labels
- optimize parameters
- add order logic
- claim profitability

## Tool Added

- `tools/paf_first_touch_attribution.py`

## Inputs

- `research/results/checkpoint_ce_paf_first_touch_relabel/paf_shadow_outcomes_first_touch_relabel.csv`

## Outputs

- `research/results/checkpoint_cg_first_touch_attribution/first_touch_attribution_by_dimension.csv`
- `research/results/checkpoint_cg_first_touch_attribution/first_touch_attribution_summary.json`
- `research/results/checkpoint_cg_first_touch_attribution/first_touch_attribution_summary.md`
- `research/results/checkpoint_cg_first_touch_attribution/first_touch_attribution_guardrail_summary.md`

## Dry Run Result

- Status: `PASS_OFFLINE_FIRST_TOUCH_ATTRIBUTION`
- Rows read: `33`
- Relabel-ready rows: `17`
- Data-missing rows: `2`
- Direction-missing rows: `14`
- Classification: `NOT_READY_FOR_ORDER_LOGIC`

## Diagnostic Findings

- `POSSIBLE_FIBO_PULLBACK` is the largest class and is `SL_FIRST_DOMINANT` in every horizon.
- `POSSIBLE_ZONE_REJECTION` has only `2` relabel-ready rows, too small to conclude.
- `ASIA` and `OVERLAP` show SL-first concentration in this tiny sample.
- `LONDON` and `NEW_YORK` look less bad in this tiny sample, but must not be turned into a session filter yet.
- `NORMAL_SPREAD` and `trend` contain most rows, so spread/regime separation remains weak.

## Decision

- `OFFLINE_FIRST_TOUCH_ATTRIBUTION_TOOL_ADDED`
- `OFFLINE_FIRST_TOUCH_ATTRIBUTION_DRY_RUN_PASS`
- `CLASSIFICATION_SESSION_SPREAD_REGIME_ATTRIBUTION_CREATED`
- `FIBO_PULLBACK_SL_FIRST_DOMINANT`
- `DIRECTION_MISSING_REMAINS_MAJOR_BLOCKER`
- `SAMPLE_SIZE_TOO_SMALL_FOR_ORDER_LOGIC`
- `ORDER_LOGIC_NOT_APPROVED`
- `OPTIMIZATION_NOT_APPROVED`
- `MT5_NOT_RUN`
- `STRATEGY_TESTER_NOT_RUN`
- `EA_SOURCE_NOT_CHANGED`
- `PRESETS_NOT_CHANGED`
- `NO_PROFITABILITY_CLAIM`

## Next Safe Step

Checkpoint CH should interpret the attribution output and decide the next diagnostic question. It should not optimize, add order logic, or claim profitability.
