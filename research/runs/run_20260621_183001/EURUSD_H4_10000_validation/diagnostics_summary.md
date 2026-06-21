# Diagnostics: EURUSD_H4_10000_validation

- Symbol: `EURUSD`
- Timeframe: `H4`
- Phase: `validation`
- Execution: `PASS`
- Phase classification: `INSUFFICIENT_TRADES`
- Case classification: `REJECTED`
- Recommendation: `REJECT_FOR_NOW`

## Signal Diagnostics

| Metric | Value |
|---|---:|
| accepted_signals | 6 |
| rejected_signals | 202 |
| signal_acceptance_rate_pct | 2.88 |
| no_signal_bars | 951 |
| unsafe_regime_blocks | 388 |
| spread_blocks | 249 |
| max_open_order_blocks | 9 |
| losing_streak_blocks | 193 |
| broker_minimum_lot_risk_budget_blocks | 0 |
| buy_count | 155 |
| sell_count | 53 |
| average_sl_distance | 0.006857 |
| average_tp_distance | 0.013432 |
| average_raw_lot | 0.015067 |
| average_normalized_lot | 0.011667 |
| average_actual_risk_money | 7.668333 |
| average_logged_spread | 26.876774 |

## GOLD / Risk Budget Review

| Metric | Value |
|---|---:|
| risk_percent | 0.1 |
| deposit | 10000.0 |
| symbol_min_lot | 0.01 |
| typical_blocked_raw_lot | None |
| typical_blocked_sl_distance | 0.006857 |
| estimated_minimum_deposit_for_min_lot | None |
| current_deposit_insufficient_for_min_lot | False |
| suggested_next_deposit_assumption_research_only | None |

This diagnostic is not an instruction to force minimum lot or increase risk.
