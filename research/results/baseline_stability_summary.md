# Baseline Stability Summary

Scope: `EURUSD_H1_10000` only. This is diagnostics, not optimization and not profitability proof.

## Phase Stability

| Phase | Net Profit | Profit Factor | Trades | Relative DD | Accepted | Rejected | Unsafe Blocks | Spread Blocks | Losing Streak Blocks | Max Open Blocks |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| train | -40.96 | 0.57 | 22 | 0.59 | 22 | 1592 | 2191 | 584 | 1558 | 34 |
| validation | 61.38 | 1.16 | 105 | 0.63 | 105 | 710 | 1049 | 348 | 467 | 240 |
| out_of_sample | 41.03 | 1.18 | 62 | 0.59 | 62 | 251 | 613 | 182 | 143 | 108 |

## Interpretation

- EURUSD H1 remains `RESEARCH_MORE`, not a strong candidate.
- Validation and out-of-sample are positive, but train is negative and has only 22 trades.
- Low train trade count makes the train period unreliable as a proof of edge.
- Rejected signal counts and losing-streak blocks show that risk gates materially affect results.

## Monthly Breakdown Availability

Monthly closed-deal performance was extracted from the MT5 Deals table. Drawdown by month is not available from the exported report and remains blank.

## Trade Activity Warning

Trade activity is uneven across periods. Train has only 22 trades across 2 years, validation has 105 trades, and out-of-sample has 62 trades. Monthly results are concentrated in 9 reported active months. Positive OOS is not enough for forward/live readiness.
