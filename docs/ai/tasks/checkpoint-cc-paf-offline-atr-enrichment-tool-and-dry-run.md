# Checkpoint CC: PAF Offline ATR Enrichment Tool and Dry Run

## Status

`DONE_FOR_REVIEW`

## Scope

Checkpoint CC adds and runs an offline ATR enrichment tool against existing Checkpoint BZ artifacts.

This checkpoint does not:

- run MT5
- run Strategy Tester
- change EA/source code
- change presets
- change production validator
- rerun first-touch labels
- optimize ATR period
- claim profitability

## Tool Added

- `tools/paf_offline_atr_enrichment.py`

## Inputs

- `research/results/checkpoint_bz_offline_joiner_run/paf_lookahead_bars.csv`
- `research/results/checkpoint_bz_offline_joiner_run/paf_shadow_outcomes_enriched.csv`

## Outputs

- `research/results/checkpoint_cc_offline_atr_enrichment/paf_shadow_outcomes_atr_enriched.csv`
- `research/results/checkpoint_cc_offline_atr_enrichment/offline_atr_enrichment_summary.json`
- `research/results/checkpoint_cc_offline_atr_enrichment/offline_atr_enrichment_summary.md`
- `research/results/checkpoint_cc_offline_atr_enrichment/offline_atr_data_completeness.csv`
- `research/results/checkpoint_cc_offline_atr_enrichment/offline_atr_guardrail_summary.md`

## Dry Run Result

- Status: `PASS_OFFLINE_ATR_ENRICHMENT`
- Bars read: `230`
- Event rows read: `33`
- Events with valid offline ATR: `17`
- Events missing ATR: `2`
- Direction-missing rows: `14`
- Unknown irregular gaps: `0`

## Method

- ATR period: `14`
- Output column: `offline_atr_14`
- ATR method: `simple_average_true_range`
- ATR alignment: completed H1 bars strictly before event bar

This is intentionally more conservative than using the event bar high/low because the event bar may still be forming at diagnostic time.

## Decision

- `OFFLINE_ATR_ENRICHMENT_TOOL_ADDED`
- `OFFLINE_ATR_ENRICHMENT_DRY_RUN_PASS`
- `OFFLINE_ATR_14_CREATED`
- `UNKNOWN_IRREGULAR_GAPS_ZERO`
- `FIRST_TOUCH_LABELS_NOT_RERUN`
- `MT5_NOT_RUN`
- `STRATEGY_TESTER_NOT_RUN`
- `EA_SOURCE_NOT_CHANGED`
- `PRESETS_NOT_CHANGED`
- `NO_OPTIMIZATION`
- `NO_PROFITABILITY_CLAIM`

## Known Issue

A local ignored `tools/__pycache__/` folder was created by Python syntax checking in the isolated worktree. It is ignored by git and not staged, but Windows denied deletion from this sandbox session. It must not be included in review packages or commits.

## Next Safe Step

Checkpoint CD should be an approval package for offline first-touch relabeling using the ATR-enriched rows from Checkpoint CC.
