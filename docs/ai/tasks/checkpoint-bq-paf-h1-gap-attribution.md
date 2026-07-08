# Checkpoint BQ: PAF H1 Gap Attribution

## Status

`DONE_FOR_REVIEW`

## Scope

Checkpoint BQ inspects the validation gaps detected during Checkpoint BP after the offline PAF pipeline normalized the real `GOLD#` H1 CSV.

This checkpoint is diagnosis-only:

- no MT5 run
- no Strategy Tester run
- no EA/source change
- no preset change
- no optimization
- no profitability interpretation
- no validator bypass
- no joiner rerun

## Input

- Normalized bars: `research/results/checkpoint_bp_real_csv_pipeline/paf_lookahead_bars.csv`
- Source checkpoint: Checkpoint BP
- Original validator issue: `detected gaps larger than expected timeframe step: 6`

## Output

- `research/results/checkpoint_bq_gap_attribution/gap_attribution.csv`
- `research/results/checkpoint_bq_gap_attribution/gap_attribution_summary.md`
- `docs/83_Checkpoint_BQ_PAF_H1_Gap_Attribution_TH.md`

## Findings

Total gaps greater than one H1 step: `6`

- `WEEKEND_MARKET_CLOSURE`: `1`
- `SHORT_SESSION_OR_HISTORY_GAP`: `5`

The gaps are not all standard weekend closures. The daily two-hour gaps need manual/broker-session review before validator behavior is changed.

## Decision

- `GAP_ATTRIBUTION_DONE`
- `GAPS_REQUIRE_MANUAL_REVIEW`
- `JOINER_STILL_BLOCKED`
- `VALIDATOR_NOT_BYPASSED`
- `MT5_NOT_RUN`
- `STRATEGY_TESTER_NOT_RUN`
- `EA_SOURCE_NOT_CHANGED`
- `PRESETS_NOT_CHANGED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`

## Next Safe Step

Prepare a reviewed validator gap policy checkpoint before any joiner rerun. The next checkpoint should decide whether specific broker-session gaps, such as `23:00 -> 01:00`, can be treated as acceptable market-session gaps without masking true missing data.
