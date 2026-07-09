# Checkpoint CG: PAF First-Touch Attribution Summary

This is an offline diagnostic summary. It does not run MT5, does not send orders, does not optimize parameters, and does not prove profitability.

## Verdict

- Status: `PASS_OFFLINE_FIRST_TOUCH_ATTRIBUTION`
- Rows read: `33`
- Relabel-ready rows: `17`
- Direction-missing rows: `14`
- Data-missing rows: `2`

## Overall Label Counts

### Horizon 6

| Label | Count |
|---|---:|
| `TP_FIRST` | 5 |
| `SL_FIRST` | 9 |
| `NO_RESOLUTION` | 2 |
| `AMBIGUOUS_SAME_BAR` | 1 |
| `DATA_MISSING` | 2 |
| `DIRECTION_MISSING` | 14 |

### Horizon 12

| Label | Count |
|---|---:|
| `TP_FIRST` | 6 |
| `SL_FIRST` | 10 |
| `NO_RESOLUTION` | 0 |
| `AMBIGUOUS_SAME_BAR` | 1 |
| `DATA_MISSING` | 2 |
| `DIRECTION_MISSING` | 14 |

### Horizon 24

| Label | Count |
|---|---:|
| `TP_FIRST` | 6 |
| `SL_FIRST` | 10 |
| `NO_RESOLUTION` | 0 |
| `AMBIGUOUS_SAME_BAR` | 1 |
| `DATA_MISSING` | 2 |
| `DIRECTION_MISSING` | 14 |

### Horizon 48

| Label | Count |
|---|---:|
| `TP_FIRST` | 6 |
| `SL_FIRST` | 10 |
| `NO_RESOLUTION` | 0 |
| `AMBIGUOUS_SAME_BAR` | 1 |
| `DATA_MISSING` | 2 |
| `DIRECTION_MISSING` | 14 |

## Top SL-FIRST Diagnostic Concentrations

| Horizon | Dimension | Value | Rows | Ready | TP_FIRST | SL_FIRST | Bias |
|---:|---|---|---:|---:|---:|---:|---|
| 6 | `classification` | `POSSIBLE_FIBO_PULLBACK` | 25 | 15 | 4 | 9 | `SL_FIRST_DOMINANT` |
| 12 | `classification` | `POSSIBLE_FIBO_PULLBACK` | 25 | 15 | 5 | 10 | `SL_FIRST_DOMINANT` |
| 24 | `classification` | `POSSIBLE_FIBO_PULLBACK` | 25 | 15 | 5 | 10 | `SL_FIRST_DOMINANT` |
| 48 | `classification` | `POSSIBLE_FIBO_PULLBACK` | 25 | 15 | 5 | 10 | `SL_FIRST_DOMINANT` |
| 6 | `spread_bucket` | `NORMAL_SPREAD` | 32 | 17 | 5 | 9 | `SL_FIRST_DOMINANT` |
| 6 | `regime` | `trend` | 30 | 17 | 5 | 9 | `SL_FIRST_DOMINANT` |
| 12 | `spread_bucket` | `NORMAL_SPREAD` | 32 | 17 | 6 | 10 | `SL_FIRST_DOMINANT` |
| 12 | `regime` | `trend` | 30 | 17 | 6 | 10 | `SL_FIRST_DOMINANT` |
| 24 | `spread_bucket` | `NORMAL_SPREAD` | 32 | 17 | 6 | 10 | `SL_FIRST_DOMINANT` |
| 24 | `regime` | `trend` | 30 | 17 | 6 | 10 | `SL_FIRST_DOMINANT` |
| 48 | `spread_bucket` | `NORMAL_SPREAD` | 32 | 17 | 6 | 10 | `SL_FIRST_DOMINANT` |
| 48 | `regime` | `trend` | 30 | 17 | 6 | 10 | `SL_FIRST_DOMINANT` |

## Interpretation Guardrails

- These are shadow diagnostic labels, not real trades.
- SL_FIRST dominance is a research warning, not proof of loss.
- No parameter or order logic may be changed from this checkpoint.
- Small sample size and direction missing remain major blockers.
