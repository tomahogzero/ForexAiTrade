# PAF Bars Schema Normalization Summary

This is an offline schema-normalization summary. It does not run MT5, does not send orders, and does not prove profitability.

## Verdict

`PASS`

## Inputs

- Raw CSV: `research\selftests\checkpoint_bh\paf_lookahead_bars_raw_mt5_style.csv`
- Normalized CSV: `research\selftests\checkpoint_bh\output\paf_lookahead_bars.csv`
- Raw preserved copy: `research\selftests\checkpoint_bh\output\paf_lookahead_bars_raw.csv`
- Source symbol: `GOLD#`
- Source timeframe: `H1`
- Broker comparable: `True`

## Columns

- Input columns: `<DATE>, <TIME>, <OPEN>, <HIGH>, <LOW>, <CLOSE>, <TICKVOL>, <VOL>, <SPREAD>`
- Output columns: `time, open, high, low, close`
- Delimiter detected: `	`
- Column mapping: `{"time": null, "date": "<DATE>", "time_only": "<TIME>", "open": "<OPEN>", "high": "<HIGH>", "low": "<LOW>", "close": "<CLOSE>"}`

## Rows

- Rows before: `4`
- Rows after: `4`
- Invalid rows: `0`

## Issues

- None

## Guardrails

- Offline normalization only.
- No MT5 run.
- No Strategy Tester run.
- No market orders or pending orders.
- No OHLC price editing.
- No missing-bar filling.
- No optimization.
- No profitability claim.
