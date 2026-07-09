# Checkpoint BY Offline Joiner Approval

This is an approval package only. It does not run MT5, does not run Strategy Tester, does not run the joiner, and does not prove profitability.

## Current Gate Evidence

- Source checkpoint: `BX`
- Gap policy dry-run verdict: `PASS`
- Accepted gaps: `9`
- Blocking/review gaps: `0`
- Daily broker-session gaps accepted in dry-run: `8`
- Weekend market closure accepted in dry-run: `1`

## Future Execution Scope

- Symbol: `GOLD#`
- Timeframe: `H1`
- Tool: `tools/paf_lookahead_joiner.py`
- Shadow outcomes: `research/results/paf_shadow_outcomes_all_cases.csv`
- Results root: `research/results/checkpoint_bz_offline_joiner_run/`

## Gate Status

- Offline joiner execution: `BLOCKED_PENDING_EXPLICIT_APPROVAL`
- MT5: `BLOCKED`
- Strategy Tester: `BLOCKED`
- Production validator change: `BLOCKED`
- Optimization: `BLOCKED`
- Demo/live: `BLOCKED`

## Required Approval Phrase

`Approved to execute Checkpoint BZ offline PAF joiner for GOLD# H1 using BX PASS gap policy and offline files only.`
