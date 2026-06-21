# Diagnostics: USDJPY_HASH_H1_10000_out_of_sample

- Symbol: `USDJPY#`
- Timeframe: `H1`
- Phase: `out_of_sample`
- Execution: `PASS`
- Phase classification: `INSUFFICIENT_TRADES`
- Case classification: `REJECTED`
- Recommendation: `NEEDS_TIMEFRAME_REVIEW`

## Signal Diagnostics

| Metric | Value |
|---|---:|
| accepted_signals | 12 |
| rejected_signals | 344 |
| signal_acceptance_rate_pct | 3.37 |
| no_signal_bars | 1899 |
| unsafe_regime_blocks | 593 |
| spread_blocks | 166 |
| max_open_order_blocks | 6 |
| losing_streak_blocks | 338 |
| broker_minimum_lot_risk_budget_blocks | 0 |
| buy_count | 248 |
| sell_count | 108 |
| average_sl_distance | 0.39175 |
| average_tp_distance | 0.742167 |
| average_raw_lot | 0.041742 |
| average_normalized_lot | 0.035833 |
| average_actual_risk_money | 8.476667 |
| average_logged_spread | 13.382424 |

## GOLD / Risk Budget Review

| Metric | Value |
|---|---:|
| risk_percent | 0.1 |
| deposit | 10000.0 |
| symbol_min_lot | 0.01 |
| typical_blocked_raw_lot | None |
| typical_blocked_sl_distance | 0.39175 |
| estimated_minimum_deposit_for_min_lot | None |
| current_deposit_insufficient_for_min_lot | False |
| suggested_next_deposit_assumption_research_only | None |

This diagnostic is not an instruction to force minimum lot or increase risk.
