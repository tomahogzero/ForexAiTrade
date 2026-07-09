# Checkpoint CO: PAF Direction Context Diagnostic Validation Approval

## Purpose

Define a safe approval package for a future one-run diagnostic validation of the Checkpoint CN `paf_*` direction context fields.

## Current Context

- Checkpoint CN is merged.
- CN implemented diagnostics-only MQL5 fields and parser compatibility.
- CN compile result was `0 errors, 0 warnings`.
- CN did not run MT5 / Strategy Tester.
- Direction completeness improvement is not proven yet.

## Future CP Scope

Future Checkpoint CP may run exactly one Strategy Tester diagnostic validation only after explicit user approval.

Constraints:

- Symbol: `GOLD#` only unless explicitly changed.
- Timeframe: `H1` only.
- Date range: short diagnostic window, maximum 1 month.
- Strategy Tester only.
- No optimization.
- No demo/live/forward test.
- No market orders.
- No pending orders.
- No position modification.
- No lot/risk increase.
- No profitability interpretation.

## Required Config Assertions

- `InpEnablePriceActionFibo=true`
- `InpPriceActionFiboDiagnosticsOnly=true`
- `InpPAFUsePendingOrders=false`
- `InpPAFMaxPendingOrders=0`
- `InpManageExistingPositions=false`
- `InpRequireStrategyTester=true`
- `InpPAFLogOnlyOnNewBar=true`
- Optimization disabled.
- Strategy Tester only.
- No existing/open position in tester context.

## Required Evidence

Future CP must prove:

- CN fields appear in EA mirror log.
- Parser reads CN fields.
- No forbidden trade actions appear.
- No baseline fallback appears.
- Direction completeness can be re-audited.

## Result of Checkpoint CO

Documentation / approval package only.

No execution is approved by this file alone.

Execution remains blocked until the exact approval phrase is provided by the user.
