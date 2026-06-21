# Diagnostics: USDJPY_HASH_H1_10000_validation

- Symbol: `USDJPY#`
- Timeframe: `H1`
- Phase: `validation`
- Execution: `PASS`
- Phase classification: `VALID_RESULT`
- Case classification: `REJECTED`
- Recommendation: `REJECT_FOR_NOW`

## Signal Diagnostics

| Metric | Value |
|---|---:|
| accepted_signals | 91 |
| rejected_signals | 714 |
| signal_acceptance_rate_pct | 11.3 |
| no_signal_bars | 4446 |
| unsafe_regime_blocks | 921 |
| spread_blocks | 323 |
| max_open_order_blocks | 177 |
| losing_streak_blocks | 534 |
| broker_minimum_lot_risk_budget_blocks | 3 |
| buy_count | 390 |
| sell_count | 415 |
| average_sl_distance | 0.592549 |
| average_tp_distance | 1.160242 |
| average_raw_lot | 0.02813 |
| average_normalized_lot | 0.023297 |
| average_actual_risk_money | 8.155165 |
| average_logged_spread | 14.158562 |

## GOLD / Risk Budget Review

| Metric | Value |
|---|---:|
| risk_percent | 0.1 |
| deposit | 10000.0 |
| symbol_min_lot | 0.01 |
| typical_blocked_raw_lot | 0.0098 |
| typical_blocked_sl_distance | 1.476 |
| estimated_minimum_deposit_for_min_lot | 10204.08 |
| current_deposit_insufficient_for_min_lot | True |
| suggested_next_deposit_assumption_research_only | 50000 |

This diagnostic is not an instruction to force minimum lot or increase risk.
