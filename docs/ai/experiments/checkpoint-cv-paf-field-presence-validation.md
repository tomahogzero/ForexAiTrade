# Checkpoint CV Experiment: PAF Field Presence Validation

Date: 2026-07-09

## Scope

One approved Strategy Tester diagnostic run only.

- RunId: `run_20260709_182444`
- Symbol: `GOLD#`
- Timeframe: `H1`
- Date range: `2026-03-01` to `2026-03-08`
- Strategy Tester only
- No optimization
- No market orders
- No pending orders
- No position modification
- No lot/risk increase
- No profitability interpretation

## Source / Setup

- Source base observed before execution: `origin/main` at `656580e`
- Branch: `research/checkpoint-cv-paf-field-presence-validation`
- Matrix: `research/paf_diagnostic_matrix_cv.json`
- Compile log: `docs/verification/compile_after_checkpoint_CV.log`
- Compile result: `0 errors, 0 warnings`

## Result

- `execution_status`: `PASS`
- `report_artifact_status`: `FOUND`
- `total_trades`: `0`
- `paf_diagnostics_status`: `FOUND`
- `paf_diagnostic_count`: `97`
- `paf_authoritative_source`: `ea_mirror.log`
- `no_trade_confirmation`: `PASS_FROM_REPORT_AND_EA_LOGS`
- `baseline_fallback_confirmation`: `PASS_FROM_EA_LOGS`
- `paf_forbidden_action_marker_count`: `0`
- `paf_baseline_fallback_marker_count`: `0`

Artifact folder:

`G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\run_20260709_182444\GOLD_HASH_H1_PAF_FIELD_PRESENCE_CV_cv_field_presence_20260301_20260308\`

## Field Presence Outcome

Checkpoint CT diagnostics-only explainability fields were present in `ea_mirror.log` and parser output.

Required log fields found:

- `paf_fibo_ema_fast_value`
- `paf_fibo_ema_slow_value`
- `paf_fibo_ema_gap_points`
- `paf_fibo_ema_slope_state`
- `paf_fibo_price_vs_ema_state`
- `paf_fibo_trend_alignment_state`
- `paf_fibo_pullback_side`
- `paf_fibo_direction_gap_reason`
- `paf_zone_touch_state`
- `paf_rejection_candle_direction`
- `paf_rejection_wick_side`
- `paf_rejection_body_ratio`
- `paf_rejection_wick_ratio`
- `paf_zone_direction_gap_reason`

Required parser keys found:

- `paf_direction_gap_bucket_counts`
- `paf_fibo_direction_gap_reason_counts`
- `paf_zone_direction_gap_reason_counts`

## Interpretation Boundary

This experiment confirms telemetry/logging field presence only. It does not prove profitability, setup quality, entry quality, exit quality, drawdown safety, forward-test readiness, or order-logic readiness.

PAF remains `NOT_READY_FOR_ORDER_LOGIC`.
