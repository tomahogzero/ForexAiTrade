# Diagnostics: EURUSD_H4_10000_out_of_sample

- Symbol: `EURUSD`
- Timeframe: `H4`
- Phase: `out_of_sample`
- Execution: `PASS`
- Phase classification: `INSUFFICIENT_TRADES`
- Case classification: `REJECTED`
- Recommendation: `REJECT_FOR_NOW`

## Signal Diagnostics

| Metric | Value |
|---|---:|
| accepted_signals | 27 |
| rejected_signals | 55 |
| signal_acceptance_rate_pct | 32.93 |
| no_signal_bars | 466 |
| unsafe_regime_blocks | 167 |
| spread_blocks | 113 |
| max_open_order_blocks | 53 |
| losing_streak_blocks | 0 |
| broker_minimum_lot_risk_budget_blocks | 2 |
| buy_count | 37 |
| sell_count | 45 |
| average_sl_distance | 0.005315 |
| average_tp_distance | 0.010223 |
| average_raw_lot | 0.019985 |
| average_normalized_lot | 0.015185 |
| average_actual_risk_money | 7.56037 |
| average_logged_spread | 25.085308 |

## GOLD / Risk Budget Review

| Metric | Value |
|---|---:|
| risk_percent | 0.1 |
| deposit | 10000.0 |
| symbol_min_lot | 0.01 |
| typical_blocked_raw_lot | 0.0093 |
| typical_blocked_sl_distance | 0.01076 |
| estimated_minimum_deposit_for_min_lot | 10752.69 |
| current_deposit_insufficient_for_min_lot | True |
| suggested_next_deposit_assumption_research_only | 50000 |

This diagnostic is not an instruction to force minimum lot or increase risk.
