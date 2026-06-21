# Diagnostics: EURUSD_H1_10000_out_of_sample

- Symbol: `EURUSD`
- Timeframe: `H1`
- Phase: `out_of_sample`
- Execution: `PASS`
- Phase classification: `VALID_RESULT`
- Case classification: `TRAIN_FAILED_VALIDATION_OOS_PASS`
- Recommendation: `RESEARCH_MORE`

## Signal Diagnostics

| Metric | Value |
|---|---:|
| accepted_signals | 62 |
| rejected_signals | 251 |
| signal_acceptance_rate_pct | 19.81 |
| no_signal_bars | 1922 |
| unsafe_regime_blocks | 613 |
| spread_blocks | 182 |
| max_open_order_blocks | 108 |
| losing_streak_blocks | 143 |
| broker_minimum_lot_risk_budget_blocks | 0 |
| buy_count | 124 |
| sell_count | 189 |
| average_sl_distance | 0.002767 |
| average_tp_distance | 0.005248 |
| average_raw_lot | 0.040987 |
| average_normalized_lot | 0.035323 |
| average_actual_risk_money | 8.49129 |
| average_logged_spread | 21.097436 |

## GOLD / Risk Budget Review

| Metric | Value |
|---|---:|
| risk_percent | 0.1 |
| deposit | 10000.0 |
| symbol_min_lot | 0.01 |
| typical_blocked_raw_lot | None |
| typical_blocked_sl_distance | 0.002767 |
| estimated_minimum_deposit_for_min_lot | None |
| current_deposit_insufficient_for_min_lot | False |
| suggested_next_deposit_assumption_research_only | None |

This diagnostic is not an instruction to force minimum lot or increase risk.
