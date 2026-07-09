# Checkpoint CX: PAF Multi-Window Field Stability Approval

## Purpose

Prepare an approval package for a future multi-window diagnostic-only validation of Checkpoint CT fields and direction-gap bucket stability.

## Scope

This checkpoint is documentation / approval-package only.

- Do not run MT5.
- Do not run Strategy Tester.
- Do not change EA/source code.
- Do not change presets.
- Do not change trading logic.
- Do not optimize.
- Do not increase lot/risk.
- Do not claim profitability.

## Context

Checkpoint CV confirmed CT field presence for one short window:

- RunId: `run_20260709_182444`
- `GOLD#` H1
- `2026-03-01` to `2026-03-08`
- `paf_diagnostic_count=97`
- `total_trades=0`

Checkpoint CW reviewed CV artifacts and concluded:

- `FIELD_PRESENCE_CONFIRMED`
- `PAF_NOT_READY_FOR_ORDER_LOGIC`

## Proposed Future Execution

Future Checkpoint CY may run only after explicit approval:

- Symbol: `GOLD#`
- Timeframe: `H1`
- Windows:
  - `2026-03-08` to `2026-03-15`
  - `2026-03-15` to `2026-03-22`
  - `2026-03-22` to `2026-03-29`
- Strategy Tester only
- No optimization
- No market orders
- No pending orders
- No position modification
- No lot/risk increase
- No profitability interpretation

## Required Checks

Each future window must confirm:

- `total_trades=0`
- forbidden action markers = `0`
- baseline fallback markers = `0`
- CT field presence in `ea_mirror.log`
- parser keys for direction-gap buckets and reason counts
- report artifact found
- no stale artifact reuse

## Approval Phrase

`Approved to execute Checkpoint CY multi-window CT field-presence diagnostic with symbol GOLD# timeframe H1 windows 2026-03-08 to 2026-03-15, 2026-03-15 to 2026-03-22, and 2026-03-22 to 2026-03-29 using official AK runner/parser workflow.`

## Status

Execution remains blocked until the explicit approval phrase is provided.
