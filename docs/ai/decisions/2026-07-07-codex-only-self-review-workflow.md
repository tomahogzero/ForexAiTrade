# Decision: Codex-Only Self-Review Workflow

Date: 2026-07-07

## Decision

ForexAiTrade will use a Codex-first / GPT-optional workflow for low-risk checkpoints.

Codex may self-review and auto-merge documentation-only and runner-plan-only PRs after Checkpoint AF is merged, provided all guardrails pass.

## Motivation

Codex cannot always send repo/private project context to ChatGPT browser because external context export can be blocked.

The project needs a way to continue safely without requiring manual copy/paste for every low-risk documentation checkpoint.

## Allowed Auto-Merge Scope

Allowed after self-review:

- docs-only
- AI memory updates
- research-plan-only
- diagnosis-plan-only
- runner-plan-only documentation

Not allowed by default:

- MQL5 source changes
- preset changes
- runner/script code changes that affect execution safety
- MT5 execution artifacts
- optimization result changes
- risk/lot changes
- profitability claims

## Required Self-Review

Before auto-merge, Codex must verify:

- diff scope
- artifact audit
- no forbidden files
- no MT5 run
- no Strategy Tester run
- no source/preset changes for docs-only tiers
- no optimization
- no risk increase
- no profitability claim

## Escalation

Use `NEEDS_USER_REVIEW` if:

- scope is unclear
- source/preset/script changes exist
- MT5 execution is involved
- policy wording could be interpreted as approving live/demo trading
- Codex is unsure whether a change is low-risk

## Non-Goals

This decision does not approve:

- live trading
- demo forward testing
- MT5 reruns
- strategy optimization
- lot/risk increases
- bypassing RiskManager

