# Checkpoint CW: PAF Field Presence Artifact Review

## Scope

Review Checkpoint CV artifacts only.

- No MT5 run
- No Strategy Tester run
- No EA/source code changes
- No preset changes
- No trading logic changes
- No optimization
- No lot/risk increase
- No profitability interpretation

## Reviewed Run

- RunId: `run_20260709_182444`
- Symbol: `GOLD#`
- Timeframe: `H1`
- Date range: `2026-03-01` to `2026-03-08`
- Artifact folder: `G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\run_20260709_182444\GOLD_HASH_H1_PAF_FIELD_PRESENCE_CV_cv_field_presence_20260301_20260308\`

## Review Result

Checkpoint CV confirms field presence and parser support for Checkpoint CT explainability fields.

Confirmed:

- `execution_status=PASS`
- `report_artifact_status=FOUND`
- `total_trades=0`
- `paf_diagnostic_count=97`
- `forbidden_action_marker_count=0`
- `baseline_fallback_marker_count=0`
- Required CT fields are present.
- Required parser summary keys are present.

## Interpretation

The original direction gap is now explainable:

- `NO_SETUP_DIRECTION_NOT_REQUIRED`: `64`
- `USABLE_DIRECTION`: `19`
- `TREND_ALIGNMENT_CONFLICT`: `9`
- `WICK_TOO_SMALL`: `4`
- `PRICE_BETWEEN_EMAS`: `1`

This means Checkpoint CT/CV improved diagnostics, but it does not make PAF ready for order logic.

## Recommendation

Next safe checkpoint:

`Checkpoint CX: Multi-Window CT Field Presence and Direction-Gap Stability Approval`

This next checkpoint should be approval-only first and must not run MT5 until separately approved.
