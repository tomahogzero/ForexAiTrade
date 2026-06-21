# Diagnostics: GOLD_HASH_H4_30000_validation

- Symbol: `GOLD#`
- Timeframe: `H4`
- Phase: `validation`
- Execution: `PASS`
- Phase classification: `NO_RISK_BUDGET`
- Case classification: `REJECTED`
- Recommendation: `NEEDS_RISK_BUDGET_REVIEW`

## Signal Diagnostics

| Metric | Value |
|---|---:|
| accepted_signals | 0 |
| rejected_signals | 178 |
| signal_acceptance_rate_pct | 0.0 |
| no_signal_bars | 894 |
| unsafe_regime_blocks | 464 |
| spread_blocks | 11 |
| max_open_order_blocks | 0 |
| losing_streak_blocks | 0 |
| broker_minimum_lot_risk_budget_blocks | 178 |
| buy_count | 169 |
| sell_count | 9 |
| average_sl_distance | None |
| average_tp_distance | None |
| average_raw_lot | None |
| average_normalized_lot | None |
| average_actual_risk_money | None |
| average_logged_spread | 19.371134 |

## GOLD / Risk Budget Review

| Metric | Value |
|---|---:|
| risk_percent | 0.05 |
| deposit | 30000.0 |
| symbol_min_lot | 0.01 |
| typical_blocked_raw_lot | 0.0042 |
| typical_blocked_sl_distance | 35.915 |
| estimated_minimum_deposit_for_min_lot | 71428.57 |
| current_deposit_insufficient_for_min_lot | True |
| suggested_next_deposit_assumption_research_only | 100000 |

This diagnostic is not an instruction to force minimum lot or increase risk.
