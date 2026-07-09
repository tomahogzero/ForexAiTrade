# Checkpoint CT: PAF Direction Explainability Fields

## Status

Diagnostics-only implementation completed.

No MT5 run, no Strategy Tester run, no preset change, no optimization, no lot/risk increase, and no profitability claim.

## Changed Scope

Allowed files changed:

- `MQL5/Include/ForexAiTrade/Strategies/PriceActionFiboStrategy.mqh`
- `tools/paf_diagnostic_parser.py`
- `docs/verification/compile_after_checkpoint_CT.log`
- docs / docs/ai task and review files

## MQL5 Diagnostics Added

Fibo Pullback fields:

- `paf_fibo_ema_fast_value`
- `paf_fibo_ema_slow_value`
- `paf_fibo_ema_gap_points`
- `paf_fibo_ema_slope_state`
- `paf_fibo_price_vs_ema_state`
- `paf_fibo_trend_alignment_state`
- `paf_fibo_pullback_side`
- `paf_fibo_direction_gap_reason`

Zone Rejection fields:

- `paf_zone_touch_state`
- `paf_rejection_candle_direction`
- `paf_rejection_wick_side`
- `paf_rejection_body_ratio`
- `paf_rejection_wick_ratio`
- `paf_zone_direction_gap_reason`

## Verification

- Parser syntax check: PASS
- EA compile: PASS
- Compile log: `docs/verification/compile_after_checkpoint_CT.log`
- Compile result: `0 errors, 0 warnings`
- MT5 run: NO
- Strategy Tester run: NO

## Guardrail Scan

`PriceActionFiboStrategy.mqh` was checked for:

- `SIGNAL_BUY`
- `SIGNAL_SELL`
- `OrderSend`
- `.Buy(`
- `.Sell(`
- `BuyLimit`
- `SellLimit`
- `BuyStop`
- `SellStop`
- `PositionModify`

Result: no matches in the PAF strategy file.

## Current Decision

PAF remains diagnostic-only.

Order logic remains blocked.

Next checkpoint should be Checkpoint CU approval package for one-run Strategy Tester validation of field presence only.
