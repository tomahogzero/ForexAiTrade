# GPT Review Request: Checkpoint CJ PAF Data Completeness Audit

Please review Checkpoint CJ for ForexAiTrade.

## Files to Review

- `tools/paf_data_completeness_audit.py`
- `docs/102_Checkpoint_CJ_PAF_Data_Completeness_Audit_TH.md`
- `docs/ai/tasks/checkpoint-cj-paf-data-completeness-audit.md`
- `research/results/checkpoint_cj_paf_data_completeness/completeness_summary.md`
- `research/results/checkpoint_cj_paf_data_completeness/completeness_summary.json`
- `research/results/checkpoint_cj_paf_data_completeness/missing_fields_by_row.csv`
- `research/results/checkpoint_cj_paf_data_completeness/readiness_by_classification.csv`

## Review Questions

1. Does the tool remain offline-only and avoid MT5/Strategy Tester execution?
2. Does it correctly preserve `DATA_COMPLETENESS_GATE_FAIL` and `NOT_READY_FOR_ORDER_LOGIC`?
3. Does it avoid profitability claims, optimization, lot/risk increase, and order logic?
4. Is the handling of `RELABEL_READY`, `DIRECTION_MISSING`, and `DATA_MISSING` consistent with the CE output?
5. Is the recommended next step appropriately focused on diagnosing `DIRECTION_MISSING` before any EA/source change?

## Expected Verdict

Return:

- `PASS`
- `NEEDS_FIX`

List exact issues if `NEEDS_FIX`.

