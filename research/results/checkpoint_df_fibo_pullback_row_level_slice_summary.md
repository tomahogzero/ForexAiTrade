# Checkpoint DF Fibo Pullback Row-Level Slice Summary

Checkpoint DF reads existing `ea_mirror.log` artifacts only. It does not run MT5 or Strategy Tester and does not change trading behavior.

## Totals

| Metric | Value |
|---|---:|
| Diagnostic rows scanned | 621 |
| Fibo Pullback rows | 128 |
| Fibo usable first-touch rows | 85 |
| Fibo direction gap rows | 43 |
| Forbidden action markers | 0 |
| Baseline fallback markers | 0 |

## Fibo Direction Counts

| Field | Value | Count |
|---|---|---:|
| `fibo_candidate_direction_counts` | `SELL` | 53 |
| `fibo_candidate_direction_counts` | `DIRECTION_UNKNOWN` | 43 |
| `fibo_candidate_direction_counts` | `BUY` | 32 |
| `fibo_direction_source_counts` | `FIBO_PULLBACK_EMA` | 85 |
| `fibo_direction_source_counts` | `NONE` | 43 |
| `fibo_direction_confidence_counts` | `HIGH` | 85 |
| `fibo_direction_confidence_counts` | `NONE` | 43 |
| `fibo_first_touch_usable_counts` | `true` | 85 |
| `fibo_first_touch_usable_counts` | `false` | 43 |
| `fibo_direction_gap_reason_counts` | `NONE` | 85 |
| `fibo_direction_gap_reason_counts` | `PRICE_BETWEEN_EMAS` | 28 |
| `fibo_direction_gap_reason_counts` | `TREND_ALIGNMENT_CONFLICT` | 15 |

## Fibo Context Counts

| Field | Value | Count |
|---|---|---:|
| `fibo_ema_slope_state_counts` | `DOWN` | 68 |
| `fibo_ema_slope_state_counts` | `UP` | 32 |
| `fibo_ema_slope_state_counts` | `MIXED` | 28 |
| `fibo_price_vs_ema_state_counts` | `BELOW_BOTH` | 68 |
| `fibo_price_vs_ema_state_counts` | `ABOVE_BOTH` | 32 |
| `fibo_price_vs_ema_state_counts` | `BETWEEN` | 28 |
| `fibo_trend_alignment_state_counts` | `BEARISH` | 53 |
| `fibo_trend_alignment_state_counts` | `CONFLICT` | 43 |
| `fibo_trend_alignment_state_counts` | `BULLISH` | 32 |
| `fibo_pullback_side_counts` | `SELL_SIDE` | 53 |
| `fibo_pullback_side_counts` | `BUY_SIDE` | 32 |
| `fibo_pullback_side_counts` | `BOTH` | 28 |
| `fibo_pullback_side_counts` | `UNKNOWN` | 15 |
| `regime_counts` | `trend` | 92 |
| `regime_counts` | `breakout` | 36 |

## Window Distribution

| Window | Fibo rows | Usable rows |
|---|---:|---:|
| `cv_field_presence_20260301_20260308` | 25 | 15 |
| `cy_w1_20260308_20260315` | 20 | 15 |
| `cy_w2_20260315_20260322` | 20 | 20 |
| `cy_w3_20260322_20260329` | 4 | 2 |
| `db_w1_20260329_20260405` | 6 | 2 |
| `db_w2_20260405_20260412` | 19 | 10 |
| `db_w3_20260412_20260419` | 13 | 9 |
| `db_w4_20260419_20260426` | 21 | 12 |

## Verdicts

- `FIBO_ROW_LEVEL_SLICE_BUILT`
- `FIBO_USABLE_DIRECTION_BELOW_RULE_CANDIDATE_GATE`
- `RULE_CANDIDATE_GATE_FAIL`
- `ORDER_LOGIC_NOT_APPROVED`
- `PAF_NOT_READY_FOR_ORDER_LOGIC`

These rows are diagnostic observations only. They are not buy/sell signals and do not approve pending orders, market orders, optimization, or demo/live trading.
