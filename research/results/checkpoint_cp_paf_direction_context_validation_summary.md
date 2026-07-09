# Checkpoint CP PAF Direction Context Validation Summary

RunId: `run_20260709_155948`

Case: `GOLD_HASH_H1_PAF_DIRECTION_CONTEXT_CP_cp_direction_validate_20260301_20260308`

## Result

| Item | Value |
|---|---|
| Execution status | `PASS` |
| Report artifact status | `FOUND` |
| Symbol | `GOLD#` |
| Timeframe | `H1` |
| Date range | `2026-03-01` to `2026-03-08` |
| Total trades | `0` |
| PAF diagnostics | `97` |
| No-trade lines | `115` |
| Forbidden action markers | `0` |
| Baseline fallback markers | `0` |
| No-trade confirmation | `PASS_FROM_REPORT_AND_EA_LOGS` |
| Baseline fallback confirmation | `PASS_FROM_EA_LOGS` |

## CN Field Presence

All 20 Checkpoint CN `paf_*` fields appeared on all `97` diagnostic lines.

## Direction Counts

| Direction | Count |
|---|---:|
| `DIRECTION_UNKNOWN` | 78 |
| `SELL` | 10 |
| `BUY` | 9 |

## Direction Source Counts

| Source | Count |
|---|---:|
| `NONE` | 78 |
| `FIBO_PULLBACK_EMA` | 15 |
| `BREAK_RETEST` | 2 |
| `ZONE_REJECTION` | 2 |

## Decision

`CN_FIELD_LOGGING_CONFIRMED`

`ORDER_PATH_STILL_BLOCKED`

This summary is diagnostic-only and is not a profitability claim.
