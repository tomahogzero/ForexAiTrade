# Checkpoint BM: PAF Offline Result Review Plan

Date: 2026-07-08

## Scope

Documentation-only review plan.

This checkpoint does not run MT5, does not run Strategy Tester, does not run the offline pipeline, does not change EA/source code, does not change presets, does not optimize, does not increase lot/risk, and does not claim profitability.

## Purpose

Define how Codex should review future offline PAF pipeline outputs after a real `GOLD#` H1 CSV is provided and Checkpoint BL is explicitly approved.

The goal is to prevent shadow outcomes from being over-interpreted as live-trading evidence.

## Expected Future Artifacts

Future Checkpoint BL output should include:

- `paf_offline_pipeline_runner_summary.json`
- `paf_offline_pipeline_runner_summary.md`
- `paf_lookahead_bars_validation_summary.json`
- `paf_lookahead_bars_validation_summary.md`
- `paf_shadow_outcomes_enriched.csv`
- `paf_lookahead_join_summary.json`
- `paf_lookahead_join_summary.md`
- normalization summary if raw CSV was used

## Review Gates

Review must verify:

- CSV source and symbol/timeframe are documented
- coverage is sufficient for the configured horizon
- validator passed
- event matching is sufficient
- missing events are understood
- joined row counts match summary counts
- direction context is sufficient
- ambiguous same-bar count is not too high
- synthetic and real data are not mixed
- no profitability claim is made
- order path remains blocked

## Recommended Classifications

Use one of:

- `OFFLINE_PIPELINE_PASS_REVIEWABLE`
- `VALIDATOR_FAIL_NEEDS_FIX`
- `COVERAGE_INSUFFICIENT`
- `EVENT_MATCH_INSUFFICIENT`
- `DIRECTION_CONTEXT_INSUFFICIENT`
- `AMBIGUITY_TOO_HIGH`
- `NON_BROKER_COMPARABLE_DIAGNOSTIC_ONLY`
- `SAMPLE_TOO_SMALL`
- `RESULT_INTERESTING_NEEDS_MORE_WINDOWS`
- `REJECT_ORDER_PATH_FOR_NOW`

Do not use:

- `PROFITABLE`
- `LIVE_READY`
- `DEMO_READY`
- `ORDER_APPROVED`
- `OPTIMIZATION_READY`

## Interpretation Limits

Shadow outcome labels are offline observations only.

- `TP_FIRST` is not real profit.
- `SL_FIRST` is not complete strategy failure by itself.
- `NO_TOUCH` may indicate horizon or target-distance issues.
- `AMBIGUOUS_SAME_BAR` must remain conservative and must not be counted as a win.
- One window is not enough for strategy approval.
- Gold results do not transfer to EURUSD or other symbols.

## Required Future Review Summary

Future review should report:

- RunId
- CSV path
- CSV source
- symbol/timeframe
- coverage
- validator status
- joined rows
- missing events
- outcome distribution
- direction distribution
- ambiguous same-bar count
- main blocker
- classification
- order path status
- profitability claim status
- next step

## Decision

- `OFFLINE_RESULT_REVIEW_PLAN_DEFINED`
- `REAL_CSV_PATH_STILL_REQUIRED`
- `OFFLINE_PIPELINE_NOT_RUN`
- `MT5_NOT_RUN`
- `STRATEGY_TESTER_NOT_RUN`
- `ORDER_PATH_STILL_BLOCKED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`

## Next Safe Step

Wait for the real `GOLD#` H1 CSV absolute path and explicit Checkpoint BL approval phrase before running the offline pipeline.
