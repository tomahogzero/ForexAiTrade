# Diagnostics: EURUSD_M30_10000_validation

- Symbol: `EURUSD`
- Timeframe: `M30`
- Phase: `validation`
- Execution: `PASS`
- Phase classification: `INSUFFICIENT_TRADES`
- Case classification: `REJECTED`
- Recommendation: `REJECT_FOR_NOW`

## Signal Diagnostics

| Metric | Value |
|---|---:|
| accepted_signals | 5 |
| rejected_signals | 1594 |
| signal_acceptance_rate_pct | 0.31 |
| no_signal_bars | 8260 |
| unsafe_regime_blocks | 2485 |
| spread_blocks | 630 |
| max_open_order_blocks | 9 |
| losing_streak_blocks | 1585 |
| broker_minimum_lot_risk_budget_blocks | 0 |
| buy_count | 923 |
| sell_count | 676 |
| average_sl_distance | 0.001446 |
| average_tp_distance | 0.002902 |
| average_raw_lot | 0.07524 |
| average_normalized_lot | 0.072 |
| average_actual_risk_money | 9.532 |
| average_logged_spread | 20.065891 |

## GOLD / Risk Budget Review

| Metric | Value |
|---|---:|
| risk_percent | 0.1 |
| deposit | 10000.0 |
| symbol_min_lot | 0.01 |
| typical_blocked_raw_lot | None |
| typical_blocked_sl_distance | 0.001446 |
| estimated_minimum_deposit_for_min_lot | None |
| current_deposit_insufficient_for_min_lot | False |
| suggested_next_deposit_assumption_research_only | None |

This diagnostic is not an instruction to force minimum lot or increase risk.
