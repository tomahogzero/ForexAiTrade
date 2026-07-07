# PAF Shadow Outcome Prototype Summary

RunId: `run_20260707_151857`

Checkpoint AT reads existing AQ no-trade diagnostics only. It does not run MT5, does not send orders, and does not optimize parameters.

## Case Summary

| Case | Diagnostics | Possible setups | NO_SETUP skipped | Readiness |
|---|---:|---:|---:|---|
| `GOLD_HASH_H1_PAF_DIAG_AQ_aq_w1_20260101_20260201` | 386 | 105 | 281 | `BLOCKED_BY_MISSING_DIRECTION` |
| `GOLD_HASH_H1_PAF_DIAG_AQ_aq_w2_20260201_20260301` | 267 | 66 | 201 | `BLOCKED_BY_MISSING_DIRECTION` |
| `GOLD_HASH_H1_PAF_DIAG_AQ_aq_w3_20260301_20260401` | 301 | 96 | 205 | `BLOCKED_BY_MISSING_DIRECTION` |

## Aggregate Counts

- Possible setup rows written: `267`
- Total diagnostic events seen: `954`
- Total NO_SETUP skipped: `687`

### Outcome Labels

| Value | Count |
|---|---:|
| `DIRECTION_MISSING` | 267 |

### Possible Setup Classifications

| Value | Count |
|---|---:|
| `POSSIBLE_FIBO_PULLBACK` | 145 |
| `POSSIBLE_ZONE_REJECTION` | 85 |
| `POSSIBLE_BREAK_RETEST` | 37 |

### Spread Buckets

| Value | Count |
|---|---:|
| `LOW_SPREAD` | 164 |
| `NORMAL_SPREAD` | 103 |

### Server-Time Session Buckets

| Value | Count |
|---|---:|
| `ASIA` | 86 |
| `LONDON` | 60 |
| `NEW_YORK` | 59 |
| `OVERLAP` | 39 |
| `OTHER` | 23 |

## Interpretation

- Current AQ diagnostics contain possible setup labels, but they do not include a direction field.
- Because direction is missing, the prototype correctly marks possible setups as `DIRECTION_MISSING` instead of guessing buy/sell context.
- No TP/SL, R-multiple, or profitability interpretation is possible from these artifacts.
- The next safe step is to add richer diagnostic logging or exported OHLC context in a later reviewed checkpoint before any order-path implementation.

## Guardrails

- No MT5 run was performed by this parser.
- No EA/source code was changed by this parser.
- No presets were changed by this parser.
- No market orders, pending orders, or position modifications were generated.
- This is not proof of profitability and not approval for demo/live trading.
