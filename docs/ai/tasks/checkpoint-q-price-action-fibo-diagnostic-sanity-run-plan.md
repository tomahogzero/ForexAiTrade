# Checkpoint Q: Price Action / Fibo Diagnostic Sanity Run Plan

Created: 2026-07-01

## Purpose

Checkpoint Q prepares a pre-run safety checklist for a future Price Action / Fibo diagnostic sanity run.

This checkpoint does not run MT5, does not run Strategy Tester, does not change EA/source code, does not change presets, and does not optimize parameters.

## Current Approval Boundary

This document only prepares the checklist for a later explicit Strategy Tester run.

Strategy Tester execution remains blocked until the user explicitly approves it in a later task.

## Diagnostic-Only Rule

Price Action / Fibo classifications are observation labels only.

They are not:

- market entry signals
- pending order instructions
- position modification instructions
- proof of profitability
- approval for demo/live forward testing

## Required Pre-Run Config Assertions

Before any later Strategy Tester diagnostic run starts, the effective configuration must be verified and recorded.

Required assertions:

- `InpEnablePriceActionFibo=true`
- `InpPriceActionFiboDiagnosticsOnly=true`
- `InpPAFUsePendingOrders=false`
- `InpPAFMaxPendingOrders=0`
- `InpManageExistingPositions=false`
- `InpRequireStrategyTester=true`
- `InpPAFLogOnlyOnNewBar=true`
- no existing/open position in tester context
- Strategy Tester only

If any assertion fails, do not run the test.

## Live Trading Gate Clarification

`InpLiveTradingEnabled=true`, if used in Strategy Tester, is only to pass the EA internal tester gate.

It is not approval for:

- demo chart trading
- live chart trading
- forward testing
- market orders
- pending orders
- position modification

Any config with `InpLiveTradingEnabled=true` must also require `InpRequireStrategyTester=true` for this diagnostic path.

## No-Trade Requirements

The future sanity run must not allow:

- market orders
- pending orders
- position modification
- fallback to baseline strategy trading
- `SIGNAL_BUY` or `SIGNAL_SELL` from the Price Action / Fibo path
- optimization
- lot/risk increase

## Suggested Later Run Scope

Use the smallest practical Strategy Tester diagnostic window first.

Suggested later scope, only after explicit approval:

- Symbol: EURUSD
- Timeframe: H1
- Period: short diagnostic period, such as 1 to 3 months
- Mode: Strategy Tester only
- Purpose: verify diagnostic logging and no-trade behavior

This is not an optimization run and must not be interpreted as a performance test.

## Required Artifacts For Later Run

If a later run is approved, collect:

- effective config / generated tester config
- tester journal excerpt
- EA mirror log if available
- Price Action / Fibo diagnostic summary
- explicit no-order confirmation
- confirmation that baseline strategy did not run instead of the diagnostic path

## Pass Criteria

The later diagnostic sanity run passes only if all of these are true:

- PriceActionFibo diagnostic summary exists.
- `classification=` exists in diagnostic logs or summary.
- no-trade reason exists.
- no market order occurs.
- no pending order occurs.
- no position modification occurs.
- no `SIGNAL_BUY` or `SIGNAL_SELL` is emitted from the Price Action / Fibo path.
- no fallback to baseline strategy occurs.
- diagnostics are inspectable and not tick-noisy.

## Fail Criteria

The later diagnostic sanity run fails if any of these occur:

- effective config differs from diagnostic-only settings.
- log is too noisy because `InpPAFLogOnlyOnNewBar` is not enabled.
- baseline strategy runs instead of the Price Action / Fibo diagnostic path.
- any `OrderSend` appears.
- any `Buy` appears as an executed trade action.
- any `Sell` appears as an executed trade action.
- any `BuyLimit` appears.
- any `SellLimit` appears.
- any `BuyStop` appears.
- any `SellStop` appears.
- any `PositionModify` appears.
- any Price Action / Fibo path returns `SIGNAL_BUY` or `SIGNAL_SELL`.

## Manual Pre-Run Checklist

Before running a later Checkpoint Q Strategy Tester sanity run:

1. Confirm the branch and commit to test.
2. Confirm there are no source or preset changes outside the approved checkpoint.
3. Confirm the effective tester config matches every required assertion above.
4. Confirm Strategy Tester is selected.
5. Confirm no existing/open position exists in the tester context.
6. Confirm no optimization mode is enabled.
7. Confirm diagnostic logs are expected on new bars only.
8. Confirm the purpose is no-trade validation, not profitability.

## Stop Conditions

Stop immediately and classify the later run as failed if:

- an order is opened
- a pending order is placed
- a position is modified
- baseline strategy trading path is active
- diagnostics are too noisy to inspect
- any config assertion cannot be verified

## Next Safe Step

Review this plan before any MT5 execution.

Only after explicit approval should Codex run a separate diagnostic Strategy Tester task using this checklist.
