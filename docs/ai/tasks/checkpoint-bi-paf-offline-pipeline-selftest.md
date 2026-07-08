# Checkpoint BI: PAF Offline Pipeline Self-Test

Date: 2026-07-08

## Scope

Run an offline synthetic end-to-end self-test:

raw MT5-style bars CSV -> schema normalizer -> bars validator -> lookahead joiner

No MT5 run.
No Strategy Tester run.
No EA/source changes.
No preset changes.
No real market data processed.
No optimization.
No lot/risk increase.
No profitability claim.

## Commands

```powershell
python -m py_compile tools\paf_bars_schema_normalizer.py tools\paf_lookahead_bars_validator.py tools\paf_lookahead_joiner.py

python tools\paf_bars_schema_normalizer.py `
  --raw-csv research\selftests\checkpoint_bi\paf_lookahead_bars_raw_mt5_style.csv `
  --output-csv research\selftests\checkpoint_bi\output\paf_lookahead_bars.csv `
  --results-root research\selftests\checkpoint_bi\output `
  --source-symbol GOLD# `
  --source-timeframe H1

python tools\paf_lookahead_bars_validator.py `
  --bars-csv research\selftests\checkpoint_bi\output\paf_lookahead_bars.csv `
  --shadow-outcomes research\selftests\checkpoint_bi\paf_shadow_outcomes_fixture.csv `
  --results-root research\selftests\checkpoint_bi\output `
  --symbol GOLD# `
  --timeframe H1 `
  --horizon-bars 1

python tools\paf_lookahead_joiner.py `
  --shadow-outcomes research\selftests\checkpoint_bi\paf_shadow_outcomes_fixture.csv `
  --bars-csv research\selftests\checkpoint_bi\output\paf_lookahead_bars.csv `
  --results-root research\selftests\checkpoint_bi\output `
  --horizons 1,2 `
  --tp-atr-multiple 1.5 `
  --sl-atr-multiple 1.0
```

## Results

- syntax check: `PASS`
- normalization verdict: `PASS`
- validation verdict: `PASS`
- join status `JOINED`: `2`
- horizon 1 outcomes: `TP_FIRST=1`, `SL_FIRST=1`
- horizon 2 outcomes: `TP_FIRST=1`, `SL_FIRST=1`

## Decision

- `OFFLINE_PIPELINE_SELFTEST_PASS`
- `NORMALIZER_VALIDATOR_JOINER_CHAIN_PASS_ON_SYNTHETIC_FIXTURE`
- `REAL_MARKET_LOOKAHEAD_CSV_STILL_MISSING`
- `JOINER_NOT_RUN_ON_REAL_DATA`
- `MT5_NOT_RUN`
- `ORDER_PATH_STILL_BLOCKED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`
