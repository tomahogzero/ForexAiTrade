# Checkpoint BK: PAF Real CSV Offline Run Approval Package

Date: 2026-07-08

## Scope

Documentation and approval package only.

Checkpoint BK does not run MT5, does not run Strategy Tester, does not run the offline pipeline on real data, does not change EA/source code, does not change presets, does not optimize, does not increase lot/risk, and does not claim profitability.

## Context

Checkpoint BJ added `tools/paf_offline_pipeline_runner.py` and verified the offline chain on synthetic fixtures:

raw MT5-style bars CSV -> normalize -> validate -> join

The next safe step is not strategy implementation. The next safe step is to define the exact approval conditions for running the offline pipeline on a real `GOLD#` H1 bars CSV when the user provides an absolute file path.

## Target Diagnostic Context

- RunId: `run_20260707_172236`
- Symbol: `GOLD#`
- Timeframe: `H1`
- Diagnostic window: `2026-03-01` to `2026-03-08`
- Required lookahead coverage: at least through `2026-03-10 23:59:59`
- Shadow outcome source: `research/results/paf_shadow_outcomes_all_cases.csv`
- Offline runner: `tools/paf_offline_pipeline_runner.py`

## Permitted Future Execution

A future checkpoint may run exactly one offline pipeline execution against one user-provided CSV path.

Allowed inputs:

- raw MT5-style CSV with date/time/OHLC columns
- normalized CSV with `time,open,high,low,close`

Not allowed:

- MT5 launch
- Strategy Tester launch
- EA/source changes
- preset changes
- market orders
- pending orders
- position modification
- optimization
- lot/risk increase
- profitability interpretation

## Required Preflight Evidence

Before future execution, Codex must verify:

- the CSV path is absolute
- the file exists and is readable
- the file is intended for `GOLD#` H1
- the source is XM MT5 or explicitly documented as non-broker-comparable
- the raw source file is preserved
- the file has sufficient date coverage for the diagnostic window plus 48 H1 lookahead bars
- the output folder is separated from synthetic self-test outputs
- the command uses `tools/paf_offline_pipeline_runner.py`
- no MT5/Strategy Tester process is required

## Future Command Template

Raw CSV:

```powershell
python tools\paf_offline_pipeline_runner.py `
  --raw-csv <absolute_path_to_raw_csv> `
  --shadow-outcomes research\results\paf_shadow_outcomes_all_cases.csv `
  --results-root research\results\checkpoint_bk_real_csv_pipeline `
  --symbol GOLD# `
  --timeframe H1 `
  --horizon-bars 48 `
  --join-horizons 6,12,24,48 `
  --tp-atr-multiple 1.5 `
  --sl-atr-multiple 1.0
```

Normalized CSV:

```powershell
python tools\paf_offline_pipeline_runner.py `
  --bars-csv <absolute_path_to_normalized_csv> `
  --shadow-outcomes research\results\paf_shadow_outcomes_all_cases.csv `
  --results-root research\results\checkpoint_bk_real_csv_pipeline `
  --symbol GOLD# `
  --timeframe H1 `
  --horizon-bars 48 `
  --join-horizons 6,12,24,48 `
  --tp-atr-multiple 1.5 `
  --sl-atr-multiple 1.0
```

These commands are examples only. They are not executed in Checkpoint BK.

## Stop Conditions

Block execution if any condition is true:

- missing or relative CSV path
- file cannot be read
- symbol/timeframe/source is unclear
- coverage is insufficient
- normalizer fails
- validator fails
- joiner fails
- output folder is ambiguous or points at synthetic self-test output
- user asks for MT5 or Strategy Tester execution in this checkpoint
- user asks for order implementation or trade execution
- user asks for optimization, lot/risk increase, or profitability proof

## Required Future Approval Phrase

`Approved to execute Checkpoint BL offline PAF pipeline on real GOLD# H1 bars CSV <absolute_path_to_csv> for RunId run_20260707_172236.`

This approval phrase authorizes offline CSV processing only. It does not authorize MT5, Strategy Tester, orders, optimization, lot/risk increase, demo/live testing, or profitability claims.

## Decision

- `REAL_CSV_OFFLINE_RUN_APPROVAL_PACKAGE_DEFINED`
- `REAL_MARKET_LOOKAHEAD_CSV_STILL_MISSING`
- `OFFLINE_RUN_NOT_EXECUTED`
- `MT5_NOT_RUN`
- `STRATEGY_TESTER_NOT_RUN`
- `ORDER_PATH_STILL_BLOCKED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`

## Next Safe Step

Wait for the user to provide an absolute path to a real `GOLD#` H1 bars CSV, then proceed with a separate Checkpoint BL execution only if the approval phrase is explicit and the preflight passes.
