# Decision: Codex/GPT Docs-Only Auto-Merge Policy

Date: 2026-07-04

## User standing approval

The user approved:

> อนุญาตให้ Codex auto-merge docs-only/research-plan-only PR ที่ GPT review PASS และไม่มี source/preset/MT5/optimization/risk changes

## Allowed auto-merge scope

Codex may auto-merge only when all conditions are true:

- PR is docs-only or research-plan-only
- GPT review result is `PASS`
- no MQL5/source code changes
- no preset changes
- no runner/execution behavior changes
- no MT5 run
- no Strategy Tester run
- no optimization
- no lot/risk increase
- no new backtest/performance result
- no profitability claim
- artifact audit passes
- PR is mergeable

## Auto-merge remains blocked for

- MQL5/source code changes
- preset changes
- runner or script behavior changes
- MT5/Strategy Tester execution
- backtest result generation
- optimization
- execution approval checkpoints
- demo/live forward testing
- risk/lot changes
- GPT `NEEDS_FIX`
- GPT `CONDITIONAL_PASS`
- merge conflict

## Notes

This decision reduces manual GitHub work only for safe documentation/research-plan checkpoints.

It does not approve MT5 execution or trading behavior changes.

