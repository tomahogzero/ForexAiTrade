# Checkpoint AF: Codex-Only Self-Review Workflow

Created: 2026-07-07

## Purpose

Define a Codex-first workflow so low-risk documentation and planning PRs can be reviewed and merged by Codex without sending project context to an external GPT browser.

This checkpoint is documentation only.

It does not run MT5, does not run Strategy Tester, does not spawn `terminal64.exe`, does not change EA/source code, does not change presets, does not optimize, does not increase lot/risk, and does not claim profitability.

## Why This Is Needed

The user wants Codex to handle more repository work without manual copy/paste into GPT.

Attempts to send repository-specific review prompts into ChatGPT browser from Codex can be blocked by tenant policy because that exports private project context to an external destination.

Therefore, safe low-risk work should use Codex self-review instead of GPT browser review.

## Codex Logical Agent Roles

These are workflow roles inside Codex, not separate external services.

### Builder

- Creates isolated worktree from `origin/main`
- Makes scoped changes
- Does not modify unrelated files
- Does not run MT5 unless explicitly approved

### Safety Reviewer

- Reviews changed files
- Checks guardrails
- Confirms artifact audit
- Confirms no source/preset/risk/MT5 changes for docs-only PRs

### Release Manager

- Stages explicit files only
- Commits
- Pushes branch
- Opens PR
- Merges only if self-review rules allow it

## Auto-Merge Eligibility

Codex may auto-merge after `CODEX_SELF_REVIEW_PASS` only when all are true:

- docs-only or research-plan-only
- no `MQL5/` changes
- no `presets/` changes
- no runner/script/tool code changes
- no MT5 run
- no Strategy Tester run
- no terminal spawn
- no optimization
- no lot/risk increase
- no profitability claim
- no forbidden artifacts
- PR body documents guardrails

## Not Eligible For Auto-Merge

User review or explicit approval is still required for:

- MQL5 source changes
- presets changes
- runner/script/tool implementation changes
- compile-required changes
- MT5 execution or Strategy Tester execution
- execution result reporting
- optimization
- risk/lot changes
- demo/live/forward test approval
- any ambiguous scope

## Required Codex Self-Review Output

Before auto-merge, Codex final status must include:

```text
Codex self-review: CODEX_SELF_REVIEW_PASS / NEEDS_USER_REVIEW / NEEDS_FIX / BLOCKED_BY_GUARDRAIL
Docs-only: yes/no
Source/preset changes: yes/no
MT5 run: yes/no
Optimization/risk/profit claim: yes/no
Artifact audit: PASS/FAIL
Auto-merge eligible: yes/no
```

## Current Recommended Next Step

After this checkpoint is reviewed and merged, future low-risk docs-only planning PRs can use Codex-only self-review without requiring GPT browser review.

Checkpoint AF itself should not be used as proof that code/risk/execution PRs can be auto-merged.

