# Checkpoint CD: PAF Offline First-Touch Relabel Approval Package

## Status

`DONE_FOR_REVIEW`

## Scope

Checkpoint CD creates an approval package for a future offline first-touch relabeling step using Checkpoint CC `offline_atr_14`.

This checkpoint does not:

- run MT5
- run Strategy Tester
- change EA/source code
- change presets
- change production validator
- run first-touch relabeling
- compute R-multiple
- optimize parameters
- claim profitability

## Source Evidence

Checkpoint CC result:

- Status: `PASS_OFFLINE_ATR_ENRICHMENT`
- Bars read: `230`
- Event rows: `33`
- Events with valid `offline_atr_14`: `17`
- Events missing ATR: `2`
- Direction-missing rows: `14`
- Unknown irregular gaps: `0`

## Approval Package

The next checkpoint may only:

- read existing CC ATR-enriched rows
- read existing BZ lookahead bars
- use `offline_atr_14`
- use fixed TP/SL multiples from BZ: `1.5` / `1.0`
- use horizons `6,12,24,48`
- relabel first-touch outcomes offline
- keep incomplete rows as `DATA_MISSING` or `DIRECTION_MISSING`

The next checkpoint must not:

- run MT5
- run Strategy Tester
- change EA/source code
- change presets
- optimize ATR/TP/SL/horizons
- interpret profitability
- generate orders

## Expected Future Outputs

- `research/results/checkpoint_ce_paf_first_touch_relabel/paf_shadow_outcomes_first_touch_relabel.csv`
- `research/results/checkpoint_ce_paf_first_touch_relabel/first_touch_relabel_summary.json`
- `research/results/checkpoint_ce_paf_first_touch_relabel/first_touch_relabel_summary.md`
- `research/results/checkpoint_ce_paf_first_touch_relabel/first_touch_relabel_by_horizon.csv`
- `research/results/checkpoint_ce_paf_first_touch_relabel/first_touch_relabel_guardrail_summary.md`

## Decision

- `FIRST_TOUCH_RELABEL_APPROVAL_PACKAGE_CREATED`
- `OFFLINE_ATR_14_REQUIRED`
- `ATR_READY_ROWS_ONLY_FOR_RELABEL`
- `DIRECTION_MISSING_STAYS_BLOCKED`
- `ATR_MISSING_STAYS_DATA_MISSING`
- `SAME_BAR_AMBIGUITY_REQUIRED`
- `NO_OPTIMIZATION_APPROVED`
- `MT5_NOT_RUN`
- `STRATEGY_TESTER_NOT_RUN`
- `EA_SOURCE_NOT_CHANGED`
- `PRESETS_NOT_CHANGED`
- `NO_PROFITABILITY_CLAIM`

## Next Safe Step

Checkpoint CE should implement and dry-run offline first-touch relabeling using `offline_atr_14` only after CD is merged/reviewed.
