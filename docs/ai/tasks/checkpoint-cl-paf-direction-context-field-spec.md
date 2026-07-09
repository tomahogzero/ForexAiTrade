# Checkpoint CL: PAF Direction Context Field Specification

## Status

`DONE_FOR_REVIEW`

## Scope

Checkpoint CL defines diagnostics-only direction context fields for Price Action/Fibo diagnostics.

This checkpoint is documentation only.

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

## Background

Checkpoint CK found:

- `FIBO_PULLBACK_EMA_DIRECTION_CONTEXT_MISSING`: `10` rows
- `ZONE_REJECTION_CANDLE_DIRECTION_CONTEXT_MISSING`: `4` rows

## Field Groups Defined

- Common PAF direction fields
- Fibo Pullback fields
- Zone Rejection fields
- Break Retest fields
- Validation rules
- Parser compatibility rules
- Future audit outputs

## Decision

`DIRECTION_FIELD_SPEC_DEFINED`

`IMPLEMENTATION_NOT_APPROVED`

`ORDER_LOGIC_NOT_APPROVED`

`NOT_READY_FOR_ORDER_LOGIC`

## Recommended Next Checkpoint

Checkpoint CM should be an approval package for a diagnostics-only implementation plan, if the user wants to proceed.

It must still not approve order logic or trading behavior changes.

## Progress Estimate

- Research infrastructure: `96%`
- PAF diagnostic pipeline: `91%`
- PAF data completeness: `67%`
- PAF direction completeness: `61%`
- PAF order-readiness: `20%`
- Demo/live readiness: `0%`

