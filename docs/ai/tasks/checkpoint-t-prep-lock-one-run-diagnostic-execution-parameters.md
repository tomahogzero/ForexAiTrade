# Checkpoint T-Prep: Lock One-Run Diagnostic Execution Parameters

Created: 2026-07-02

## Purpose

Checkpoint T-Prep locks the exact parameters required for a future Checkpoint T one-run Price Action / Fibo no-trade Strategy Tester diagnostic execution.

This checkpoint does not run MT5, does not run Strategy Tester, does not change EA/source code, does not change presets, does not optimize, and does not approve demo/live trading.

## Current Context

- PR #9 / Checkpoint S has been merged.
- GPT Review Agent verdict for PR #9: PASS.
- Checkpoint S prepared a one-run execution approval package.
- Checkpoint T-Prep only locks the parameters that still need final user approval.

## Exact Source Proposed For Future Execution

The future Checkpoint T diagnostic execution, if explicitly approved later, must use:

- Source branch: `main`
- Source commit proposed for execution: `580a1cebf47d7fa86630fc1a51e338a2b07e6066`
- Commit meaning: merge commit for PR #9 / Checkpoint S

Before any future run starts, Codex must confirm the active source exactly matches this branch/commit or explicitly document why a newer reviewed merge commit is being used.

## Locked Execution Parameters

Future run parameters:

- Symbol: EURUSD only
- Timeframe: H1 only
- Date range start: `NEED_USER_APPROVAL`
- Date range end: `NEED_USER_APPROVAL`
- Environment: Strategy Tester only
- Number of runs: one run only
- Optimization: disabled
- Demo/live/forward test: not allowed
- Market orders: not allowed
- Pending orders: not allowed
- Position modification: not allowed
- Lot/risk increase: not allowed
- Profitability interpretation: not allowed

The date range is intentionally not selected in this document because the user has not provided it yet.

## Required User Approval Before Execution

MT5 / Strategy Tester execution remains blocked until the user explicitly sends this exact style of approval:

`Approved to execute Checkpoint T one-run diagnostic with date range YYYY-MM-DD to YYYY-MM-DD`

Without that exact approval intent and concrete date range, do not run MT5.

## Required Effective Config Assertions Before Run

Before any future Checkpoint T run starts, capture and verify the effective config.

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

If any assertion fails or cannot be proven, do not start execution.

## Live Trading Gate Clarification

`InpLiveTradingEnabled=true`, if required inside Strategy Tester to pass internal EA tester gates, is not approval for demo or live chart trading.

Any future Checkpoint T run using `InpLiveTradingEnabled=true` must also prove:

- `InpRequireStrategyTester=true`
- Strategy Tester environment is active
- demo/live/forward environment is not active
- Price Action / Fibo remains diagnostics-only

## Stop Conditions

If the future run is explicitly approved, stop immediately and classify the run as failed if any of these occur:

- config mismatch
- any market order attempt
- any pending order attempt
- any position modification attempt
- baseline strategy fallback
- log too noisy
- optimization enabled
- demo/live/forward environment detected
- date range differs from the explicit approval
- more than one run is attempted

## Forbidden Markers / Checks

The future artifact audit must check for forbidden trade action markers in Strategy Tester logs, EA logs, and generated artifacts where available.

Forbidden markers include:

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

The check must distinguish diagnostic text from actual trade-action attempts. If ambiguous, classify the run as needing manual review and do not treat it as passed.

## Required Artifacts After Future Run

If the user later explicitly approves and the future run is executed, collect:

- RunId
- Strategy Tester report/log path
- effective config snapshot
- forbidden action grep/check summary
- Price Action / Fibo diagnostic classification summary
- no-trade confirmation
- no baseline fallback confirmation

Also record:

- tested branch and commit
- symbol/timeframe/date range
- confirmation optimization was disabled
- confirmation no demo/live/forward environment was used
- whether any stop condition was triggered

## Minimum Pass Criteria For Future Run

The future Checkpoint T run can pass only if:

- source branch/commit is confirmed
- approved date range matches the executed date range
- all effective config assertions match
- Strategy Tester is the only execution environment
- exactly one run is executed
- optimization is disabled
- Price Action / Fibo diagnostic classification summary exists
- no-trade confirmation exists
- forbidden action check is clean
- no market order attempt is found
- no pending order attempt is found
- no position modification attempt is found
- no baseline fallback occurs

## Mandatory Fail Criteria For Future Run

The future Checkpoint T run must fail if:

- source branch/commit cannot be confirmed
- date range is missing or differs from approval
- effective config differs from this parameter lock
- optimization is enabled
- demo/live/forward environment is detected
- any trade action is attempted
- baseline strategy path runs instead of the diagnostic path
- logs are too noisy to audit
- required artifacts are missing
- more than one run is executed

## What Checkpoint T-Prep Does Not Approve

Checkpoint T-Prep does not approve:

- running MT5 now
- running Strategy Tester now
- selecting a date range without user approval
- more than one run
- optimization
- demo/live/forward testing
- market orders
- pending orders
- position modification
- lot/risk increase
- profitability interpretation

## Final Gate

The only remaining approval needed before execution is:

`Approved to execute Checkpoint T one-run diagnostic with date range YYYY-MM-DD to YYYY-MM-DD`

Until that approval is provided, actual MT5 / Strategy Tester execution remains blocked.
