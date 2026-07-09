# Checkpoint CY Experiment: Multi-Window PAF Field Stability

Date: 2026-07-09

## Approval

User approved:

`Approved to execute Checkpoint CY multi-window CT field-presence diagnostic with symbol GOLD# timeframe H1 windows 2026-03-08 to 2026-03-15, 2026-03-15 to 2026-03-22, and 2026-03-22 to 2026-03-29 using official AK runner/parser workflow.`

## Run

- RunId: `run_20260709_202415`
- Symbol: `GOLD#`
- Timeframe: `H1`
- Strategy Tester only
- No optimization
- No market orders
- No pending orders
- No position modification
- No lot/risk increase
- No profitability interpretation

## Result

All three windows completed with parseable reports and PAF diagnostics.

| Window | Period | Status | Trades | Diagnostics | Field presence | Forbidden markers | Fallback markers |
|---|---|---|---:|---:|---|---:|---:|
| W1 | `2026-03-08` to `2026-03-15` | `PASS` | 0 | 74 | `PASS` | 0 | 0 |
| W2 | `2026-03-15` to `2026-03-22` | `PASS` | 0 | 72 | `PASS` | 0 | 0 |
| W3 | `2026-03-22` to `2026-03-29` | `PASS` | 0 | 31 | `PASS` | 0 | 0 |

## Verdict

- `FIELD_PRESENCE_CONFIRMED_ALL_WINDOWS`
- `NO_TRADE_CONFIRMED_ALL_WINDOWS`
- `DIRECTION_GAP_STABILITY_INCONCLUSIVE_LOW_SAMPLE`
- `PAF_NOT_READY_FOR_ORDER_LOGIC`

## Notes

Window 3 is thin: only `31` diagnostics and `3` usable direction rows. This prevents a strong stability conclusion.
