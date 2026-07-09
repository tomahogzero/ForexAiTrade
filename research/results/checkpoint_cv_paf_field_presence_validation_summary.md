# Checkpoint CV PAF Field Presence Validation Summary

RunId: `run_20260709_182444`

## Scope

- Symbol: `GOLD#`
- Timeframe: `H1`
- Date range: `2026-03-01` to `2026-03-08`
- Strategy Tester only
- One run only
- No optimization
- No market orders
- No pending orders
- No position modification
- No lot/risk increase
- No profitability interpretation

## Execution

| Metric | Value |
|---|---|
| Compile result | `0 errors, 0 warnings` |
| Execution status | `PASS` |
| Report artifact status | `FOUND` |
| Total trades | `0` |
| PAF diagnostics status | `FOUND` |
| PAF diagnostic count | `97` |
| Authoritative source | `ea_mirror.log` |
| No-trade confirmation | `PASS_FROM_REPORT_AND_EA_LOGS` |
| Baseline fallback confirmation | `PASS_FROM_EA_LOGS` |
| Forbidden action marker count | `0` |
| Baseline fallback marker count | `0` |

## Classification Counts

| Classification | Count |
|---|---:|
| `NO_SETUP` | 64 |
| `POSSIBLE_FIBO_PULLBACK` | 25 |
| `POSSIBLE_ZONE_REJECTION` | 6 |
| `POSSIBLE_BREAK_RETEST` | 2 |

## Direction Gap Counts

| Direction Gap | Count |
|---|---:|
| `NO_SETUP_DIRECTION_NOT_REQUIRED` | 64 |
| `USABLE_DIRECTION` | 19 |
| `TREND_ALIGNMENT_CONFLICT` | 9 |
| `WICK_TOO_SMALL` | 4 |
| `PRICE_BETWEEN_EMAS` | 1 |

## Field Presence

All required Checkpoint CT diagnostics-only fields were found in `ea_mirror.log`, including Fibo EMA context, trend-alignment context, pullback-side context, zone-touch context, rejection-candle context, and direction-gap reasons.

Parser output also included:

- `paf_direction_gap_bucket_counts`
- `paf_fibo_direction_gap_reason_counts`
- `paf_zone_direction_gap_reason_counts`

## Interpretation Boundary

This summary is diagnostic-only. It does not prove profitability, does not approve order logic, does not approve demo/live trading, and does not justify lot/risk increases.
