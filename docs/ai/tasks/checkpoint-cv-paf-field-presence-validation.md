# Checkpoint CV: PAF Field Presence Validation

## Objective

Validate that Checkpoint CT diagnostics-only PAF direction explainability fields appear in a real Strategy Tester diagnostic run and are parsed correctly.

## Approved Run

Approval phrase received:

`Approved to execute Checkpoint CV one-run PAF field presence validation with symbol GOLD# timeframe H1 date range 2026-03-01 to 2026-03-08 using CT diagnostics-only fields.`

Executed scope:

- Symbol: `GOLD#`
- Timeframe: `H1`
- Date range: `2026-03-01` to `2026-03-08`
- One run only
- Strategy Tester only
- No optimization
- No market orders
- No pending orders
- No position modification
- No lot/risk increase
- No profitability interpretation

## Output

- RunId: `run_20260709_182444`
- Artifact folder: `G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\run_20260709_182444\GOLD_HASH_H1_PAF_FIELD_PRESENCE_CV_cv_field_presence_20260301_20260308\`
- Compile log: `docs/verification/compile_after_checkpoint_CV.log`
- Result doc: `docs/114_Checkpoint_CV_PAF_Field_Presence_Validation_Result_TH.md`
- Experiment memory: `docs/ai/experiments/checkpoint-cv-paf-field-presence-validation.md`
- Summary: `research/results/checkpoint_cv_paf_field_presence_validation_summary.md`
- Machine-readable summary: `research/results/checkpoint_cv_paf_field_presence_validation_summary.json`

## Result

PASS for field-presence validation:

- MT5 report artifact was produced.
- Parsed report shows `total_trades=0`.
- PAF diagnostics were generated from `ea_mirror.log`.
- All required CT fields were present in logs.
- Required parser summary keys were present.
- Forbidden action marker count was `0`.
- Baseline fallback marker count was `0`.

## Remaining Boundary

PAF is still not ready for order logic. The next safe checkpoint should review CV artifacts and decide whether the added gap reasons are sufficiently explanatory before any further diagnostic design.
