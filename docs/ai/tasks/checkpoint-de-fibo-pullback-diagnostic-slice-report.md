# Checkpoint DE: Fibo Pullback Diagnostic Slice Report

Date: 2026-07-09

## Scope

Checkpoint DE is an artifact-summary-only diagnostic slice report.

It uses existing CV + CY + DB + DC + DD committed summaries. It does not run MT5, does not run Strategy Tester, does not modify EA/source code, does not modify presets, does not optimize, does not increase lot/risk, and does not add trading/order logic.

## Inputs

- `research/results/checkpoint_cv_paf_field_presence_validation_summary.json`
- `research/results/checkpoint_cy_paf_multi_window_field_stability_summary.json`
- `research/results/checkpoint_db_paf_data_collection_expansion_summary.json`
- `research/results/checkpoint_dc_paf_diagnostic_interpretation_summary.json`
- `research/results/checkpoint_dd_fibo_pullback_diagnostic_plan_summary.json`

## Key Findings

- Combined diagnostic rows: `621`
- Combined possible setup rows: `174`
- Combined usable direction rows: `106`
- Possible Fibo Pullback rows: `128`
- Possible Fibo Pullback share of possible setup rows: `73.6%`
- Diagnostic interpretation gate: `PASS_LOW_MARGIN`
- Rule-candidate gate: `FAIL`

## Interpretation Boundary

`Possible Fibo Pullback` is approved only as the first diagnostic focus.

It is not:

- a buy signal
- a sell signal
- a pending order rule
- an edge proof
- a profitability proof
- a demo/live approval

## Limitations

The committed summaries do not contain enough row-level Fibo-specific detail to answer:

- Fibo-specific usable direction counts
- Fibo-specific BUY/SELL distribution
- Fibo-specific direction confidence distribution
- Fibo-specific first-touch usability
- Fibo-specific EMA state distribution
- Fibo-specific spread/regime/session distribution

## Verdict

- `FIBO_PULLBACK_DIAGNOSTIC_FOCUS_CONFIRMED`
- `FIBO_PULLBACK_ROW_LEVEL_SLICE_REQUIRED`
- `RULE_CANDIDATE_GATE_FAIL`
- `ORDER_LOGIC_NOT_APPROVED`
- `PAF_NOT_READY_FOR_ORDER_LOGIC`

## Recommended Next Safe Step

Checkpoint DF should create an artifact-only row-level Fibo Pullback slice extractor/report from existing logs/artifacts if available.

No MT5 run should occur unless separately approved.

