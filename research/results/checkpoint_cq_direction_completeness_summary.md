# Checkpoint CQ Direction Completeness Analysis

RunId: `run_20260709_155948`

## Summary

| Metric | Count |
|---|---:|
| `USABLE_DIRECTION` | 19 |
| `NO_SETUP_DIRECTION_NOT_REQUIRED` | 64 |
| `FIBO_PULLBACK_EMA_DIRECTION_CONTEXT_MISSING` | 10 |
| `ZONE_REJECTION_CANDLE_DIRECTION_CONTEXT_MISSING` | 4 |

## Candidate Direction

| Direction | Count |
|---|---:|
| `BUY` | 9 |
| `DIRECTION_UNKNOWN` | 78 |
| `SELL` | 10 |

## Bucket By Classification

| Classification | Bucket | Count |
|---|---|---:|
| `NO_SETUP` | `NO_SETUP_DIRECTION_NOT_REQUIRED` | 64 |
| `POSSIBLE_BREAK_RETEST` | `USABLE_DIRECTION` | 2 |
| `POSSIBLE_FIBO_PULLBACK` | `USABLE_DIRECTION` | 15 |
| `POSSIBLE_FIBO_PULLBACK` | `FIBO_PULLBACK_EMA_DIRECTION_CONTEXT_MISSING` | 10 |
| `POSSIBLE_ZONE_REJECTION` | `ZONE_REJECTION_CANDLE_DIRECTION_CONTEXT_MISSING` | 4 |
| `POSSIBLE_ZONE_REJECTION` | `USABLE_DIRECTION` | 2 |

## Interpretation

`DIRECTION_UNKNOWN` is mostly expected on `NO_SETUP` rows. The true unresolved direction-completeness issue is the 14 possible-setup rows with missing usable direction context.

This is diagnostic-only. It is not profitability proof and does not approve order logic.
