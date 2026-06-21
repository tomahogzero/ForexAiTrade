# Diagnostics: USDJPY_HASH_H1_10000_train

- Symbol: `USDJPY#`
- Timeframe: `H1`
- Phase: `train`
- Execution: `PASS`
- Phase classification: `INSUFFICIENT_TRADES`
- Case classification: `REJECTED`
- Recommendation: `NEEDS_TIMEFRAME_REVIEW`

## Signal Diagnostics

| Metric | Value |
|---|---:|
| accepted_signals | 13 |
| rejected_signals | 1736 |
| signal_acceptance_rate_pct | 0.74 |
| no_signal_bars | 8651 |
| unsafe_regime_blocks | 2012 |
| spread_blocks | 614 |
| max_open_order_blocks | 45 |
| losing_streak_blocks | 1691 |
| broker_minimum_lot_risk_budget_blocks | 0 |
| buy_count | 1173 |
| sell_count | 576 |
| average_sl_distance | 0.643077 |
| average_tp_distance | 1.268 |
| average_raw_lot | 0.022392 |
| average_normalized_lot | 0.016154 |
| average_actual_risk_money | 6.926154 |
| average_logged_spread | 12.808403 |

## GOLD / Risk Budget Review

| Metric | Value |
|---|---:|
| risk_percent | 0.1 |
| deposit | 10000.0 |
| symbol_min_lot | 0.01 |
| typical_blocked_raw_lot | None |
| typical_blocked_sl_distance | 0.643077 |
| estimated_minimum_deposit_for_min_lot | None |
| current_deposit_insufficient_for_min_lot | False |
| suggested_next_deposit_assumption_research_only | None |

This diagnostic is not an instruction to force minimum lot or increase risk.
