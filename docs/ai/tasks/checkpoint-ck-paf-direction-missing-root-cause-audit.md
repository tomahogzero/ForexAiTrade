# Checkpoint CK: PAF Direction Missing Root-Cause Audit

## Status

`DONE_FOR_REVIEW`

## Scope

Checkpoint CK adds and runs an offline-only root-cause audit for `DIRECTION_MISSING` rows.

It does not:

- run MT5
- run Strategy Tester
- change EA/source code
- change presets
- add order logic
- add market orders
- add pending orders
- optimize
- increase lot/risk
- claim profitability

## Tool Added

- `tools/paf_direction_missing_audit.py`

## Input

- `research/results/checkpoint_ce_paf_first_touch_relabel/paf_shadow_outcomes_first_touch_relabel.csv`

## Outputs

- `research/results/checkpoint_ck_paf_direction_missing_audit/direction_missing_summary.md`
- `research/results/checkpoint_ck_paf_direction_missing_audit/direction_missing_summary.json`
- `research/results/checkpoint_ck_paf_direction_missing_audit/direction_missing_rows.csv`
- `research/results/checkpoint_ck_paf_direction_missing_audit/direction_missing_root_cause_counts.csv`
- `research/results/checkpoint_ck_paf_direction_missing_audit/direction_missing_by_classification.csv`
- `research/results/checkpoint_ck_paf_direction_missing_audit/direction_missing_by_session.csv`
- `research/results/checkpoint_ck_paf_direction_missing_audit/direction_missing_guardrail_summary.md`

## Dry Run Result

- Status: `PASS_OFFLINE_DIRECTION_MISSING_AUDIT`
- Classification: `DIRECTION_COMPLETENESS_FAIL`
- Rows read: `33`
- Direction-missing rows: `14`

## Root Cause Result

- `FIBO_PULLBACK_EMA_DIRECTION_CONTEXT_MISSING`: `10`
- `ZONE_REJECTION_CANDLE_DIRECTION_CONTEXT_MISSING`: `4`

## Decision

`NOT_READY_FOR_ORDER_LOGIC`

## Recommended Next Checkpoint

Checkpoint CL should define diagnostics-only direction context fields before any EA/source implementation.

If EA/source changes are needed later, they require a separate reviewed checkpoint.

## Progress Estimate

- Research infrastructure: `96%`
- PAF diagnostic pipeline: `91%`
- PAF data completeness: `66%`
- PAF direction completeness: `58%`
- PAF order-readiness: `20%`
- Demo/live readiness: `0%`

