# PAF Lookahead Join Summary

This is an offline diagnostic summary. It does not run MT5, does not send orders, and does not prove profitability.

## Inputs

- Shadow outcomes CSV: `research\selftests\checkpoint_bi\paf_shadow_outcomes_fixture.csv`
- Bars CSV: `research\selftests\checkpoint_bi\output\paf_lookahead_bars.csv`
- TP ATR multiple: `1.5`
- SL ATR multiple: `1.0`
- Horizons: `1,2`

## Join Status

| Status | Count |
|---|---:|
| `JOINED` | 2 |

## Outcome Labels By Horizon

### Horizon 1 Bars

| Outcome | Count |
|---|---:|
| `SL_FIRST` | 1 |
| `TP_FIRST` | 1 |

### Horizon 2 Bars

| Outcome | Count |
|---|---:|
| `SL_FIRST` | 1 |
| `TP_FIRST` | 1 |

## Guardrails

- Lookahead data is used only after diagnostic events have been logged.
- The output is for offline research only.
- No market orders, pending orders, or position modifications are generated.
- This is not an optimization result and not a profitability claim.

## Limitations

- Bar OHLC cannot prove tick order inside a bar.
- Same-bar TP/SL ambiguity is labeled conservatively as `AMBIGUOUS_SAME_BAR`.
- Missing timestamps or missing ATR keep rows in `DATA_MISSING` rather than guessing.
