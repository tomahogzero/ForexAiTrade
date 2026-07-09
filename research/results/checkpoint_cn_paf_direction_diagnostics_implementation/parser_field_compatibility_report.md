# Checkpoint CN Parser Field Compatibility Report

## Result

`PASS_PARSER_COMPATIBILITY_STATIC_CHECK`

## New Field Handling

`tools/paf_diagnostic_parser.py` now recognizes these direction context fields:

- `paf_candidate_direction`
- `paf_direction_source`
- `paf_direction_confidence`
- `paf_direction_reason`
- `paf_direction_is_usable_for_first_touch`
- `paf_trend_context`
- `paf_pullback_side`
- `paf_ema_fast_value`
- `paf_ema_slow_value`
- `paf_ema_fast_slope`
- `paf_ema_slow_slope`
- `paf_fibo_zone_level`
- `paf_zone_side`
- `paf_rejection_side`
- `paf_candle_body_direction`
- `paf_wick_side`
- `paf_rejection_strength`
- `paf_break_direction`
- `paf_retest_side`
- `paf_break_level`

## Legacy Log Compatibility

If an older log does not contain the new fields:

- `paf_candidate_direction` is derived from `direction_context`
- `paf_direction_reason` is copied from `direction_reason`
- missing `paf_*` fields are filled with safe defaults

## Limitation

This is a static/parser compatibility check only.

It does not prove live diagnostic completeness because MT5 / Strategy Tester was not run in Checkpoint CN.

Future validation requires a separately approved diagnostic run.
