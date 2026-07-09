# GPT Review Request: Checkpoint CG PAF First-Touch Attribution

Please review Checkpoint CG for ForexAiTrade.

## Files to Review

- `tools/paf_first_touch_attribution.py`
- `docs/99_Checkpoint_CG_PAF_First_Touch_Attribution_TH.md`
- `docs/ai/tasks/checkpoint-cg-paf-first-touch-attribution.md`
- `research/results/checkpoint_cg_first_touch_attribution/first_touch_attribution_summary.md`
- `research/results/checkpoint_cg_first_touch_attribution/first_touch_attribution_summary.json`
- `research/results/checkpoint_cg_first_touch_attribution/first_touch_attribution_by_dimension.csv`
- `research/results/checkpoint_cg_first_touch_attribution/first_touch_attribution_guardrail_summary.md`

## Review Questions

1. Does the tool stay offline-only and avoid MT5 / Strategy Tester execution?
2. Does the attribution avoid rerunning or changing first-touch labels?
3. Does it avoid optimization and profitability claims?
4. Does it correctly keep order logic blocked?
5. Does it present Fibo/session/spread/regime findings as diagnostics only?
6. Are sample-size and direction-missing blockers clearly preserved?

## Expected Verdict

Return:

- `PASS`
- `NEEDS_FIX`

List exact issues if `NEEDS_FIX`.
