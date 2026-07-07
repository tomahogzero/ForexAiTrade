# Checkpoint AN: PAF Diagnostic Artifact Review

## Objective

Review Checkpoint AM artifacts without rerunning MT5 and determine whether the official AK runner/parser workflow produced safe, coherent diagnostic evidence.

## Scope

In scope:

- Review `run_20260707_121145`.
- Compare AM `417` diagnostics against AI/AJ `418`.
- Confirm no-trade behavior from report and logs.
- Confirm no forbidden action markers.
- Confirm no baseline fallback markers.
- Summarize whether more diagnostic windows are needed.

Out of scope:

- MT5 execution.
- Strategy Tester execution.
- EA/source changes.
- Preset changes.
- Optimization.
- Lot/risk increase.
- Market orders.
- Pending orders.
- Position modification.
- Profitability interpretation.

## Key Finding

The one-line difference between AM `417` and AJ `418` is at `2026.06.29 01:00:00`.

AM classified that hour as `unsafe regime: spread too wide` with spread `115.0`, so no PAF diagnostic line was emitted for that hour. AI logged a PAF `NO_SETUP` diagnostic line for the same hour.

This is a safety/filter classification difference, not order behavior.

## Result

- AM execution status: `PASS`
- Report artifact status: `FOUND`
- Total trades: `0`
- PAF diagnostic count: `417`
- No-trade count: `502`
- Forbidden action marker count: `0`
- Baseline fallback marker count: `0`
- No-trade confirmation: `PASS_FROM_REPORT_AND_EA_LOGS`
- Baseline fallback confirmation: `PASS_FROM_EA_LOGS`

## Next Safe Step

Checkpoint AO should be planning or approval-only for additional no-trade diagnostic windows if needed. Do not run MT5 automatically.

