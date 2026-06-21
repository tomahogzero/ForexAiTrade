# Diagnostics: EURUSD_H1_10000_validation

- Symbol: `EURUSD`
- Timeframe: `H1`
- Phase: `validation`
- Execution: `PASS`
- Phase classification: `VALID_RESULT`
- Case classification: `TRAIN_FAILED_VALIDATION_OOS_PASS`
- Recommendation: `RESEARCH_MORE`

## Signal Diagnostics

| Metric | Value |
|---|---:|
| accepted_signals | 105 |
| rejected_signals | 710 |
| signal_acceptance_rate_pct | 12.88 |
| no_signal_bars | 4308 |
| unsafe_regime_blocks | 1049 |
| spread_blocks | 348 |
| max_open_order_blocks | 240 |
| losing_streak_blocks | 467 |
| broker_minimum_lot_risk_budget_blocks | 3 |
| buy_count | 493 |
| sell_count | 322 |
| average_sl_distance | 0.003546 |
| average_tp_distance | 0.006684 |
| average_raw_lot | 0.033768 |
| average_normalized_lot | 0.028857 |
| average_actual_risk_money | 8.367429 |
| average_logged_spread | 20.580735 |

## GOLD / Risk Budget Review

| Metric | Value |
|---|---:|
| risk_percent | 0.1 |
| deposit | 10000.0 |
| symbol_min_lot | 0.01 |
| typical_blocked_raw_lot | 0.0082 |
| typical_blocked_sl_distance | 0.01231 |
| estimated_minimum_deposit_for_min_lot | 12195.12 |
| current_deposit_insufficient_for_min_lot | True |
| suggested_next_deposit_assumption_research_only | 50000 |

This diagnostic is not an instruction to force minimum lot or increase risk.
