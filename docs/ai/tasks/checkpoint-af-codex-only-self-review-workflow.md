# Checkpoint AF: Codex-Only Self-Review Workflow

Created: 2026-07-07

## Purpose

Create a Codex-only self-review workflow so low-risk documentation and planning checkpoints can proceed without requiring GPT browser review.

This checkpoint is documentation only.

It does not run MT5, does not run Strategy Tester, does not spawn `terminal64.exe`, does not change EA/source code, does not change presets, does not optimize, does not increase lot/risk, and does not claim profitability.

## Background

The project previously used GPT review for many documentation checkpoints.

Codex cannot reliably send repo/private project context to ChatGPT browser because the environment can block external context export.

The user asked whether Codex can work 100% independently by using separate agent roles.

Checkpoint AF defines Codex-first / GPT-optional workflow:

- Codex self-review for low-risk docs/plans
- GPT optional only when needed
- user approval still required for MT5 execution
- no relaxation of trading safety guardrails

## Logical Agent Roles

Codex uses logical roles in one workflow:

- Builder: implements scoped checkpoint work
- Reviewer: audits diff, artifacts, wording, and guardrails
- Release: stages, commits, opens PR, and merges only if policy allows

These roles are process discipline, not a permission to bypass guardrails.

## Merge Tiers

### Tier 0: Docs / Memory / Research Plan Only

Allowed for Codex self-review and auto-merge after this checkpoint is merged.

Scope examples:

- `docs/`
- `docs/ai/`
- research idea documents
- checkpoint status documents
- GPT request documents

Must not include:

- `MQL5/`
- `presets/`
- `scripts/`
- `tools/`
- MT5 run artifacts
- optimization
- risk increase
- profitability claim

### Tier 1: Runner / Tool Plan Only

Allowed for Codex self-review and auto-merge if documentation-only.

Examples:

- runner plan docs
- artifact path plan docs
- diagnosis docs

### Tier 2: Script / Tool / Runner Code Change

Codex may implement and self-review, but auto-merge requires explicit checkpoint permission or future policy expansion.

Requires safety checks:

- no MT5 run
- no terminal spawn unless explicitly approved
- no broad terminal kill
- runner stops only the PID it starts
- syntax checks where appropriate

### Tier 3: MQL5 Source Change

No default auto-merge.

Requires explicit checkpoint scope and compile verification when possible.

### Tier 4: Preset Change

No default auto-merge if risk/trading behavior can change.

Requires explicit review.

### Tier 5: MT5 / Strategy Tester Execution

Never automatic.

Requires explicit user approval phrase with symbol, timeframe, date range, and artifact path constraints.

## Self-Review Checklist

Before Codex auto-merges Tier 0 or Tier 1:

1. Confirm branch is based on latest `origin/main`.
2. Confirm changed files are allowed for the tier.
3. Confirm no `MQL5/`, `presets/`, `scripts/`, or `tools/` changes for docs-only auto-merge.
4. Confirm no forbidden artifacts:
   - `.ex5`
   - `.pyc`
   - `__pycache__/`
   - `.zip`
   - `.agents/`
   - temp/cache/log files
5. Confirm no MT5/Strategy Tester execution occurred.
6. Confirm no optimization was performed.
7. Confirm no lot/risk increase.
8. Confirm no profitability claim.
9. Confirm no demo/live approval.
10. Confirm current status and task docs remain consistent.

## Release Behavior

For Tier 0 and Tier 1 after self-review passes:

1. Open Draft PR.
2. Record self-review in final response.
3. Mark PR ready only when auto-merge criteria are satisfied.
4. Merge PR.
5. Fetch `origin/main` and confirm merge commit.

If any condition is unclear:

`NEEDS_USER_REVIEW`

## Current Project Impact

This workflow does not approve:

- Checkpoint AC retry
- Checkpoint AF runner code changes
- MT5 execution
- Strategy Tester execution
- live/demo forward testing
- strategy implementation
- risk changes

The next technical checkpoint remains likely:

`Checkpoint AG: MT5 report path runner-only hardening`

or another name chosen by the user.

## Guardrail Summary

Codex-only does not mean uncontrolled.

It means Codex can handle low-risk repository workflow autonomously while keeping MT5 execution, source changes, preset changes, and risk-sensitive changes behind stricter gates.

