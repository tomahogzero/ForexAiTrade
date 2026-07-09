# Checkpoint BS: PAF Gap Policy Dry-Run

## Status

`DONE_FOR_REVIEW`

## Scope

Checkpoint BS adds a standalone dry-run tool to classify attributed PAF gaps against a reviewed policy draft.

This checkpoint does not:

- run MT5
- run Strategy Tester
- change EA/source code
- change presets
- change the production validator
- run the joiner
- optimize parameters
- claim profitability

## Added Tool

`tools/paf_gap_policy_dry_run.py`

The tool reads:

- an attributed gap CSV
- a policy JSON

It writes:

- `gap_policy_dry_run.csv`
- `gap_policy_dry_run_summary.json`
- `gap_policy_dry_run_summary.md`

## Policy Draft

`research/policies/paf_gold_h1_gap_policy_draft.json`

The draft policy:

- accepts only reviewed Friday-to-Monday weekend closures
- keeps daily broker-session gaps in `review_required`
- keeps unknown gaps as blockers

## Dry-Run Result

Input:

- `research/results/checkpoint_bq_gap_attribution/gap_attribution.csv`

Output:

- `research/results/checkpoint_bs_gap_policy_dry_run/`

Result:

- Verdict: `REVIEW_REQUIRED`
- Gap count: `6`
- Accepted weekend gap: `1`
- Review-required daily broker-session gaps: `5`
- Joiner status: `blocked_by_gap_policy`

## Decision

- `GAP_POLICY_DRY_RUN_TOOL_ADDED`
- `POLICY_DRAFT_ADDED`
- `DRY_RUN_EXECUTED_OFFLINE_ONLY`
- `VERDICT_REVIEW_REQUIRED`
- `WEEKEND_GAP_ACCEPTED_1`
- `DAILY_SESSION_GAPS_REVIEW_REQUIRED_5`
- `JOINER_STILL_BLOCKED`
- `VALIDATOR_PRODUCTION_NOT_CHANGED`
- `MT5_NOT_RUN`
- `STRATEGY_TESTER_NOT_RUN`
- `EA_SOURCE_NOT_CHANGED`
- `PRESETS_NOT_CHANGED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`

## Next Safe Step

Checkpoint BT should review whether the daily broker-session gap rule can be explicitly approved for `GOLD#` H1. If approved later, the policy must remain symbol/timeframe-scoped and must not silence unknown gaps.
