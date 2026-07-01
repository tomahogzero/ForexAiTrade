# Checkpoint R: Explicit No-Trade Strategy Tester Diagnostic Run Approval Pack

Created: 2026-07-02

## Purpose

Checkpoint R prepares an approval pack for a future Price Action / Fibo diagnostic sanity run.

This checkpoint does not run MT5, does not run Strategy Tester, does not change EA/source code, does not change presets, does not optimize, and does not approve demo/live trading.

## Approval Boundary

This document is not an execution instruction.

Actual MT5 / Strategy Tester execution remains blocked until the user gives a separate explicit approval after Checkpoint R review.

## Future Diagnostic Run Scope

The future run, if separately approved later, must remain very narrow:

- Symbol: EURUSD
- Timeframe: H1
- Period: short diagnostic window only
- Environment: Strategy Tester only
- Optimization: disabled
- Demo/live/forward test: not allowed
- Market orders: not allowed
- Pending orders: not allowed
- Position modification: not allowed
- Lot/risk increase: not allowed
- Profitability claim: not allowed

## Required Pre-Run Effective Config Assertions

Before any later run starts, the effective configuration must be captured and verified.

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

If any assertion fails or cannot be verified, the run must not start.

## Live Trading Gate Clarification

`InpLiveTradingEnabled=true`, if used later in Strategy Tester, is only to pass the EA internal tester gate.

It is not approval for:

- demo chart trading
- live chart trading
- forward testing
- market orders
- pending orders
- position modification

For this diagnostic path, any configuration using `InpLiveTradingEnabled=true` must also require `InpRequireStrategyTester=true`.

## Diagnostic Classification Rule

Diagnostic classifications are observation labels only.

They must not be treated as:

- `SIGNAL_BUY`
- `SIGNAL_SELL`
- market entry approval
- pending order approval
- position management approval
- proof of profitability

## Run Stop Conditions

If a later run is approved, stop immediately and classify the run as failed if any of these conditions occur:

- effective config mismatch
- any market order attempt
- any pending order attempt
- any position modification attempt
- baseline strategy fallback
- log too noisy because `InpPAFLogOnlyOnNewBar` is not effective
- any optimization setting enabled
- any demo/live environment detected

Forbidden trade-action markers to inspect include:

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

## Required Post-Run Artifacts For Future Execution

If execution is separately approved later, the resulting artifact package must include:

- Strategy Tester report/log path
- RunId
- effective config snapshot
- grep/check summary for forbidden trade actions
- diagnostic classification summary
- no-trade confirmation
- confirmation that no pending order was placed
- confirmation that no position modification occurred
- confirmation that baseline strategy did not replace the Price Action / Fibo diagnostic path

## Minimum Pass Criteria For Future Execution

A later diagnostic run can pass only if:

- effective config matches every required assertion
- Price Action / Fibo diagnostic summary exists
- `classification=` appears in diagnostic output
- a no-trade reason appears
- no market order attempt is found
- no pending order attempt is found
- no position modification attempt is found
- no `SIGNAL_BUY` / `SIGNAL_SELL` is emitted from the Price Action / Fibo path
- no fallback to baseline strategy occurs
- diagnostic logs are readable and not tick-noisy

## Mandatory Fail Criteria For Future Execution

A later diagnostic run must fail if:

- config assertions differ from the approved checklist
- Strategy Tester is not the execution environment
- optimization is enabled
- a demo/live environment is detected
- any order or position-management action is attempted
- diagnostic output is too noisy to review
- baseline strategy executes instead of the diagnostic path

## What This Checkpoint Does Not Approve

Checkpoint R does not approve:

- running MT5 now
- running Strategy Tester now
- optimization
- demo/live forward testing
- market orders
- pending orders
- position modification
- lot/risk increase
- profitability claims

## Next Gate

After Checkpoint R is reviewed, the next possible step is a separate explicit user approval for a no-trade Strategy Tester diagnostic execution.

Without that explicit approval, MT5 execution remains blocked.
