# Diagnostics: EURUSD_M30_10000_train

- Symbol: `EURUSD`
- Timeframe: `M30`
- Phase: `train`
- Execution: `PASS`
- Phase classification: `INSUFFICIENT_TRADES`
- Case classification: `REJECTED`
- Recommendation: `REJECT_FOR_NOW`

## Signal Diagnostics

| Metric | Value |
|---|---:|
| accepted_signals | 21 |
| rejected_signals | 3051 |
| signal_acceptance_rate_pct | 0.68 |
| no_signal_bars | 16076 |
| unsafe_regime_blocks | 5675 |
| spread_blocks | 1000 |
| max_open_order_blocks | 48 |
| losing_streak_blocks | 3003 |
| broker_minimum_lot_risk_budget_blocks | 0 |
| buy_count | 1434 |
| sell_count | 1638 |
| average_sl_distance | 0.002442 |
| average_tp_distance | 0.00449 |
| average_raw_lot | 0.046248 |
| average_normalized_lot | 0.041429 |
| average_actual_risk_money | 8.838571 |
| average_logged_spread | 18.603972 |

## GOLD / Risk Budget Review

| Metric | Value |
|---|---:|
| risk_percent | 0.1 |
| deposit | 10000.0 |
| symbol_min_lot | 0.01 |
| typical_blocked_raw_lot | None |
| typical_blocked_sl_distance | 0.002442 |
| estimated_minimum_deposit_for_min_lot | None |
| current_deposit_insufficient_for_min_lot | False |
| suggested_next_deposit_assumption_research_only | None |

This diagnostic is not an instruction to force minimum lot or increase risk.
