# Diagnostics: EURUSD_H1_10000_train

- Symbol: `EURUSD`
- Timeframe: `H1`
- Phase: `train`
- Execution: `PASS`
- Phase classification: `INSUFFICIENT_TRADES`
- Case classification: `TRAIN_FAILED_VALIDATION_OOS_PASS`
- Recommendation: `RESEARCH_MORE`

## Signal Diagnostics

| Metric | Value |
|---|---:|
| accepted_signals | 22 |
| rejected_signals | 1592 |
| signal_acceptance_rate_pct | 1.36 |
| no_signal_bars | 8607 |
| unsafe_regime_blocks | 2191 |
| spread_blocks | 584 |
| max_open_order_blocks | 34 |
| losing_streak_blocks | 1558 |
| broker_minimum_lot_risk_budget_blocks | 0 |
| buy_count | 741 |
| sell_count | 873 |
| average_sl_distance | 0.003541 |
| average_tp_distance | 0.006612 |
| average_raw_lot | 0.029968 |
| average_normalized_lot | 0.024545 |
| average_actual_risk_money | 8.048636 |
| average_logged_spread | 19.113725 |

## GOLD / Risk Budget Review

| Metric | Value |
|---|---:|
| risk_percent | 0.1 |
| deposit | 10000.0 |
| symbol_min_lot | 0.01 |
| typical_blocked_raw_lot | None |
| typical_blocked_sl_distance | 0.003541 |
| estimated_minimum_deposit_for_min_lot | None |
| current_deposit_insufficient_for_min_lot | False |
| suggested_next_deposit_assumption_research_only | None |

This diagnostic is not an instruction to force minimum lot or increase risk.
