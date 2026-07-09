# Checkpoint CI: PAF Data Completeness Plan

## Status

`DONE_FOR_REVIEW`

## Scope

Checkpoint CI creates a documentation-only plan for improving PAF diagnostic data completeness before any order logic.

It does not:

- run MT5
- run Strategy Tester
- change EA/source code
- change presets
- add order logic
- add market orders
- add pending orders
- optimize
- increase lot/risk
- claim profitability

## Current Evidence

From Checkpoints CG/CH:

- rows: `33`
- relabel-ready rows: `17`
- direction-missing rows: `14`
- data-missing rows: `2`
- classification: `NOT_READY_FOR_ORDER_LOGIC`

## Plan

Define the fields required before PAF first-touch results can be trusted:

- signal time
- symbol/timeframe
- classification
- direction
- entry reference
- intended SL
- intended TP
- session/spread/regime
- source run/file metadata

## Proposed Gates

Before any future order logic:

- `direction_missing_rate <= 10%`
- `data_missing_rate <= 5%`
- `relabel_ready_rows >= 100` for diagnostic interpretation
- `relabel_ready_rows >= 300` before rule-candidate discussion
- entry, SL, and TP references must be complete

## Recommended Next Checkpoint

Checkpoint CJ should add a tooling-only completeness audit report.

It should not run MT5 or change trading behavior.

## Progress Estimate

- Research infrastructure: `96%`
- PAF diagnostic pipeline: `89%`
- PAF data completeness: `62%`
- PAF order-readiness: `20%`
- Demo/live readiness: `0%`

