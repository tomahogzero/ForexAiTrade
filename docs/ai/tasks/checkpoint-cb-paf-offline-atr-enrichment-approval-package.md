# Checkpoint CB: PAF Offline ATR Enrichment Approval Package

## Status

`DONE_FOR_REVIEW`

## Scope

Checkpoint CB creates an approval package for a future offline ATR enrichment step after Checkpoint BZ and CA.

This checkpoint does not:

- run MT5
- run Strategy Tester
- change EA/source code
- change presets
- change production validator
- run the joiner again
- compute new first-touch outcomes
- optimize ATR period
- claim profitability

## BZ Limitation

- Shadow rows: `33`
- Joined rows: `19`
- Direction missing rows: `14`
- MFE/MAE context: available
- First-touch labels: unavailable
- Reason: `atr is missing or invalid`

## Approval Package

The next checkpoint may only:

- read existing BZ offline artifacts
- compute offline ATR from normalized `GOLD#` H1 bars
- use fixed `ATR period = 14`
- enforce no-future-leakage ATR calculation
- produce data completeness artifacts

The next checkpoint must not:

- run MT5
- run Strategy Tester
- change EA/source code
- change presets
- optimize ATR period
- rerun first-touch labeling unless separately approved
- interpret profitability

## Required Inputs for Future Checkpoint

- `research/results/checkpoint_bz_offline_joiner_run/paf_lookahead_bars.csv`
- `research/results/checkpoint_bz_offline_joiner_run/paf_shadow_outcomes_enriched.csv`
- `research/results/checkpoint_bz_offline_joiner_run/paf_lookahead_join_summary.json`

## Future Output Proposal

- `research/results/checkpoint_cc_offline_atr_enrichment/paf_shadow_outcomes_atr_enriched.csv`
- `research/results/checkpoint_cc_offline_atr_enrichment/offline_atr_enrichment_summary.json`
- `research/results/checkpoint_cc_offline_atr_enrichment/offline_atr_enrichment_summary.md`
- `research/results/checkpoint_cc_offline_atr_enrichment/offline_atr_data_completeness.csv`
- `research/results/checkpoint_cc_offline_atr_enrichment/offline_atr_guardrail_summary.md`

## Decision

- `OFFLINE_ATR_ENRICHMENT_APPROVAL_PACKAGE_CREATED`
- `ATR_PERIOD_FIXED_FOR_DIAGNOSTIC_ONLY`
- `NO_ATR_OPTIMIZATION_APPROVED`
- `FUTURE_LEAKAGE_GUARD_REQUIRED`
- `FIRST_TOUCH_LABELS_STILL_BLOCKED`
- `JOINER_RERUN_NOT_APPROVED`
- `MT5_NOT_RUN`
- `STRATEGY_TESTER_NOT_RUN`
- `EA_SOURCE_NOT_CHANGED`
- `PRESETS_NOT_CHANGED`
- `NO_PROFITABILITY_CLAIM`

## Next Safe Step

Checkpoint CC should implement and dry-run the offline ATR enrichment tool only after this approval package is merged/reviewed.
