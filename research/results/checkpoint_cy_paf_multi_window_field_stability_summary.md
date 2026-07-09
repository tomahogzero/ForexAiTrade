# Checkpoint CY PAF Multi-Window Field Stability Summary

RunId: `run_20260709_202415`

## Verdict

- `FIELD_PRESENCE_CONFIRMED_ALL_WINDOWS`
- `NO_TRADE_CONFIRMED_ALL_WINDOWS`
- `DIRECTION_GAP_STABILITY_INCONCLUSIVE_LOW_SAMPLE`
- `PAF_NOT_READY_FOR_ORDER_LOGIC`

## Execution Summary

| Window | Period | Execution | Report | Trades | Diagnostics | Forbidden markers | Baseline fallback markers |
|---|---|---|---|---:|---:|---:|---:|
| W1 | `2026-03-08` to `2026-03-15` | `PASS` | `FOUND` | 0 | 74 | 0 | 0 |
| W2 | `2026-03-15` to `2026-03-22` | `PASS` | `FOUND` | 0 | 72 | 0 | 0 |
| W3 | `2026-03-22` to `2026-03-29` | `PASS` | `FOUND` | 0 | 31 | 0 | 0 |

## Direction Gap Buckets

| Window | NO_SETUP_DIRECTION_NOT_REQUIRED | USABLE_DIRECTION | TREND_ALIGNMENT_CONFLICT | WICK_TOO_SMALL | PRICE_BETWEEN_EMAS |
|---|---:|---:|---:|---:|---:|
| W1 | 46 | 18 | 3 | 5 | 2 |
| W2 | 47 | 23 | 0 | 2 | 0 |
| W3 | 26 | 3 | 0 | 0 | 2 |

## Interpretation

CT field presence is confirmed across all three windows. No trade or fallback behavior was observed.

Direction-gap stability is inconclusive because W3 has only `31` diagnostics and only `3` usable direction rows. This is not enough to approve order logic.

This is diagnostic evidence only and is not profitability proof.
