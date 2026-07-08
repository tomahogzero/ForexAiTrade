# Checkpoint BJ: PAF Offline Pipeline Runner

Date: 2026-07-08

## Scope

Add an offline-only pipeline runner:

raw bars CSV or normalized bars CSV -> normalize if needed -> validate -> join

No MT5 run.
No Strategy Tester run.
No EA/source changes.
No preset changes.
No real market data processed.
No optimization.
No lot/risk increase.
No profitability claim.

## Tool

`tools/paf_offline_pipeline_runner.py`

The runner uses existing tools:

- `tools/paf_bars_schema_normalizer.py`
- `tools/paf_lookahead_bars_validator.py`
- `tools/paf_lookahead_joiner.py`

## Stop Gate

- If normalization fails, stop.
- If validation fails, stop and do not run joiner.
- If joiner fails, report failure.

## Self-Test

Synthetic fixture only:

```powershell
python -m py_compile tools\paf_offline_pipeline_runner.py tools\paf_bars_schema_normalizer.py tools\paf_lookahead_bars_validator.py tools\paf_lookahead_joiner.py

python tools\paf_offline_pipeline_runner.py `
  --raw-csv research\selftests\checkpoint_bi\paf_lookahead_bars_raw_mt5_style.csv `
  --shadow-outcomes research\selftests\checkpoint_bi\paf_shadow_outcomes_fixture.csv `
  --results-root research\selftests\checkpoint_bj\output `
  --symbol GOLD# `
  --timeframe H1 `
  --horizon-bars 1 `
  --join-horizons 1,2 `
  --tp-atr-multiple 1.5 `
  --sl-atr-multiple 1.0
```

Results:

- syntax check: `PASS`
- runner verdict: `PASS`
- normalize stage: `PASS`
- validate stage: `PASS`
- join stage: `PASS`
- join status `JOINED`: `2`

## Decision

- `OFFLINE_PIPELINE_RUNNER_ADDED`
- `OFFLINE_PIPELINE_RUNNER_SELFTEST_PASS`
- `NORMALIZE_VALIDATE_JOIN_CHAIN_PASS_ON_SYNTHETIC_FIXTURE`
- `REAL_MARKET_LOOKAHEAD_CSV_STILL_MISSING`
- `JOINER_NOT_RUN_ON_REAL_DATA`
- `MT5_NOT_RUN`
- `ORDER_PATH_STILL_BLOCKED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`
