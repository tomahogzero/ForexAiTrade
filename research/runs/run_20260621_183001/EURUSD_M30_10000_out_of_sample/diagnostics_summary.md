# Diagnostics: EURUSD_M30_10000_out_of_sample

- Symbol: `EURUSD`
- Timeframe: `M30`
- Phase: `out_of_sample`
- Execution: `PASS`
- Phase classification: `VALID_RESULT`
- Case classification: `REJECTED`
- Recommendation: `REJECT_FOR_NOW`

## Signal Diagnostics

| Metric | Value |
|---|---:|
| accepted_signals | 71 |
| rejected_signals | 649 |
| signal_acceptance_rate_pct | 9.86 |
| no_signal_bars | 3692 |
| unsafe_regime_blocks | 1284 |
| spread_blocks | 307 |
| max_open_order_blocks | 150 |
| losing_streak_blocks | 499 |
| broker_minimum_lot_risk_budget_blocks | 0 |
| buy_count | 258 |
| sell_count | 462 |
| average_sl_distance | 0.001726 |
| average_tp_distance | 0.003279 |
| average_raw_lot | 0.070939 |
| average_normalized_lot | 0.065915 |
| average_actual_risk_money | 9.214507 |
| average_logged_spread | 21.024719 |

## GOLD / Risk Budget Review

| Metric | Value |
|---|---:|
| risk_percent | 0.1 |
| deposit | 10000.0 |
| symbol_min_lot | 0.01 |
| typical_blocked_raw_lot | None |
| typical_blocked_sl_distance | 0.001726 |
| estimated_minimum_deposit_for_min_lot | None |
| current_deposit_insufficient_for_min_lot | False |
| suggested_next_deposit_assumption_research_only | None |

This diagnostic is not an instruction to force minimum lot or increase risk.
