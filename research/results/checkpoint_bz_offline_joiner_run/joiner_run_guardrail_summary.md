# Checkpoint BZ Joiner Run Guardrail Summary

## Execution Type

Offline joiner execution only.

## Approval Phrase

`Approved to execute Checkpoint BZ offline PAF joiner for GOLD# H1 using BX PASS gap policy and offline files only.`

## Guardrails

- MT5 run: `NO`
- Strategy Tester run: `NO`
- EA/source changed: `NO`
- Presets changed: `NO`
- Production validator changed: `NO`
- Market orders: `NO`
- Pending orders: `NO`
- Position modification: `NO`
- Optimization: `NO`
- Lot/risk increase: `NO`
- Profitability claim: `NO`

## Inputs

- Raw H1 CSV: `G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\manual_gap_evidence\GOLD_HASH_H1\csv\GOLD#_H1_202603020100_202603132200.csv`
- Shadow outcomes: `research/results/paf_shadow_outcomes_all_cases.csv`
- BX gap policy dry-run: `PASS`

## Outputs

- Normalized bars: `research/results/checkpoint_bz_offline_joiner_run/paf_lookahead_bars.csv`
- Enriched rows: `research/results/checkpoint_bz_offline_joiner_run/paf_shadow_outcomes_enriched.csv`
- Join summary: `research/results/checkpoint_bz_offline_joiner_run/paf_lookahead_join_summary.md`

## Result

- Normalization: `PASS`
- Joiner: `EXECUTED`
- Rows: `33`
- Joined: `19`
- Direction missing: `14`
- Limitation: `ATR_MISSING`

## Interpretation Guardrail

This checkpoint provides offline diagnostic enrichment only. It is not a trading result, not optimization, and not proof of profitability.
