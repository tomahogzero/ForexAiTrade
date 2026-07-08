# Checkpoint BL-Prep: PAF Real CSV Handoff Guide

Date: 2026-07-08

## Scope

Documentation-only handoff preparation.

This checkpoint does not run MT5, does not run Strategy Tester, does not run the offline pipeline, does not change EA/source code, does not change presets, does not optimize, does not increase lot/risk, and does not claim profitability.

## Purpose

Checkpoint BJ added the offline pipeline runner.
Checkpoint BK defined the future approval package.

Checkpoint BL-Prep tells the user exactly what real `GOLD#` H1 CSV file is needed before Checkpoint BL can safely run the offline pipeline.

## Required Real CSV

Target context:

- RunId: `run_20260707_172236`
- Symbol: `GOLD#`
- Timeframe: `H1`
- Diagnostic range: `2026-03-01` to `2026-03-08`
- Required coverage: at least through `2026-03-10 23:59:59`

Accepted formats:

- raw MT5-style CSV with `<DATE>`, `<TIME>`, `<OPEN>`, `<HIGH>`, `<LOW>`, `<CLOSE>`
- normalized CSV with `time`, `open`, `high`, `low`, `close`

## Recommended Location

Recommended folder:

`G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\manual_exports\`

Recommended filenames:

- `GOLD_HASH_H1_20260301_20260310_raw_mt5.csv`
- `GOLD_HASH_H1_20260301_20260310_normalized.csv`

Use `GOLD_HASH` in filenames instead of `GOLD#` to avoid shell/path issues.

## Required Future Approval Phrase

`Approved to execute Checkpoint BL offline PAF pipeline on real GOLD# H1 bars CSV <absolute_path_to_csv> for RunId run_20260707_172236.`

This future approval authorizes only offline CSV processing. It does not authorize MT5, Strategy Tester, market orders, pending orders, position modification, optimization, lot/risk increase, demo/live testing, or profitability claims.

## BL Future Execution Limits

Checkpoint BL may:

- check the absolute CSV path
- normalize if needed
- validate schema and coverage
- join with shadow outcomes
- produce offline summary artifacts

Checkpoint BL must not:

- launch MT5
- launch Strategy Tester
- place or modify orders
- change EA/source code
- change presets
- optimize
- increase lot/risk
- interpret results as profitability proof

## Stop Conditions

Block future execution if:

- CSV path is missing or relative
- file does not exist
- file cannot be read
- symbol/timeframe/source is unclear
- coverage is insufficient
- normalizer fails
- validator fails
- joiner fails
- user asks for order path or demo/live
- user asks for optimization or profitability proof

## Decision

- `REAL_CSV_HANDOFF_GUIDE_DEFINED`
- `REAL_CSV_PATH_STILL_REQUIRED`
- `OFFLINE_PIPELINE_NOT_RUN`
- `MT5_NOT_RUN`
- `STRATEGY_TESTER_NOT_RUN`
- `ORDER_PATH_STILL_BLOCKED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`

## Next Safe Step

Wait for the user to place or provide the absolute path to the real `GOLD#` H1 CSV file, then require the explicit Checkpoint BL approval phrase before running any offline pipeline command.
