# Checkpoint BN: PAF CSV Availability Preflight

Date: 2026-07-08

## Scope

Documentation and filesystem availability preflight only.

This checkpoint does not run MT5, does not run Strategy Tester, does not run the offline pipeline, does not change EA/source code, does not change presets, does not optimize, does not increase lot/risk, and does not claim profitability.

## Preflight Performed

Checked the recommended manual export folder:

`G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\manual_exports`

Observed result:

`MISSING: mt5_artifacts\manual_exports`

No real `GOLD#` H1 CSV path is currently available for Checkpoint BL.

## Status

- Manual export folder: `MISSING`
- Real CSV file: `MISSING`
- CSV source verification: `NOT_AVAILABLE`
- Checkpoint BL execution: `BLOCKED`
- Offline pipeline: `NOT_RUN`
- MT5: `NOT_RUN`
- Strategy Tester: `NOT_RUN`
- Order path: `BLOCKED`

## User Action Required

Create or provide a real `GOLD#` H1 CSV file covering at least:

`2026-03-01 00:00:00` through `2026-03-10 23:59:59`

Recommended location:

`G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\manual_exports\GOLD_HASH_H1_20260301_20260310_raw_mt5.csv`

or:

`G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\manual_exports\GOLD_HASH_H1_20260301_20260310_normalized.csv`

## Future Approval Phrase

`Approved to execute Checkpoint BL offline PAF pipeline on real GOLD# H1 bars CSV <absolute_path_to_csv> for RunId run_20260707_172236.`

This approval phrase authorizes offline CSV processing only. It does not authorize MT5, Strategy Tester, market orders, pending orders, position modification, optimization, lot/risk increase, demo/live testing, or profitability claims.

## Decision

- `CSV_AVAILABILITY_PREFLIGHT_DONE`
- `MANUAL_EXPORT_FOLDER_MISSING`
- `REAL_CSV_PATH_STILL_REQUIRED`
- `CHECKPOINT_BL_BLOCKED`
- `OFFLINE_PIPELINE_NOT_RUN`
- `MT5_NOT_RUN`
- `STRATEGY_TESTER_NOT_RUN`
- `ORDER_PATH_STILL_BLOCKED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`

## Next Safe Step

Wait for the real CSV absolute path. Do not run the offline pipeline until the user provides the exact Checkpoint BL approval phrase.
