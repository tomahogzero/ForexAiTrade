# Checkpoint CU: PAF Field Presence Validation Approval

## Status

Approval package only.

No MT5 run, no Strategy Tester run, no EA/source change, no preset change, no optimization, no lot/risk increase, and no profitability claim.

## Proposed Future Run

- Checkpoint: CV
- Purpose: validate field presence only
- Runs: exactly one
- Symbol: `GOLD#`
- Timeframe: H1
- Date range: `2026-03-01` to `2026-03-08`
- Strategy Tester only
- Optimization disabled
- No demo/live/forward test
- No market orders
- No pending orders
- No position modification

## Required Config Assertions

- `InpEnablePriceActionFibo=true`
- `InpPriceActionFiboDiagnosticsOnly=true`
- `InpPAFUsePendingOrders=false`
- `InpPAFMaxPendingOrders=0`
- `InpManageExistingPositions=false`
- `InpRequireStrategyTester=true`
- `InpPAFLogOnlyOnNewBar=true`
- Optimization disabled
- Strategy Tester only
- No open position in tester context

## Required Field Checks

EA mirror log must include:

- `paf_fibo_ema_fast_value=`
- `paf_fibo_ema_slow_value=`
- `paf_fibo_ema_gap_points=`
- `paf_fibo_ema_slope_state=`
- `paf_fibo_price_vs_ema_state=`
- `paf_fibo_trend_alignment_state=`
- `paf_fibo_pullback_side=`
- `paf_fibo_direction_gap_reason=`
- `paf_zone_touch_state=`
- `paf_rejection_candle_direction=`
- `paf_rejection_wick_side=`
- `paf_rejection_body_ratio=`
- `paf_rejection_wick_ratio=`
- `paf_zone_direction_gap_reason=`

Parser output must include:

- `paf_direction_gap_bucket_counts`
- `paf_fibo_direction_gap_reason_counts`
- `paf_zone_direction_gap_reason_counts`

## Required Guardrails

Future CV must stop/fail on:

- config mismatch
- optimization enabled
- market order attempt
- pending order attempt
- position modification attempt
- baseline fallback
- missing report/log artifacts
- missing required CT fields
- parser failure

## Approval Phrase

`Approved to execute Checkpoint CV one-run PAF field presence validation with symbol GOLD# timeframe H1 date range 2026-03-01 to 2026-03-08 using CT diagnostics-only fields.`

## Current Decision

MT5 execution remains blocked until the exact approval phrase is provided.
