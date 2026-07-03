# GPT Review Request: Checkpoint Y Gold Diagnostic Data Requirements

Created: 2026-07-04

## Files to review

- `docs/38_Checkpoint_Y_Gold_Diagnostic_Data_Requirements_TH.md`
- `docs/ai/tasks/checkpoint-y-gold-diagnostic-data-requirements-and-no-trade-logging-plan.md`
- `research/strategy_ideas/gold_diagnostic_data_requirements.md`

## Context

Checkpoint X introduced a Gold 2-5% monthly research framework as an aggressive research target only.

Checkpoint Y defines what diagnostics must exist before Gold implementation, Gold Strategy Tester execution, optimization, or any trading behavior change.

This is documentation-only.

## Review questions

1. Does Checkpoint Y require enough Gold diagnostics before implementation?
2. Does it keep Gold diagnostic paths no-trade only?
3. Does it block market orders, pending orders, position modification, baseline fallback, `SIGNAL_BUY`, and `SIGNAL_SELL`?
4. Does it keep broker-specific risk-budget review central?
5. Does it preserve Checkpoint W artifact-path reliability requirements?
6. Does it correctly treat missing artifacts as inconclusive?
7. Is the proposed Codex/GPT autonomy policy safe enough?
8. Should auto-merge remain blocked unless the user gives explicit standing approval?
9. Is Checkpoint Z as an approval-only pack the right next step?

## Expected output

- PASS / NEEDS_FIX
- Issues found
- Required docs-only fixes
- Optional improvements
- Whether Checkpoint Z should remain approval-only

