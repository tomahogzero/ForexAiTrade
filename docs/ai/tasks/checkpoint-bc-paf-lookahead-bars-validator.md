# Checkpoint BC: PAF Lookahead Bars Validator

Date: 2026-07-07

## Scope

Add an offline validator for `paf_lookahead_bars.csv`.

No MT5 run.
No Strategy Tester run.
No EA/source changes.
No preset changes.
No optimization.
No lot/risk increase.
No profitability claim.

## Tool

`tools/paf_lookahead_bars_validator.py`

The validator checks:

- required OHLC columns
- timestamp parsing
- OHLC numeric parsing
- exact diagnostic event timestamp matching
- lookahead horizon coverage
- large timeframe gaps

## Self-Test

The validator was run against synthetic Checkpoint BB-Prep fixtures.

Result:

- verdict: `PASS`
- bar count: `20`
- event count: `4`
- matched event count: `4`
- missing event count: `0`
- gap count: `0`

## Guardrails

This is offline validation only. It must not be interpreted as market evidence or profitability proof.

## Next Safe Step

Use this validator on a real verified `paf_lookahead_bars.csv` before running the Checkpoint BB offline join.
