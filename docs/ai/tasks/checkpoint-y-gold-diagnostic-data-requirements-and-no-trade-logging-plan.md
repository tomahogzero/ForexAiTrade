# Checkpoint Y: Gold Diagnostic Data Requirements and No-Trade Logging Plan

Created: 2026-07-04

## Purpose

Define what must be logged and proven before any Gold strategy implementation, Gold Strategy Tester run, or Gold optimization is considered.

This checkpoint is documentation-only.

## Context

- PR #15 / Checkpoint X is merged.
- Gold 2-5% monthly remains an aggressive research target only.
- Checkpoint T remains failed/inconclusive because required tester artifacts were not produced.
- Checkpoint W created verified artifact path requirements.
- No Gold Strategy Tester run is approved by this checkpoint.

## Required diagnostic areas

- broker symbol metadata
- no-trade signal classifications
- risk budget and minimum lot feasibility
- session attribution
- regime attribution
- event/macro context
- spread/slippage context
- artifact path reliability
- stale artifact prevention

## Gold diagnostic-only rule

Gold diagnostic paths must be able to produce classifications and no-trade reasons without:

- market orders
- pending orders
- position modification
- baseline fallback
- `SIGNAL_BUY`
- `SIGNAL_SELL`

## Autonomy rule proposal

Codex may be allowed to handle GitHub + GPT review loops with less user effort, but auto-merge should require explicit standing approval and must be limited to docs-only/research-plan-only PRs with GPT `PASS`.

No auto-merge should happen for code, presets, runner behavior, MT5 execution, backtest results, optimization, or any PR involving trading behavior.

## Next safe step

After GPT review of Checkpoint Y, the next safe checkpoint is:

`Checkpoint Z: Gold No-Trade Diagnostic Execution Approval Pack`

Checkpoint Z should still be approval-only and should not execute MT5.

