# Decision: Codex-Only Self-Review Workflow

Date: 2026-07-07

## Decision

ForexAiTrade may use Codex-only self-review for low-risk documentation and planning PRs.

Codex may auto-merge only when the PR is clearly docs-only or research-plan-only and passes the Codex self-review checklist.

## Reason

The user wants less manual copy/paste to GPT.

Codex cannot reliably send private repository context to ChatGPT browser because tenant policy may block external export of project context.

Using Codex-only self-review for low-risk work keeps the project moving while preserving guardrails.

## Boundaries

Codex-only auto-merge does not apply to:

- MQL5 source changes
- preset changes
- runner/script/tool implementation changes
- MT5 execution
- Strategy Tester execution
- optimization
- risk/lot changes
- live/demo/forward approval
- execution result interpretation

## Required Label

Codex must report one of:

- `CODEX_SELF_REVIEW_PASS`
- `NEEDS_USER_REVIEW`
- `NEEDS_FIX`
- `BLOCKED_BY_GUARDRAIL`

## Safety Principle

When uncertain, do not auto-merge.

