# Checkpoint AL: PAF Diagnostic One-Run Approval Package

## Objective

Prepare a narrow approval package for a future one-run Price Action/Fibo diagnostic execution using the official Checkpoint AK runner/parser workflow.

## Scope

This checkpoint is documentation and approval planning only.

In scope:

- Define the proposed future source target.
- Define exact future diagnostic constraints.
- Define required pre-run config assertions.
- Define stop conditions.
- Define required post-run artifacts.
- Define the exact user approval phrase for a later execution checkpoint.

Out of scope:

- MT5 execution.
- Strategy Tester execution.
- Source/EA changes.
- Preset changes.
- Trading logic changes.
- Optimization.
- Lot/risk increase.
- Profitability interpretation.

## Proposed Future Execution

- Symbol: `GOLD#` only
- Timeframe: `H1` only
- Date range: `NEED_USER_APPROVAL`
- Maximum date range: 1 month
- Strategy Tester only
- One run only
- No optimization
- No market orders
- No pending orders
- No position modification
- No demo/live/forward test

## Approval Phrase Required Later

```text
Approved to execute Checkpoint AM one-run PAF diagnostic with symbol GOLD# timeframe H1 date range YYYY-MM-DD to YYYY-MM-DD using official AK runner/parser workflow.
```

## Source / Preset Drift Guard

The proposed future execution target is `main` at commit `621463d056d559a5c4cdc05a6175d70bb0a73430`, based on PR #29 / Checkpoint AK.

If a newer commit is used, Codex must prove and document that EA/source code and presets have not changed from the approved target. If they changed, execution is blocked until a new reviewed checkpoint.

## Required Config Assertions

- `InpLiveTradingEnabled=true`
- `InpDemoSafeMode=true`
- `InpRequireStrategyTester=true`
- `InpEnablePriceActionFibo=true`
- `InpPriceActionFiboDiagnosticsOnly=true`
- `InpPAFUsePendingOrders=false`
- `InpPAFMaxPendingOrders=0`
- `InpPAFLogOnlyOnNewBar=true`
- `InpManageExistingPositions=false`
- `InpAllowedSymbolsCsv=GOLD#`
- `InpCanonicalSymbolName=GOLD`
- `InpBrokerGoldSymbolName=GOLD#`

`InpLiveTradingEnabled=true` is allowed only inside Strategy Tester to pass internal tester gates. It is not demo/live approval.

## Required Artifacts

- RunId
- generated tester config
- effective config snapshot
- process info
- runner log
- MT5 report
- EA mirror log
- tester log excerpt
- PAF diagnostics JSON/Markdown
- aggregate PAF diagnostics CSV/Markdown
- forbidden marker check
- no-trade confirmation
- no baseline fallback confirmation

## Final Status

Checkpoint AL does not approve execution. Execution remains blocked until a later explicit Checkpoint AM user approval phrase is provided.
