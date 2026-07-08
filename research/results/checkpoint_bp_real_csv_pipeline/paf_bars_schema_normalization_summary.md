# PAF Bars Schema Normalization Summary

This is an offline schema-normalization summary. It does not run MT5, does not send orders, and does not prove profitability.

## Verdict

`PASS`

## Inputs

- Raw CSV: `G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\manual_exports\GOLD_HASH_H1_20260301_20260310_raw_mt5_H1.csv`
- Normalized CSV: `research\results\checkpoint_bp_real_csv_pipeline\paf_lookahead_bars.csv`
- Raw preserved copy: `research\results\checkpoint_bp_real_csv_pipeline\paf_lookahead_bars_raw.csv`
- Source symbol: `GOLD#`
- Source timeframe: `H1`
- Broker comparable: `True`

## Columns

- Input columns: `<DATE>, <TIME>, <OPEN>, <HIGH>, <LOW>, <CLOSE>, <TICKVOL>, <VOL>, <SPREAD>`
- Output columns: `time, open, high, low, close`
- Delimiter detected: `	`
- Column mapping: `{"time": null, "date": "<DATE>", "time_only": "<TIME>", "open": "<OPEN>", "high": "<HIGH>", "low": "<LOW>", "close": "<CLOSE>"}`

## Rows

- Rows before: `139`
- Rows after: `139`
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
