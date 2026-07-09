# Checkpoint CE: PAF Offline First-Touch Relabel Tool and Dry Run

## Status

`DONE_FOR_REVIEW`

## Scope

Checkpoint CE adds and runs an offline first-touch relabeling tool using Checkpoint CC `offline_atr_14`.

This checkpoint does not:

- run MT5
- run Strategy Tester
- change EA/source code
- change presets
- change production validator
- generate orders
- optimize parameters
- compute real trade profitability
- claim profitability

## Tool Added

- `tools/paf_first_touch_relabel.py`

## Inputs

- `research/results/checkpoint_cc_offline_atr_enrichment/paf_shadow_outcomes_atr_enriched.csv`
- `research/results/checkpoint_bz_offline_joiner_run/paf_lookahead_bars.csv`

## Outputs

- `research/results/checkpoint_ce_paf_first_touch_relabel/paf_shadow_outcomes_first_touch_relabel.csv`
- `research/results/checkpoint_ce_paf_first_touch_relabel/first_touch_relabel_summary.json`
- `research/results/checkpoint_ce_paf_first_touch_relabel/first_touch_relabel_summary.md`
- `research/results/checkpoint_ce_paf_first_touch_relabel/first_touch_relabel_by_horizon.csv`
- `research/results/checkpoint_ce_paf_first_touch_relabel/first_touch_relabel_guardrail_summary.md`

## Dry Run Result

- Status: `PASS_OFFLINE_FIRST_TOUCH_RELABEL`
- Rows read: `33`
- Relabel-ready rows: `17`
- Data-missing rows: `2`
- Direction-missing rows: `14`

## Outcome Label Distribution

| Horizon | TP_FIRST | SL_FIRST | NO_RESOLUTION | AMBIGUOUS_SAME_BAR | DATA_MISSING | DIRECTION_MISSING |
|---:|---:|---:|---:|---:|---:|---:|
| 6 | 5 | 9 | 2 | 1 | 2 | 14 |
| 12 | 6 | 10 | 0 | 1 | 2 | 14 |
| 24 | 6 | 10 | 0 | 1 | 2 | 14 |
| 48 | 6 | 10 | 0 | 1 | 2 | 14 |

## Decision

- `OFFLINE_FIRST_TOUCH_RELABEL_TOOL_ADDED`
- `OFFLINE_FIRST_TOUCH_RELABEL_DRY_RUN_PASS`
- `OFFLINE_ATR_14_USED_ONLY`
- `TP_SL_MULTIPLES_FIXED`
- `DIRECTION_MISSING_STAYS_BLOCKED`
- `ATR_MISSING_STAYS_DATA_MISSING`
- `SAME_BAR_AMBIGUITY_HANDLED`
- `MT5_NOT_RUN`
- `STRATEGY_TESTER_NOT_RUN`
- `EA_SOURCE_NOT_CHANGED`
- `PRESETS_NOT_CHANGED`
- `NO_OPTIMIZATION`
- `NO_PROFITABILITY_CLAIM`

## Important Limitation

These labels are hypothetical shadow diagnostics. They are not real trades and must not be interpreted as profit/loss or approval for live/demo trading.

## Next Safe Step

Checkpoint CF should be a diagnostic interpretation package only. It should summarize label distribution, data quality, and blocker status without optimizing or adding order logic.
