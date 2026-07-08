# Checkpoint BG: PAF Bars Schema Normalization Plan

Date: 2026-07-08

## Scope

Define a documentation-only schema normalization plan for future MT5-exported OHLC bar files.

No MT5 run.
No Strategy Tester run.
No EA/source changes.
No preset changes.
No tool implementation in this checkpoint.
No optimization.
No lot/risk increase.
No profitability claim.

## Problem

The validator expects:

- `time`
- `open`
- `high`
- `low`
- `close`

MT5 or other checked sources may export bars with different column names, separated date/time columns, extra volume columns, or different delimiters.

## Allowed Transformations

Only format-level transformations are allowed:

- combine date and time columns
- rename OHLC columns
- remove extra columns
- convert delimiter
- trim whitespace
- normalize timestamp format without timezone shift

## Forbidden Transformations

Do not:

- change OHLC prices
- fill missing bars without source
- shift timezone without evidence
- resample another timeframe without a separate checkpoint
- use a different symbol as `GOLD#`
- remove rows to improve outcome
- feed lookahead data into EA decisions

## Future Tool Candidate

Potential future offline-only tool:

`tools/paf_bars_schema_normalizer.py`

This tool may be implemented only in a later checkpoint.

It should preserve the raw file, write a normalized file, and produce a normalization summary.

## Required Follow-Up

After normalization, run `tools/paf_lookahead_bars_validator.py`.

Do not run `tools/paf_lookahead_joiner.py` unless the validator passes.

## Decision

- `SCHEMA_NORMALIZATION_PLAN_DEFINED`
- `NORMALIZER_TOOL_NOT_IMPLEMENTED`
- `REAL_MARKET_LOOKAHEAD_CSV_STILL_MISSING`
- `VALIDATOR_NOT_RUN`
- `JOINER_NOT_RUN`
- `MT5_NOT_RUN`
- `ORDER_PATH_STILL_BLOCKED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`
