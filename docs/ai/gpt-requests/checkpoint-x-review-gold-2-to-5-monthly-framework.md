# GPT Review Request: Checkpoint X Gold 2-5% Monthly Research Framework

Created: 2026-07-04

## Repository

ForexAiTrade

## Files to review

- `docs/37_Checkpoint_X_Gold_2_5_Monthly_Research_Framework_TH.md`
- `docs/ai/tasks/checkpoint-x-gold-2-to-5-monthly-research-framework.md`
- `research/strategy_ideas/gold_2_to_5_monthly_research_framework.md`

## Review context

The user is interested in Gold research because Gold can move strongly and may offer faster opportunity than EURUSD.

The user mentioned a possible 2-5% monthly target, but the project must remain capital-preservation-first.

This checkpoint is documentation-only and must not approve MT5 execution, Strategy Tester execution, optimization, demo/live trading, lot/risk increase, or profitability claims.

## Review questions

1. Does the framework treat 2-5% monthly as an aggressive research target rather than a promise?
2. Does it preserve capital-first guardrails?
3. Does it correctly separate Gold from EURUSD and other forex pairs?
4. Does it prohibit forced broker minimum lot when risk budget is insufficient?
5. Does it avoid martingale, uncontrolled grid, recovery lot multiplication, and no-stop-loss holding?
6. Does it identify common Gold strategy families without implementing them?
7. Does it require enough diagnostics before any future implementation?
8. Does it correctly block MT5 execution until artifact-path reliability and explicit approval exist?
9. Are any additional risk gates needed before Gold research can be considered?

## Expected output

- PASS / NEEDS_FIX
- Issues found
- Required docs-only fixes
- Optional improvements
- Whether Checkpoint Y should be docs-only or diagnostic-only planning

