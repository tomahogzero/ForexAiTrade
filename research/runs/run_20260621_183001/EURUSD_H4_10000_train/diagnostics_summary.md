# Diagnostics: EURUSD_H4_10000_train

- Symbol: `EURUSD`
- Timeframe: `H4`
- Phase: `train`
- Execution: `PASS`
- Phase classification: `INSUFFICIENT_TRADES`
- Case classification: `REJECTED`
- Recommendation: `REJECT_FOR_NOW`

## Signal Diagnostics

| Metric | Value |
|---|---:|
| accepted_signals | 17 |
| rejected_signals | 453 |
| signal_acceptance_rate_pct | 3.62 |
| no_signal_bars | 1927 |
| unsafe_regime_blocks | 714 |
| spread_blocks | 482 |
| max_open_order_blocks | 40 |
| losing_streak_blocks | 413 |
| broker_minimum_lot_risk_budget_blocks | 0 |
| buy_count | 228 |
| sell_count | 242 |
| average_sl_distance | 0.007238 |
| average_tp_distance | 0.014098 |
| average_raw_lot | 0.014165 |
| average_normalized_lot | 0.01 |
| average_actual_risk_money | 7.237647 |
| average_logged_spread | 24.373722 |

## GOLD / Risk Budget Review

| Metric | Value |
|---|---:|
| risk_percent | 0.1 |
| deposit | 10000.0 |
| symbol_min_lot | 0.01 |
| typical_blocked_raw_lot | None |
| typical_blocked_sl_distance | 0.007238 |
| estimated_minimum_deposit_for_min_lot | None |
| current_deposit_insufficient_for_min_lot | False |
| suggested_next_deposit_assumption_research_only | None |

This diagnostic is not an instruction to force minimum lot or increase risk.
