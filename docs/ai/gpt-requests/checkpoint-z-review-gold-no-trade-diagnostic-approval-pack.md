# GPT Review Request: Checkpoint Z Gold No-Trade Diagnostic Approval Pack

Created: 2026-07-04

## Files to review

- `docs/39_Checkpoint_Z_Gold_No_Trade_Diagnostic_Execution_Approval_Pack_TH.md`
- `docs/ai/tasks/checkpoint-z-gold-no-trade-diagnostic-execution-approval-pack.md`
- `docs/ai/decisions/2026-07-04-codex-gpt-docs-only-automerge-policy.md`

## Context

Checkpoint Z is an approval-only pack for a future Gold no-trade diagnostic Strategy Tester run.

It must not execute MT5, run Strategy Tester, change EA/source code, change presets, optimize, increase risk, or claim profitability.

The user has approved Codex auto-merge only for docs-only/research-plan-only PRs with GPT `PASS` and no source/preset/MT5/optimization/risk changes.

## Review questions

1. Is Checkpoint Z clearly approval-only and not execution?
2. Does it keep the future Gold run one-run only?
3. Does it keep the future symbol constrained to verified `GOLD#` or `GOLDm#` only?
4. Does it require a concrete date range no longer than 1 month?
5. Does it preserve Checkpoint W artifact-path requirements?
6. Does it require source/preset drift guard?
7. Does it require Gold broker metadata and risk-budget checks?
8. Does it block market orders, pending orders, position modification, and baseline fallback?
9. Does it treat missing artifacts as `FAILED_NO_TESTER_ARTIFACTS / INCONCLUSIVE`?
10. Is the docs-only auto-merge decision scoped safely?

## Expected output

- PASS / NEEDS_FIX
- Issues found
- Required docs-only fixes
- Optional improvements
- Whether Checkpoint AA should be execution approval only

