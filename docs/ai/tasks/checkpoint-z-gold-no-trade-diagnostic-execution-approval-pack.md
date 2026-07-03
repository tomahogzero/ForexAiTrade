# Checkpoint Z: Gold No-Trade Diagnostic Execution Approval Pack

Created: 2026-07-04

## Purpose

Prepare an approval-only pack for a future one-run Gold no-trade diagnostic Strategy Tester execution.

Checkpoint Z does not execute MT5.

## Scope

Documentation only:

- no EA/source code changes
- no preset changes
- no runner changes
- no MT5 run
- no Strategy Tester run
- no optimization
- no lot/risk increase
- no profitability claim

## Proposed future run

- Symbol: `GOLD#` if verified as the actual XM symbol
- Alternate: `GOLDm#` only if verified
- Timeframe: H1
- Date range: not set in this checkpoint
- Maximum future date range: 1 month
- One run only
- Strategy Tester only
- Diagnostic/no-trade only

## Required future approval phrase

`Approved to execute Checkpoint Z Gold no-trade diagnostic with symbol GOLD# timeframe H1 date range YYYY-MM-DD to YYYY-MM-DD using verified artifact paths.`

## Must be proven before future execution

- exact source branch and commit
- no `MQL5/` or `presets/` drift from reviewed target
- exact terminal path
- exact data folder
- absolute report path
- writable report folder marker
- terminal log folder
- tester log folder
- EA/mirror log folder
- stale artifact inventory
- actual Gold symbol availability
- H1 history availability
- effective config snapshot

## Stop conditions

Block execution if:

- symbol unknown
- artifact paths unknown
- report path not writable
- source/preset drift cannot be proven clean
- optimization enabled
- effective config mismatch
- any trade action is attempted
- baseline fallback occurs
- required artifacts are missing

## Next safe checkpoint

Checkpoint AA should be the first possible execution approval checkpoint, and only if the user provides exact dates and verified artifact paths.

