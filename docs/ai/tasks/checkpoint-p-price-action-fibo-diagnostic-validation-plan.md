# Checkpoint P: Price Action / Fibo Diagnostic Validation Plan

Created: 2026-07-01

## Purpose

Checkpoint P prepares a safe validation plan for the merged Checkpoint N Price Action / Fibo diagnostics.

This plan does not run MT5, does not change EA source code, does not change presets, and does not perform optimization.

## Current State

- PR #4 / Checkpoint N diagnostics is merged into `main`.
- PR #5 / Javis Codex project memory is merged into `main`.
- Latest known `origin/main` commit during this planning task: `04dabdea719628a8eae0ab61c477507e68db2a4f`.
- Price Action / Fibo diagnostics are available in source, but they remain diagnostic-only.
- No diagnostic validation run has been approved yet.

## Non-Negotiable Guardrails

- No market orders from Price Action / Fibo.
- No pending orders from Price Action / Fibo.
- No position modification from Price Action / Fibo.
- No optimization.
- No lot/risk increase.
- No profitability claim.
- No demo/live forward test.
- Strategy Tester execution only in a later checkpoint after explicit user approval.

## Validation Goal

The first validation should answer only:

- Does the EA attach/compile/run with Price Action / Fibo diagnostics enabled?
- Are diagnostic summaries logged on new bars without excessive tick-by-tick logging?
- Do classifications remain logging-only?
- Does the module continue to return `SIGNAL_NONE`?
- Are no market orders, pending orders, or position modifications created by Price Action / Fibo?
- Are actual broker symbol and canonical symbol fields still visible in logs?

The first validation must not answer:

- Is the strategy profitable?
- Which parameters are best?
- Should lot size or risk be increased?
- Is demo/live forward testing approved?

## Proposed Later Checkpoint Scope

Checkpoint Q, only if explicitly approved, should be a controlled Strategy Tester sanity run:

- Symbol: EURUSD only
- Timeframe: H1 only
- Period: short diagnostic window first, such as 1 to 3 months
- Mode: Strategy Tester only
- `InpRequireStrategyTester=true`
- `InpLiveTradingEnabled=true` only inside tester preset/config
- `InpDemoSafeMode=true`
- `InpEnablePriceActionFibo=true`
- `InpPriceActionFiboDiagnosticsOnly=true`
- `InpPAFDiagnosticsEnabled=true`
- `InpPAFUsePendingOrders=false`
- `InpPAFMaxPendingOrders=0`
- Existing risk gates remain enabled
- No optimization

## Expected Artifacts For Later Execution

If later approved, collect:

- tester journal excerpt
- EA mirror log
- generated tester config
- effective preset/config
- report file if produced
- explicit no-order confirmation
- diagnostic summary sample

## Pass Criteria For Later Execution

The later diagnostic run passes only if:

- EA runs without compile/runtime errors.
- Price Action / Fibo diagnostic logs are produced.
- No Price Action / Fibo market orders are opened.
- No Price Action / Fibo pending orders are placed.
- No Price Action / Fibo position modifications occur.
- Logs clearly show diagnostic classifications are not trade signals.

## Fail Criteria For Later Execution

The later diagnostic run fails if:

- Any Price Action / Fibo signal becomes `SIGNAL_BUY` or `SIGNAL_SELL`.
- Any pending order is placed by Price Action / Fibo.
- Any market order is opened by Price Action / Fibo.
- Any position is modified by Price Action / Fibo.
- The run requires parameter optimization to appear useful.
- Logs are too noisy to inspect.

## GPT Review Gate

Before any MT5 execution, GPT should review:

- Checkpoint N diagnostic code intent and guardrails.
- This Checkpoint P validation plan.
- Whether additional no-trade assertions or logging checks are needed.

## Next Safe Codex Task

Recommended next task:

1. Ask GPT to review Checkpoint N diagnostics and this plan.
2. Address any documentation-only review findings.
3. Only then propose a separate Checkpoint Q for an explicitly approved no-trade Strategy Tester diagnostic sanity run.
