# Checkpoint CN: PAF Direction Context Diagnostics Implementation

## Purpose

Implement the diagnostics-only direction context fields approved by Checkpoint CM.

The goal is to make future Price Action / Fibo logs explain why a diagnostic row has or does not have a usable first-touch direction.

## Scope

Allowed:

- Add diagnostics-only fields to Price Action / Fibo diagnostic state.
- Log the approved `paf_*` context fields.
- Update parser compatibility for new fields and legacy logs.
- Compile if MQL5 changes.
- Produce guardrail and review documentation.

Not allowed:

- No market orders.
- No pending orders.
- No position modification.
- No strategy entry/exit behavior change for profitability.
- No optimization.
- No lot/risk increase.
- No MT5 / Strategy Tester execution in this checkpoint.
- No demo/live/forward testing.
- No profitability claim.

## Implementation Summary

MQL5:

- `MQL5/Include/ForexAiTrade/Strategies/PriceActionFiboStrategy.mqh`
- Added context fields for candidate direction, source, confidence, EMA values/slopes, trend context, pullback side, zone side, rejection details, wick side, break/retest details.
- Existing `direction_context` and `direction_reason` remain for backward compatibility.
- `Evaluate()` remains diagnostic-only and does not emit trade signals.

Python:

- `tools/paf_diagnostic_parser.py`
- Added field normalization for new and legacy diagnostic logs.
- Added aggregate counts for direction context fields.

## Verification

- `python -m py_compile tools/paf_diagnostic_parser.py`: PASS
- MetaEditor compile of `MQL5/Experts/ForexAiTrade/ForexAiTrade.mq5`: PASS, `0 errors, 0 warnings`
- MT5 / Strategy Tester: NOT RUN

## Result

Checkpoint CN prepares better diagnostic data for future runs but does not prove that direction completeness improves yet.

Future validation requires a separately approved diagnostic run.
