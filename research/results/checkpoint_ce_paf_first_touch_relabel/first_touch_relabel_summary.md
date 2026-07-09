# Checkpoint CE: PAF Offline First-Touch Relabel Summary

This is an offline diagnostic artifact. It does not run MT5, does not send orders, does not optimize parameters, and does not prove profitability.

## Verdict

- Status: `PASS_OFFLINE_FIRST_TOUCH_RELABEL`
- Required ATR column: `offline_atr_14`
- TP ATR multiple: `1.5`
- SL ATR multiple: `1.0`
- Horizons: `6,12,24,48`

## Counts

- Rows read: `33`
- Relabel-ready rows: `17`
- Data-missing rows: `2`
- Direction-missing rows: `14`

## Outcome Labels By Horizon

### Horizon 6

| Label | Count |
|---|---:|
| `AMBIGUOUS_SAME_BAR` | 1 |
| `DATA_MISSING` | 2 |
| `DIRECTION_MISSING` | 14 |
| `NO_RESOLUTION` | 2 |
| `SL_FIRST` | 9 |
| `TP_FIRST` | 5 |

### Horizon 12

| Label | Count |
|---|---:|
| `AMBIGUOUS_SAME_BAR` | 1 |
| `DATA_MISSING` | 2 |
| `DIRECTION_MISSING` | 14 |
| `SL_FIRST` | 10 |
| `TP_FIRST` | 6 |

### Horizon 24

| Label | Count |
|---|---:|
| `AMBIGUOUS_SAME_BAR` | 1 |
| `DATA_MISSING` | 2 |
| `DIRECTION_MISSING` | 14 |
| `SL_FIRST` | 10 |
| `TP_FIRST` | 6 |

### Horizon 48

| Label | Count |
|---|---:|
| `AMBIGUOUS_SAME_BAR` | 1 |
| `DATA_MISSING` | 2 |
| `DIRECTION_MISSING` | 14 |
| `SL_FIRST` | 10 |
| `TP_FIRST` | 6 |

## Guardrails

- offline files only
- no MT5 run
- no Strategy Tester run
- no EA/source changes
- no preset changes
- no orders
- no optimization
- no profitability claim

## Limitations

- Labels are hypothetical shadow diagnostics, not real orders.
- OHLC bars cannot prove tick order inside the same bar.
- `AMBIGUOUS_SAME_BAR` is used when TP and SL touch in the same bar.
- This summary is not a profitability assessment.
