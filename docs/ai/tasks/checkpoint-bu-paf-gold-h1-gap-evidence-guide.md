# Checkpoint BU: PAF Gold H1 Gap Evidence Collection Guide

## Status

`DONE_FOR_REVIEW`

## Scope

Checkpoint BU creates a manual evidence collection guide for `GOLD#` H1 daily session gaps.

This checkpoint is documentation-only:

- no MT5 run by Codex
- no Strategy Tester run
- no EA/source change
- no preset change
- no production validator change
- no joiner run
- no optimization
- no profitability claim

## Why

Checkpoint BT did not approve daily broker-session gaps because independent evidence is still missing.

Checkpoint BU tells the user exactly what manual MT5 screenshots, CSV exports, and notes are needed before policy review can continue.

## Required Evidence

- `GOLD#` H1 chart screenshots around each daily gap.
- A longer `GOLD#` H1 CSV export, ideally `2026-02-01` to `2026-04-01`.
- Confirmation that the CSV is H1, not M1.
- Optional symbol/session specification screenshots.
- Notes documenting terminal, account type, symbol, timeframe, and export date.

## Evidence Folder

Recommended path:

`G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\manual_gap_evidence\GOLD_HASH_H1\`

Suggested subfolders:

- `screenshots/`
- `csv/`
- `notes/`

## Decision

- `MANUAL_GAP_EVIDENCE_GUIDE_CREATED`
- `DAILY_SESSION_GAP_STILL_NOT_APPROVED`
- `JOINER_STILL_BLOCKED`
- `VALIDATOR_PRODUCTION_NOT_CHANGED`
- `MT5_NOT_RUN_BY_CODEX`
- `STRATEGY_TESTER_NOT_RUN`
- `EA_SOURCE_NOT_CHANGED`
- `PRESETS_NOT_CHANGED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`

## Next Safe Step

Checkpoint BV should only start after the user provides manual evidence. If evidence is incomplete, the gap policy remains blocked and the joiner should not run.
