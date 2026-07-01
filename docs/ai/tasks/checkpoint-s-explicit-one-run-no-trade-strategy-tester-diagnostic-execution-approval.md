# Checkpoint S: Explicit One-Run No-Trade Strategy Tester Diagnostic Execution Approval

Created: 2026-07-02

## Purpose

Checkpoint S prepares an explicit approval package for one future Price Action / Fibo no-trade Strategy Tester diagnostic execution.

This checkpoint does not execute MT5, does not run Strategy Tester, does not change EA/source code, does not change presets, does not optimize, and does not approve demo/live trading.

## Current Context

- PR #8 / Checkpoint R has been merged.
- GPT Review Agent verdict for PR #8: PASS.
- Checkpoint R defined the approval-pack guardrails for a future no-trade diagnostic run.
- Actual execution remains blocked until the user gives a separate explicit approval after Checkpoint S review.

## Exact Proposed Execution Target

The future diagnostic execution, if separately approved later, should use the checked-in EA source from:

- Branch: `main`
- Source commit proposed for execution: `cd1b5118e4c443d240f63553abcabce18f2a0982`
- Commit meaning: merge commit for PR #8 / Checkpoint R

Checkpoint S itself is documentation-only. If Checkpoint S is later merged before execution, the runner must confirm that EA/source code and presets are unchanged from the proposed source commit before executing.

## One-Run Scope

The future diagnostic execution must be exactly one narrow run:

- Symbol: EURUSD only
- Timeframe: H1 only
- Period: short diagnostic window only
- Environment: Strategy Tester only
- Number of runs: one
- Optimization: disabled
- Demo/live/forward test: not allowed
- Market orders: not allowed
- Pending orders: not allowed
- Position modification: not allowed
- Lot/risk increase: not allowed
- Profitability interpretation: not allowed

The run is for diagnostic safety validation only.

## Required Pre-Run Effective Config Assertions

Before the future run starts, the effective config snapshot must be captured and checked.

Required assertions:

- `InpEnablePriceActionFibo=true`
- `InpPriceActionFiboDiagnosticsOnly=true`
- `InpPAFUsePendingOrders=false`
- `InpPAFMaxPendingOrders=0`
- `InpManageExistingPositions=false`
- `InpRequireStrategyTester=true`
- `InpPAFLogOnlyOnNewBar=true`
- no existing/open position in tester context
- optimization disabled
- Strategy Tester only

If any assertion fails or cannot be proven from the effective config, execution must not start.

## Live Trading Gate Clarification

`InpLiveTradingEnabled=true`, if required later inside Strategy Tester to pass internal EA tester gates, is not approval for demo or live chart trading.

Any later execution that uses `InpLiveTradingEnabled=true` must also prove:

- `InpRequireStrategyTester=true`
- Strategy Tester environment is active
- demo/live/forward environment is not active
- Price Action / Fibo remains diagnostics-only

## Diagnostic Classification Rule

Price Action / Fibo diagnostic classifications are observation labels.

They are not:

- entry signals
- `SIGNAL_BUY`
- `SIGNAL_SELL`
- pending order instructions
- position management instructions
- approval to trade
- proof of profitability

## Explicit Stop Conditions

If a later run is separately approved, stop immediately and classify the run as failed if any of these conditions occur:

- config mismatch
- any market order attempt
- any pending order attempt
- any position modification attempt
- baseline strategy fallback
- log too noisy
- optimization enabled
- demo/live/forward environment detected

Forbidden trade-action markers to check include:

- `OrderSend`
- `Buy`
- `Sell`
- `BuyLimit`
- `SellLimit`
- `BuyStop`
- `SellStop`
- `PositionModify`
- `SIGNAL_BUY`
- `SIGNAL_SELL`

## Required Artifacts After Future Run

If the future run is separately approved and executed, the artifact package must include:

- RunId
- Strategy Tester report/log path
- effective config snapshot
- forbidden action grep/check summary
- Price Action / Fibo diagnostic classification summary
- no-trade confirmation
- no baseline fallback confirmation

The artifact package should also record:

- tested branch and commit
- Strategy Tester symbol/timeframe/period
- whether optimization was disabled
- whether any stop condition was triggered

## Minimum Pass Criteria

The future one-run diagnostic can pass only if:

- exact branch/commit is confirmed before execution
- all effective config assertions match
- Strategy Tester is the only execution environment
- optimization is disabled
- Price Action / Fibo diagnostic output exists
- diagnostic classification summary exists
- no-trade reason exists
- forbidden action grep/check summary is clean
- no market order attempt is found
- no pending order attempt is found
- no position modification attempt is found
- no baseline fallback occurs

## Mandatory Fail Criteria

The future one-run diagnostic must fail if:

- branch/commit cannot be confirmed
- effective config differs from this approval package
- optimization is enabled
- demo/live/forward environment is detected
- any trade action is attempted
- baseline strategy path runs instead of the diagnostic path
- logs are too noisy to audit
- required artifacts are missing

## What Checkpoint S Does Not Approve

Checkpoint S does not approve:

- running MT5 now
- running Strategy Tester now
- more than one run
- optimization
- demo/live/forward testing
- market orders
- pending orders
- position modification
- lot/risk increase
- profitability interpretation

## Next Gate

After Checkpoint S is reviewed, the user may separately approve one no-trade Strategy Tester diagnostic execution.

Until that explicit approval is given, actual execution remains blocked.
