# Checkpoint DA: PAF Data Collection Expansion Approval

## Purpose

Create an approval package for a future Checkpoint DB diagnostic-only data collection expansion.

Checkpoint CZ showed that the no-trade PAF diagnostic pipeline works, but combined CV + CY usable direction rows are still too low:

- total diagnostic rows: 274
- possible setup rows: 91
- usable direction rows: 63
- diagnostic interpretation gate: 100 usable rows
- rule-candidate gate: 300 usable rows

## Scope

This checkpoint is documentation and approval planning only.

Do not run MT5.
Do not run Strategy Tester.
Do not change EA/source code.
Do not change presets.
Do not optimize.
Do not increase lot/risk.
Do not claim profitability.
Do not approve demo/live trading.

## Future Checkpoint DB Proposed Run

Future DB, if separately approved, should run diagnostic-only Strategy Tester windows:

- Symbol: GOLD#
- Timeframe: H1
- Runner/parser: official AK workflow
- Strategy Tester only
- No optimization
- No demo/live/forward test
- No market orders
- No pending orders
- No position modification
- No lot/risk increase
- No profitability interpretation

Proposed windows:

1. 2026-03-29 to 2026-04-05
2. 2026-04-05 to 2026-04-12
3. 2026-04-12 to 2026-04-19
4. 2026-04-19 to 2026-04-26

## Required Future Effective Config Assertions

- InpEnablePriceActionFibo=true
- InpPriceActionFiboDiagnosticsOnly=true
- InpPAFUsePendingOrders=false
- InpPAFMaxPendingOrders=0
- InpManageExistingPositions=false
- InpRequireStrategyTester=true
- InpPAFLogOnlyOnNewBar=true
- Optimization disabled
- Strategy Tester only
- Actual runtime symbol is GOLD#

## Stop Conditions

Future DB must stop immediately on:

- config mismatch
- market order attempt
- pending order attempt
- position modification attempt
- baseline strategy fallback
- optimization enabled
- demo/live/forward environment detected
- missing report/log artifacts
- stale artifact reuse
- forbidden action marker
- symbol/timeframe/date mismatch

## Required Future Artifacts

For each window:

- RunId
- case folder
- status.json
- generated_tester.ini
- effective_preset.set
- effective config snapshot
- runner.log
- Strategy Tester report
- tester log excerpt
- ea_mirror.log
- parsed report/result
- PAF diagnostic parser output
- forbidden action grep/check summary
- no-trade confirmation
- no-baseline-fallback confirmation

## Future Review After DB

After DB, a separate artifact-review checkpoint should aggregate CV + CY + DB and decide:

- whether usable direction rows reached 100
- whether distribution is stable enough for diagnostic interpretation
- whether any window produced forbidden actions or baseline fallback
- whether PAF remains blocked from order logic

Even if usable direction rows reach 100, order logic remains blocked until much stronger evidence and separate reviewed approval exist.

## Approval Phrase

Future DB remains blocked until the user provides:

`Approved to execute Checkpoint DB PAF diagnostic data collection expansion with symbol GOLD# timeframe H1 windows 2026-03-29 to 2026-04-05, 2026-04-05 to 2026-04-12, 2026-04-12 to 2026-04-19, and 2026-04-19 to 2026-04-26 using official AK runner/parser workflow.`

## Status

Checkpoint DA creates the approval package only. It does not execute DB.
