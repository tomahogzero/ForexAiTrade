# PAF Offline Pipeline Runner Summary

This is an offline research pipeline summary. It does not run MT5, does not send orders, and does not prove profitability.

## Verdict

`PASS`

## Inputs

- Raw CSV: `research\selftests\checkpoint_bi\paf_lookahead_bars_raw_mt5_style.csv`
- Bars CSV: `research\selftests\checkpoint_bj\output\paf_lookahead_bars.csv`
- Shadow outcomes: `research\selftests\checkpoint_bi\paf_shadow_outcomes_fixture.csv`
- Results root: `research\selftests\checkpoint_bj\output`
- Symbol: `GOLD#`
- Timeframe: `H1`
- Horizon bars: `1`
- Join horizons: `1,2`

## Stage Results

| Stage | Status | Return Code |
|---|---|---:|
| `normalize` | `PASS` | 0 |
| `validate` | `PASS` | 0 |
| `join` | `PASS` | 0 |

## Stop Reason

``

## Guardrails

- Offline pipeline only.
- No MT5 run.
- No Strategy Tester run.
- No market orders or pending orders.
- No position modification.
- No optimization.
- No lot/risk increase.
- No profitability claim.
