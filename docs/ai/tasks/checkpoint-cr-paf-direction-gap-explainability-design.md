# Checkpoint CR: PAF Direction Gap Explainability Design

## Status

Documentation / design-only checkpoint.

No MT5 run, no Strategy Tester run, no EA/source change, no preset change, no optimization, no lot/risk increase, and no profitability claim.

## Context

Checkpoint CQ reviewed Checkpoint CP artifacts and found that `DIRECTION_UNKNOWN=78` is mostly expected:

- `NO_SETUP_DIRECTION_NOT_REQUIRED`: `64`
- `USABLE_DIRECTION`: `19`
- `FIBO_PULLBACK_EMA_DIRECTION_CONTEXT_MISSING`: `10`
- `ZONE_REJECTION_CANDLE_DIRECTION_CONTEXT_MISSING`: `4`

The true possible-setup direction explainability gap is `14` rows.

## Objective

Define a diagnostics-only design for explaining the 14 possible-setup direction gaps before any future implementation or Strategy Tester validation.

## Required Future Scope

Future work may add only diagnostic fields, parser support, and summary outputs that explain:

- why Fibo Pullback EMA direction context is unclear
- why Zone Rejection candle/zone direction context is unclear
- whether a row should remain possible setup or be reclassified as no setup

Future work must not:

- emit `SIGNAL_BUY` or `SIGNAL_SELL`
- send market orders
- send pending orders
- modify positions
- fallback to baseline strategy
- optimize parameters
- increase lot/risk
- claim profitability

## Proposed Fibo Pullback Gap Reasons

- `EMA_VALUES_MISSING`
- `EMA_GAP_TOO_SMALL`
- `EMA_SLOPE_FLAT`
- `PRICE_BETWEEN_EMAS`
- `TREND_ALIGNMENT_CONFLICT`
- `PULLBACK_SIDE_UNKNOWN`
- `FIBO_ZONE_SIDE_CONFLICT`
- `INSUFFICIENT_BAR_CONTEXT`

## Proposed Zone Rejection Gap Reasons

- `ZONE_SIDE_UNKNOWN`
- `ZONE_TOUCH_MISSING`
- `TOUCHED_BOTH_SIDES`
- `REJECTION_CANDLE_DOJI`
- `WICK_TOO_SMALL`
- `BODY_DIRECTION_CONFLICT`
- `WICK_SIDE_CONFLICT`
- `INSUFFICIENT_BAR_CONTEXT`

## Acceptance Criteria For A Future Implementation Checkpoint

- EA compiles `0 errors, 0 warnings` if MQL5 changes are made.
- Parser remains backward-compatible with older logs.
- Missing fields become `null` or `UNKNOWN`, not parser crashes.
- Summary separates `NO_SETUP_DIRECTION_NOT_REQUIRED` from true possible-setup gaps.
- No order path is activated.
- No MT5 run occurs without separate explicit approval.

## Current Recommendation

Proceed next to Checkpoint CS as diagnostics-only implementation approval or diagnostics-only implementation with compile verification.

Order logic remains blocked.
