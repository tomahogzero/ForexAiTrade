# Checkpoint AX PAF Field Verification Summary

RunId: `run_20260707_172236`

Case: `GOLD_HASH_H1_PAF_FIELD_VERIFY_AX_ax_field_verify_20260301_20260308`

Symbol/timeframe: `GOLD#` `H1`

Date range: `2026-03-01` to `2026-03-08`

## Execution

| Item | Result |
|---|---|
| Execution status | `PASS` |
| Report artifact | `FOUND` |
| Metadata match | `true` |
| Total trades | `0` |
| PAF diagnostic source | `ea_mirror.log` |
| PAF diagnostics | `97` |
| Forbidden action markers | `0` |
| Baseline fallback markers | `0` |

## Diagnostic Field Counts

| Field | Count |
|---|---:|
| `direction_context` | 97 |
| `direction_reason` | 97 |
| `entry_reference_price` | 97 |
| `bar_open` | 97 |
| `bar_high` | 97 |
| `bar_low` | 97 |
| `bar_close` | 97 |
| `atr` | 97 |
| `ema_fast` | 97 |
| `ema_slow` | 97 |
| `bb_width_percent` | 97 |

## Direction Context

| Direction context | Count |
|---|---:|
| `BUY_CONTEXT` | 9 |
| `SELL_CONTEXT` | 10 |
| `DIRECTION_UNKNOWN` | 78 |

## Shadow Outcome Parser

| Outcome label | Count |
|---|---:|
| `DATA_MISSING` | 19 |
| `DIRECTION_MISSING` | 14 |

Readiness: `BLOCKED_BY_MISSING_LOOKAHEAD_DATA`

## Interpretation

Checkpoint AX proves the added diagnostic fields are emitted in Strategy Tester no-trade diagnostics. It does not prove profitability and does not approve market orders, pending orders, position modification, optimization, lot/risk increase, or demo/live testing.

The next safe step is to add or export OHLC/tick lookahead context for future shadow-outcome labeling.
