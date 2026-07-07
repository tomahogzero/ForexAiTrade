# Checkpoint AW: PAF Diagnostic Field Verification Approval

## Status

Completed as an approval-package-only checkpoint.

## Scope

Checkpoint AW defines the future one-run Strategy Tester diagnostic required to verify that Checkpoint AV diagnostic fields appear in `ea_mirror.log`.

No execution is performed in Checkpoint AW.

## Proposed Future Run

- Symbol: `GOLD#`
- Timeframe: `H1`
- Date range: `2026-03-01` to `2026-03-08`
- Runs: exactly one
- Strategy Tester only
- Optimization disabled
- No demo/live/forward test
- No market orders
- No pending orders
- No position modification
- No lot/risk increase
- No profitability interpretation

## Required Effective Config

- `InpEnablePriceActionFibo=true`
- `InpPriceActionFiboDiagnosticsOnly=true`
- `InpPAFUsePendingOrders=false`
- `InpPAFMaxPendingOrders=0`
- `InpManageExistingPositions=false`
- `InpRequireStrategyTester=true`
- `InpPAFLogOnlyOnNewBar=true`
- Optimization disabled
- Strategy Tester only
- No existing/open position in tester context

## Required Field Checks

The future run must confirm these fields appear in `ea_mirror.log`:

- `direction_context=`
- `direction_reason=`
- `entry_reference_price=`
- `bar_open=`
- `bar_high=`
- `bar_low=`
- `bar_close=`
- `atr=`
- `ema_fast=`
- `ema_slow=`
- `bb_width_percent=`

## Required Approval Phrase

```text
Approved to execute Checkpoint AX one-run PAF diagnostic field verification with symbol GOLD# timeframe H1 date range 2026-03-01 to 2026-03-08 using official AK runner/parser workflow.
```

## Decision

`PAF_FIELD_VERIFICATION_APPROVAL_PACKAGE_CREATED`

`EXECUTION_STILL_BLOCKED_UNTIL_USER_APPROVAL`

`ORDER_PATH_STILL_BLOCKED`

`NO_OPTIMIZATION_APPROVED`

`NO_PROFITABILITY_CLAIM`

## Next Safe Step

After PR #40 is merged and the exact approval phrase is provided, Checkpoint AX may execute exactly one no-trade diagnostic field verification run.

