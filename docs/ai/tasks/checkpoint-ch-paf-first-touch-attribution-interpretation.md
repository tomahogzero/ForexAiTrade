# Checkpoint CH: PAF First-Touch Attribution Interpretation

## Status

`DONE_FOR_REVIEW`

## Scope

Checkpoint CH interprets Checkpoint CG attribution outputs and turns them into a blocker-ranked research decision.

This checkpoint is documentation only.

It does not:

- run MT5
- run Strategy Tester
- change EA/source code
- change presets
- add order logic
- add market orders
- add pending orders
- optimize parameters
- increase lot/risk
- claim profitability

## Inputs Reviewed

- `research/results/checkpoint_cg_first_touch_attribution/first_touch_attribution_summary.md`
- `research/results/checkpoint_cg_first_touch_attribution/first_touch_attribution_summary.json`
- `research/results/checkpoint_cg_first_touch_attribution/first_touch_attribution_by_dimension.csv`

## Key Interpretation

- `POSSIBLE_FIBO_PULLBACK` is the largest class but remains `SL_FIRST_DOMINANT`.
- `POSSIBLE_ZONE_REJECTION` has too few relabel-ready rows to conclude.
- Session attribution is not strong enough to create a filter.
- Spread/regime attribution remains limited because most data is `NORMAL_SPREAD` and `trend`.
- Direction missing remains a major blocker.

## Decision

Final classification:

`NOT_READY_FOR_ORDER_LOGIC`

## Recommended Next Safe Step

Checkpoint CI should focus on data completeness before order logic:

- reduce `DIRECTION_MISSING`
- verify direction/TP/SL fields in joined offline data
- define what extra diagnostic fields are needed
- do not change trading behavior

## Progress Estimate

- Research infrastructure: `96%`
- PAF diagnostic pipeline: `88%`
- PAF data completeness: `60%`
- PAF order-readiness: `20%`
- Demo/live readiness: `0%`

