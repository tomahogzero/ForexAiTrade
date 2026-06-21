# Trade-Level Diagnostics Summary

Selected RunId: `run_20260621_214917`

This summary uses existing MT5 HTML reports only. No MT5 run was performed. Main tables are scoped to the selected run only.

| Case | Trades | Net Profit | Win Rate % | PF | Avg Hold Min | Max Consecutive Losses | Exit Counts |
|---|---:|---:|---:|---:|---:|---:|---|
| EURUSD_H1_RISKGATE_FIXED_COOLDOWN_24BARS_10000 | 931 | -656.97 | 53.17 | 0.8248 | 680.4577 | 12 | {"SL": 823, "TP": 108} |
| EURUSD_H1_RISKGATE_NEXT_DAY_RESET_10000 | 956 | -639.23 | 53.35 | 0.8335 | 680.2123 | 8 | {"SL": 843, "TP": 113} |
| EURUSD_H1_RISKGATE_NORMAL_10000 | 189 | 61.45 | 55.56 | 1.0864 | 722.9193 | 7 | {"SL": 160, "TP": 29} |
| EURUSD_H1_RISKGATE_NO_LOSING_STREAK_GATE_10000 | 997 | -596.53 | 53.56 | 0.8504 | 690.4509 | 7 | {"SL": 876, "TP": 121} |

## Data Limitations

- MT5 HTML report gives deal/order history, but not a reliable magic-number column.
- Exit reason is inferred from close deal comments such as `sl` and `tp`.
- Trailing stop or breakeven movement is not directly visible unless future EA logs explicitly record position modification events.
- Duplicate case/phase reports detected outside the selected scope: 5. They are recorded separately in `duplicates_detected.json` and are not merged into this table.
