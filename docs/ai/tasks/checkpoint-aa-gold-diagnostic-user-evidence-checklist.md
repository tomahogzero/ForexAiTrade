# Checkpoint AA: Gold Diagnostic User Evidence Checklist

Created: 2026-07-04

## Purpose

Create a user-facing evidence checklist before any future Gold no-trade Strategy Tester diagnostic execution can be approved.

This checkpoint exists because Checkpoint T failed with `FAILED_NO_TESTER_ARTIFACTS / INCONCLUSIVE`, while manual MT5 Strategy Tester behavior only proved that manual testing can work in one context. It did not prove automated `/config` handoff, Gold H1 availability, no-trade behavior, or absence of baseline fallback.

## Scope

Documentation / preflight checklist only.

- no EA/source code changes
- no preset changes
- no runner changes
- no MT5 run
- no Strategy Tester run
- no terminal64.exe spawn
- no optimization
- no lot/risk increase
- no profitability claim
- no demo/live approval

## Required Evidence Before Any Future Retry Approval

### Terminal Evidence

- exact `terminal64.exe` path
- MT5 Data Folder path from `File > Open Data Folder`
- confirmation whether portable mode is used
- confirmation whether another MT5 instance is already running
- confirmation that the manual terminal is the same terminal intended for retry, or an explanation of the difference

### Symbol / History Evidence

- actual XM Gold symbol selected explicitly: `GOLD#` or `GOLDm#`
- screenshot or note showing the symbol in Market Watch
- H1 history availability for the proposed future date range
- proposed future date range must be concrete and <= 1 month

### Artifact Path Evidence

- absolute report output folder
- pre-created report folder
- write marker file in the report folder
- expected Strategy Tester report path
- expected terminal log folder
- expected tester agent log folder
- expected EA/mirror log folder
- stale artifact inventory before the run

### Source / Preset Drift Evidence

- exact reviewed source branch
- exact reviewed commit
- proof that `MQL5/` has not changed from the reviewed target
- proof that `presets/` has not changed from the reviewed target

If source or presets changed, execution must remain blocked until a new GPT review and approval checkpoint.

## Future Effective Config Assertions

A later execution checkpoint must prove an effective config snapshot before the run:

- Strategy Tester only
- optimization disabled
- `InpRequireStrategyTester=true`
- diagnostic path enabled
- no market orders
- no pending orders
- no position modification
- no baseline fallback
- no-trade reason/classification logging enabled

## Stop Conditions

Block any future retry if:

- terminal path unknown
- data folder unknown
- report folder not writable
- report/log paths are not absolute
- Gold symbol not verified
- H1 history unavailable
- date range longer than 1 month
- effective config mismatch
- optimization enabled
- existing/open position is present in tester context
- baseline strategy fallback cannot be excluded
- forbidden trade action appears
- artifact paths are missing or stale artifacts cannot be separated

Missing required artifacts after a future run must remain `FAILED_NO_TESTER_ARTIFACTS / INCONCLUSIVE`.

## User Evidence Packet

Before the next approval checkpoint, ask the user for:

- terminal path
- Data Folder path
- verified Gold symbol
- H1 history confirmation
- desired absolute report folder
- confirmation whether other MT5 instances are running
- concrete diagnostic date range, not longer than 1 month

## Next Safe Checkpoint

Checkpoint AB may convert the evidence into a narrow one-run execution approval package only after this checklist is reviewed.

Actual MT5 execution remains blocked until explicit approval with concrete symbol, timeframe, date range, and verified artifact paths.

