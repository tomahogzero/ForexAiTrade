# PAF Offline Pipeline Runner Summary

This is an offline research pipeline summary. It does not run MT5, does not send orders, and does not prove profitability.

## Verdict

`FAIL`

## Inputs

- Raw CSV: `G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\manual_exports\GOLD_HASH_H1_20260301_20260310_raw_mt5_H1.csv`
- Bars CSV: `research\results\checkpoint_bp_real_csv_pipeline\paf_lookahead_bars.csv`
- Shadow outcomes: `research\results\paf_shadow_outcomes_all_cases.csv`
- Results root: `research\results\checkpoint_bp_real_csv_pipeline`
- Symbol: `GOLD#`
- Timeframe: `H1`
- Horizon bars: `48`
- Join horizons: `6,12,24,48`

## Stage Results

| Stage | Status | Return Code |
|---|---|---:|
| `normalize` | `PASS` | 0 |
| `validate` | `FAIL` | 2 |

## Stop Reason

`validation failed; joiner was not run`

## Guardrails

- Offline pipeline only.
- No MT5 run.
- No Strategy Tester run.
- No market orders or pending orders.
- No position modification.
- No optimization.
- No lot/risk increase.
- No profitability claim.
