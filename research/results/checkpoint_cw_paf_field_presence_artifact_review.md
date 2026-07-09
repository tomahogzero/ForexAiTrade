# Checkpoint CW PAF Field Presence Artifact Review

Reviewed RunId: `run_20260709_182444`

## Verdict

`FIELD_PRESENCE_CONFIRMED`

`PAF_NOT_READY_FOR_ORDER_LOGIC`

## Evidence

| Metric | Value |
|---|---|
| Execution status | `PASS` |
| Report artifact status | `FOUND` |
| Total trades | `0` |
| PAF diagnostics | `97` |
| No-trade confirmation | `PASS_FROM_REPORT_AND_EA_LOGS` |
| Baseline fallback confirmation | `PASS_FROM_EA_LOGS` |
| Forbidden action markers | `0` |
| Baseline fallback markers | `0` |

## Direction Gap Interpretation

| Bucket | Count | Review interpretation |
|---|---:|---|
| `NO_SETUP_DIRECTION_NOT_REQUIRED` | 64 | Exclude from failure count |
| `USABLE_DIRECTION` | 19 | Usable diagnostic direction |
| `TREND_ALIGNMENT_CONFLICT` | 9 | Explainable Fibo condition conflict |
| `WICK_TOO_SMALL` | 4 | Explainable zone rejection weakness |
| `PRICE_BETWEEN_EMAS` | 1 | Explainable ambiguous EMA context |

## Main Finding

Checkpoint CV changed the direction issue from unknown/missing-field evidence into explainable condition buckets. This is progress for diagnostics, not a trading signal.

## Remaining Blocker

The dataset is still too small and too narrow:

- 1 short window only
- 97 diagnostic rows
- 19 usable direction rows
- No multi-window stability check after CT fields

## Next Safe Step

Prepare Checkpoint CX approval package for multi-window CT field-presence and direction-gap stability validation. Do not add order logic.
