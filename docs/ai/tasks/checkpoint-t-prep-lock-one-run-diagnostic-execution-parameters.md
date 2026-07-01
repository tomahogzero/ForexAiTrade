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
- PR #10 / Checkpoint T-Prep has been merged.
- GPT Review Agent verdict for PR #10: CONDITIONAL PASS.
- This fix resolves the required documentation-only changes from that CONDITIONAL PASS:
  - add a maximum one-month date range bound
  - add a source/preset drift guard before any execution

## Exact Source Proposed For Future Execution

The future Checkpoint T diagnostic execution, if explicitly approved later, must use:

- Source branch: `main`
- Source commit proposed for execution: `580a1cebf47d7fa86630fc1a51e338a2b07e6066`
- Commit meaning: merge commit for PR #9 / Checkpoint S

The proposed execution target remains `580a1cebf47d7fa86630fc1a51e338a2b07e6066` unless explicitly changed by a new reviewed checkpoint.

Before any future run starts, Codex must confirm the active source exactly matches this branch/commit.

## Source / Preset Drift Guard

If a newer commit is used for execution, execution must be blocked unless Codex proves and documents that EA/source code and presets have not changed from the approved target commit.

Required drift checks if a newer commit is proposed:

- compare `MQL5/` against `580a1cebf47d7fa86630fc1a51e338a2b07e6066`
- compare `presets/` against `580a1cebf47d7fa86630fc1a51e338a2b07e6066`
- document the exact diff result before execution
- confirm there are no EA/source code changes
- confirm there are no preset changes

If EA/source code or presets changed, execution must remain blocked.

Any EA/source code or preset drift requires a new GPT review and a new approval checkpoint before execution.

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

## Date Range Bound

The approved date range must remain a short diagnostic window only.

Maximum allowed date range: 1 month.

The approval phrase must include concrete dates in `YYYY-MM-DD to YYYY-MM-DD` format.

If the requested date range is longer than 1 month, execution must be blocked and a new approval checkpoint is required.

If either date is missing, ambiguous, malformed, or not in `YYYY-MM-DD` format, execution must be blocked.

## Required User Approval Before Execution

MT5 / Strategy Tester execution remains blocked until the user explicitly sends this exact style of approval:

`Approved to execute Checkpoint T one-run diagnostic with date range YYYY-MM-DD to YYYY-MM-DD`

Without that exact approval intent and concrete date range, do not run MT5.

The concrete date range in the approval must also pass the one-month maximum bound.

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
- date range is longer than 1 month
- date range is missing, ambiguous, malformed, or not in `YYYY-MM-DD` format
- source commit differs from `580a1cebf47d7fa86630fc1a51e338a2b07e6066` without documented no-drift proof
- EA/source code drift is detected
- preset drift is detected
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
- source/preset drift check result if the execution commit differs from `580a1cebf47d7fa86630fc1a51e338a2b07e6066`
- symbol/timeframe/date range
- confirmation optimization was disabled
- confirmation no demo/live/forward environment was used
- whether any stop condition was triggered

## Minimum Pass Criteria For Future Run

The future Checkpoint T run can pass only if:

- source branch/commit is confirmed
- approved date range matches the executed date range
- approved date range is no longer than 1 month
- approved date range uses concrete `YYYY-MM-DD to YYYY-MM-DD` dates
- source/preset drift guard passes if a newer commit is used
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
- date range is longer than 1 month
- date range is ambiguous, malformed, or not in `YYYY-MM-DD` format
- source/preset drift guard is missing when a newer commit is used
- EA/source code drift is detected
- preset drift is detected
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
