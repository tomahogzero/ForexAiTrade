# Checkpoint BA: PAF Lookahead Bars Artifact Checklist

Date: 2026-07-07

## Scope

Documentation and artifact checklist only.

No EA/source changes.
No preset changes.
No MT5 run.
No Strategy Tester run.
No optimization.
No lot/risk increase.
No profitability claim.

## Purpose

Checkpoint AZ added an offline joiner, but the project still needs a verified `paf_lookahead_bars.csv` before the joiner can be used on real diagnostic artifacts.

BA defines the required bar artifact, validation checklist, stop conditions, and future approval phrase.

## Required Artifact

Recommended file name:

`paf_lookahead_bars.csv`

Required columns:

- `time`
- `open`
- `high`
- `low`
- `close`

Recommended time format:

`YYYY.MM.DD HH:MM:SS`

## Target Context

Current target for the first offline join:

- RunId: `run_20260707_172236`
- Symbol: `GOLD#`
- Timeframe: `H1`
- Diagnostic range: `2026-03-01` to `2026-03-08`
- Bar coverage recommended through at least `2026-03-10 23:59:59` for 48-hour lookahead coverage

## Stop Conditions

Stop if:

- symbol is not `GOLD#`
- timeframe is not `H1`
- timestamp cannot exact-match diagnostic event times
- required columns are missing
- bar coverage is insufficient for the selected horizon
- any MT5 or Strategy Tester execution is needed without a separate approval
- any source/preset change is proposed
- any output is interpreted as profitability proof

## Future Approval Phrase

`Approved to execute Checkpoint BB offline PAF lookahead join with bars CSV <absolute_path_to_csv> for RunId run_20260707_172236.`

This approval must allow only offline Python analysis. It must not authorize MT5, Strategy Tester, orders, optimization, or risk changes.

## Decision

- `LOOKAHEAD_BARS_CHECKLIST_DEFINED`
- `OFFLINE_JOIN_NOT_RUN`
- `MT5_STILL_BLOCKED`
- `ORDER_PATH_STILL_BLOCKED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`

## Next Safe Step

Prepare a verified `paf_lookahead_bars.csv`, then use the future approval phrase to run Checkpoint BB offline join only.
