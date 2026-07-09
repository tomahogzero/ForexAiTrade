# PAF Lookahead Join Summary

This is an offline diagnostic summary. It does not run MT5, does not send orders, and does not prove profitability.

## Inputs

- Shadow outcomes CSV: `research\results\paf_shadow_outcomes_all_cases.csv`
- Bars CSV: `research\results\checkpoint_bz_offline_joiner_run\paf_lookahead_bars.csv`
- TP ATR multiple: `1.5`
- SL ATR multiple: `1.0`
- Horizons: `6,12,24,48`

## Join Status

| Status | Count |
|---|---:|
| `JOINED` | 19 |
| `DIRECTION_MISSING` | 14 |

## Outcome Labels By Horizon

### Horizon 6 Bars

| Outcome | Count |
|---|---:|
| `DATA_MISSING` | 19 |

### Horizon 12 Bars

| Outcome | Count |
|---|---:|
| `DATA_MISSING` | 19 |

### Horizon 24 Bars

| Outcome | Count |
|---|---:|
| `DATA_MISSING` | 19 |

### Horizon 48 Bars

| Outcome | Count |
|---|---:|
| `DATA_MISSING` | 19 |

## Guardrails

- Lookahead data is used only after diagnostic events have been logged.
- The output is for offline research only.
- No market orders, pending orders, or position modifications are generated.
- This is not an optimization result and not a profitability claim.

## Limitations

- Bar OHLC cannot prove tick order inside a bar.
- Same-bar TP/SL ambiguity is labeled conservatively as `AMBIGUOUS_SAME_BAR`.
- Missing timestamps or missing ATR keep rows in `DATA_MISSING` rather than guessing.
