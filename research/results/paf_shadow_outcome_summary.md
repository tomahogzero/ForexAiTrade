# PAF Shadow Outcome Prototype Summary

RunId: `run_20260707_172236`

This summary reads existing no-trade diagnostic artifacts only. The parser itself does not run MT5, does not send orders, and does not optimize parameters.

## Case Summary

| Case | Diagnostics | Possible setups | NO_SETUP skipped | Readiness |
|---|---:|---:|---:|---|
| `GOLD_HASH_H1_PAF_FIELD_VERIFY_AX_ax_field_verify_20260301_20260308` | 97 | 33 | 64 | `BLOCKED_BY_MISSING_LOOKAHEAD_DATA` |

## Aggregate Counts

- Possible setup rows written: `33`
- Total diagnostic events seen: `97`
- Total NO_SETUP skipped: `64`

### Outcome Labels

| Value | Count |
|---|---:|
| `DATA_MISSING` | 19 |
| `DIRECTION_MISSING` | 14 |

### Possible Setup Classifications

| Value | Count |
|---|---:|
| `POSSIBLE_FIBO_PULLBACK` | 25 |
| `POSSIBLE_ZONE_REJECTION` | 6 |
| `POSSIBLE_BREAK_RETEST` | 2 |

### Spread Buckets

| Value | Count |
|---|---:|
| `NORMAL_SPREAD` | 32 |
| `LOW_SPREAD` | 1 |

### Server-Time Session Buckets

| Value | Count |
|---|---:|
| `LONDON` | 11 |
| `ASIA` | 7 |
| `NEW_YORK` | 6 |
| `OTHER` | 5 |
| `OVERLAP` | 4 |

## Interpretation

- Diagnostic artifacts may contain possible setup labels, direction context, and entry reference data depending on the selected run.
- If direction is missing or unknown, the prototype marks possible setups as `DIRECTION_MISSING` instead of guessing buy/sell context.
- If direction exists but OHLC/tick lookahead data is unavailable, the prototype marks rows as `DATA_MISSING`.
- No TP/SL, R-multiple, or profitability interpretation is possible from these artifacts.
- The next safe step is to add richer diagnostic logging or exported OHLC context in a later reviewed checkpoint before any order-path implementation.

## Guardrails

- No MT5 run was performed by this parser.
- No EA/source code was changed by this parser.
- No presets were changed by this parser.
- No market orders, pending orders, or position modifications were generated.
- This is not proof of profitability and not approval for demo/live trading.
