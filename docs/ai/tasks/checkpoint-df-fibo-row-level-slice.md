# Checkpoint DF: Fibo Pullback Row-Level Slice

Date: 2026-07-09

## Scope

Checkpoint DF creates an offline row-level slice for `POSSIBLE_FIBO_PULLBACK` diagnostics from existing `ea_mirror.log` artifacts.

It does not run MT5, does not run Strategy Tester, does not modify EA/MQL5, does not modify presets, does not change trading logic, does not optimize, does not increase lot/risk, and does not add order logic.

## Tool Added

- `tools/paf_fibo_slice_report.py`

The tool reads existing logs only and outputs:

- `research/results/checkpoint_df_fibo_pullback_row_level_slice.csv`
- `research/results/checkpoint_df_fibo_pullback_row_level_slice_summary.md`
- `research/results/checkpoint_df_fibo_pullback_row_level_slice_summary.json`

## Inputs

- `mt5_artifacts/run_20260709_182444`
- `mt5_artifacts/run_20260709_202415`
- `mt5_artifacts/run_20260709_212026`

## Key Results

- Diagnostic rows scanned: `621`
- Fibo Pullback rows: `128`
- Fibo usable first-touch rows: `85`
- Fibo direction gap rows: `43`
- Forbidden action markers: `0`
- Baseline fallback markers: `0`

## Direction Counts

- SELL: `53`
- BUY: `32`
- DIRECTION_UNKNOWN: `43`

## Gate Status

- Fibo row-level slice: `BUILT`
- Fibo-specific usable direction rows: below future gate
- Rule-candidate gate: `FAIL`
- Order logic: `NOT_APPROVED`
- PAF: `NOT_READY_FOR_ORDER_LOGIC`

## Recommended Next Step

Checkpoint DG should interpret the Fibo row-level slice artifact-only.

No MT5 run, no EA/MQL5 change, no preset change, no optimization, and no order logic.

