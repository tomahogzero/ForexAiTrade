# Checkpoint CZ PAF Data Sufficiency Summary

## Verdict

- `NO_TRADE_DIAGNOSTIC_PIPELINE_CONFIRMED`
- `DATA_SUFFICIENCY_FAIL_LOW_USABLE_DIRECTION`
- `PAF_NOT_READY_FOR_ORDER_LOGIC`

## Inputs

| Checkpoint | RunId | Window |
|---|---|---|
| CV | `run_20260709_182444` | `2026-03-01` to `2026-03-08` |
| CY-W1 | `run_20260709_202415` | `2026-03-08` to `2026-03-15` |
| CY-W2 | `run_20260709_202415` | `2026-03-15` to `2026-03-22` |
| CY-W3 | `run_20260709_202415` | `2026-03-22` to `2026-03-29` |

## Combined Counts

| Metric | Count |
|---|---:|
| Total diagnostic rows | 274 |
| NO_SETUP_DIRECTION_NOT_REQUIRED | 183 |
| Possible setup rows | 91 |
| USABLE_DIRECTION | 63 |
| TREND_ALIGNMENT_CONFLICT | 12 |
| WICK_TOO_SMALL | 11 |
| PRICE_BETWEEN_EMAS | 5 |

## Gate Decision

| Gate | Required | Actual | Result |
|---|---:|---:|---|
| Diagnostic interpretation | 100 usable rows | 63 | FAIL |
| Rule-candidate discussion | 300 usable rows | 63 | FAIL |

## Recommendation

Proceed only to a future data collection expansion approval checkpoint. Do not implement order logic.
