# Checkpoint BF: PAF Lookahead Bars CSV Intake Validation

Date: 2026-07-08

## Scope

Define the intake and validation gate for a future real `paf_lookahead_bars.csv`.

No MT5 run.
No Strategy Tester run.
No EA/source changes.
No preset changes.
No optimization.
No lot/risk increase.
No profitability claim.

## Target CSV Context

- RunId: `run_20260707_172236`
- Symbol: `GOLD#`
- Timeframe: `H1`
- Diagnostic range: `2026-03-01` to `2026-03-08`
- Required coverage: `2026-03-01 00:00:00` through at least `2026-03-10 23:59:59`
- Lookahead horizon: `48` H1 bars

## Intake Gate

When a CSV path is supplied, Codex must confirm:

- path is absolute
- file exists and is readable
- file is CSV/text, not zip/binary
- source is identified as XM MT5 `GOLD#` H1 or explicitly marked otherwise
- OHLC data is present
- timestamp format can be parsed or a schema-normalization checkpoint is needed
- raw file is not manually price-edited to improve outcomes

## Validation Gate

Run `tools/paf_lookahead_bars_validator.py` before any join attempt.

Validation must determine:

- validation verdict
- bar count
- event count
- matched event count
- missing event count
- gap count
- first/last bar time
- coverage sufficiency

## Classification

Use one of:

- `INTAKE_BLOCKED_NO_FILE`
- `INTAKE_BLOCKED_UNREADABLE_FILE`
- `SCHEMA_CONVERSION_REQUIRED`
- `VALIDATOR_FAIL_NEEDS_FIX`
- `NON_BROKER_COMPARABLE_DIAGNOSTIC_ONLY`
- `VALIDATOR_PASS_READY_FOR_JOIN`

## Join Rule

Do not run `tools/paf_lookahead_joiner.py` unless validation classification is:

`VALIDATOR_PASS_READY_FOR_JOIN`

## Future Approval Phrase

`Approved to execute Checkpoint BB offline PAF lookahead join with bars CSV <absolute_path_to_csv> for RunId run_20260707_172236.`

This permits offline validation/joining only. It does not permit MT5, Strategy Tester, trading, optimization, risk increase, or profitability interpretation.

## Decision

- `CSV_INTAKE_VALIDATION_GATE_DEFINED`
- `REAL_MARKET_LOOKAHEAD_CSV_STILL_MISSING`
- `VALIDATOR_NOT_RUN`
- `JOINER_NOT_RUN`
- `MT5_NOT_RUN`
- `ORDER_PATH_STILL_BLOCKED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`
