# Checkpoint BP: PAF Real CSV Offline Pipeline Result

Date: 2026-07-08

## Scope

Offline pipeline execution only.

No MT5 run, no Strategy Tester run, no EA/source code changes, no preset changes, no optimization, no lot/risk increase, no profitability claim, and no order path approval.

## Approval Received

`Approved to execute Checkpoint BP offline PAF pipeline on real GOLD# H1 bars CSV G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\manual_exports\GOLD_HASH_H1_20260301_20260310_raw_mt5_H1.csv for RunId run_20260707_172236.`

## Result

- Pipeline verdict: `FAIL`
- Stop reason: `validation failed; joiner was not run`
- Normalize stage: `PASS`
- Validate stage: `FAIL`
- Join stage: `NOT_RUN`

## Validation Summary

- Bar count: `139`
- Coverage from: `2026-03-02 01:00:00`
- Coverage to: `2026-03-10 00:00:00`
- Required coverage to: `2026-03-08 22:00:00`
- Event count: `33`
- Matched events: `33`
- Missing events: `0`
- Gap count: `6`
- Issue: `detected gaps larger than expected timeframe step: 6`

## Artifacts

Created under:

`research/results/checkpoint_bp_real_csv_pipeline/`

Files:

- `paf_bars_schema_normalization_summary.json`
- `paf_bars_schema_normalization_summary.md`
- `paf_lookahead_bars.csv`
- `paf_lookahead_bars_raw.csv`
- `paf_lookahead_bars_validation_summary.json`
- `paf_lookahead_bars_validation_summary.md`
- `paf_offline_pipeline_runner_summary.json`
- `paf_offline_pipeline_runner_summary.md`

No enriched joined output exists because joiner was not run.

## Interpretation

This is not profitability evidence.

The real H1 CSV is usable enough to normalize and match all 33 diagnostic events, but the current validator blocks join due to 6 large timeframe gaps.

Do not bypass the validator in this checkpoint.

## Decision

- `BP_APPROVAL_RECEIVED`
- `CSV_FILE_FOUND`
- `CSV_APPEARS_H1`
- `NORMALIZATION_PASS`
- `VALIDATION_FAIL_GAPS_DETECTED`
- `EVENT_MATCH_33_OF_33`
- `MISSING_EVENTS_0`
- `JOINER_NOT_RUN`
- `OFFLINE_PIPELINE_STOP_GATE_WORKED`
- `MT5_NOT_RUN`
- `STRATEGY_TESTER_NOT_RUN`
- `ORDER_PATH_STILL_BLOCKED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`

## Next Safe Step

Create a follow-up checkpoint to inspect the 6 detected gaps and decide whether they are expected market-session/weekend gaps or true missing data. Do not implement orders or optimize.
