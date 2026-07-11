# Checkpoint EB Diagnostic Rule-Candidate Specification

Date: 2026-07-11

## Decision

`PAF_FIBO_USABLE_DIRECTION_V1_SPEC_DEFINED`

This is a default-disabled diagnostic row-eligibility specification, not a BUY/SELL signal or order permission.

Frozen outputs:

- `ELIGIBLE_DIAGNOSTIC_ROW`
- `REJECTED_DIRECTION_GAP`
- `NOT_APPLICABLE`
- `INVALID_DATA`

Precedence is fail-closed: invalid/missing/conflicting data, non-Fibo classification, direction-gap rejection, then eligibility only when all required categorical invariants pass.

## Gates

- specification: `DEFINED`
- implementation: `NOT_IMPLEMENTED`
- validation: `NOT_RUN`
- research-use approval: `NOT_APPROVED`
- order logic: `FAIL_NOT_APPROVED`
- PAF: `NOT_READY_FOR_ORDER_LOGIC`
- three-year gate: `PASS`
- existing 20-window gate: `FAIL_REPORTED_SEPARATELY`

## Next Safe Step

Checkpoint EC docs-only approval/readiness package for an offline verifier. Freeze exact committed inputs, fixtures, outputs, and separate approval wording. No MT5, optimization, EA/preset change, order logic, demo/live test, or profitability claim.
