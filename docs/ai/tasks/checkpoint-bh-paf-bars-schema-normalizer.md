# Checkpoint BH: PAF Bars Schema Normalizer

Date: 2026-07-08

## Scope

Add an offline-only schema normalizer for PAF lookahead OHLC bar CSV files.

No MT5 run.
No Strategy Tester run.
No EA/source changes.
No preset changes.
No optimization.
No lot/risk increase.
No profitability claim.

## Tool

`tools/paf_bars_schema_normalizer.py`

The tool converts raw CSV files into:

`time,open,high,low,close`

It supports MT5-style exports such as:

- `<DATE>`
- `<TIME>`
- `<OPEN>`
- `<HIGH>`
- `<LOW>`
- `<CLOSE>`

## Safety Rules

The tool may:

- detect delimiter
- combine date and time
- rename columns
- drop extra non-OHLC columns
- preserve a raw copy
- write normalization summary files

The tool must not:

- change OHLC prices
- fill missing bars
- shift timezone without evidence
- resample another timeframe
- run MT5
- run Strategy Tester
- send orders
- optimize
- claim profitability

## Self-Test

Synthetic fixture:

- `research/selftests/checkpoint_bh/paf_lookahead_bars_raw_mt5_style.csv`
- `research/selftests/checkpoint_bh/paf_shadow_outcomes_fixture.csv`

Commands run:

```powershell
python -m py_compile tools\paf_bars_schema_normalizer.py tools\paf_lookahead_bars_validator.py

python tools\paf_bars_schema_normalizer.py `
  --raw-csv research\selftests\checkpoint_bh\paf_lookahead_bars_raw_mt5_style.csv `
  --output-csv research\selftests\checkpoint_bh\output\paf_lookahead_bars.csv `
  --results-root research\selftests\checkpoint_bh\output `
  --source-symbol GOLD# `
  --source-timeframe H1

python tools\paf_lookahead_bars_validator.py `
  --bars-csv research\selftests\checkpoint_bh\output\paf_lookahead_bars.csv `
  --shadow-outcomes research\selftests\checkpoint_bh\paf_shadow_outcomes_fixture.csv `
  --results-root research\selftests\checkpoint_bh\output `
  --symbol GOLD# `
  --timeframe H1 `
  --horizon-bars 1
```

Results:

- Python syntax check: `PASS`
- normalization verdict: `PASS`
- validator verdict on normalized synthetic fixture: `PASS`

## Decision

- `SCHEMA_NORMALIZER_TOOL_ADDED`
- `SCHEMA_NORMALIZER_SELFTEST_PASS`
- `NORMALIZED_OUTPUT_VALIDATOR_PASS_ON_SYNTHETIC_FIXTURE`
- `REAL_MARKET_LOOKAHEAD_CSV_STILL_MISSING`
- `JOINER_NOT_RUN_ON_REAL_DATA`
- `MT5_NOT_RUN`
- `ORDER_PATH_STILL_BLOCKED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`
