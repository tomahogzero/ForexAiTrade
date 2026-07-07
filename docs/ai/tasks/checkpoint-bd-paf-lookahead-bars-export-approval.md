# Checkpoint BD: PAF Lookahead Bars Export Approval

Date: 2026-07-07

## Scope

This checkpoint creates an approval/preflight package for a future one-time real `paf_lookahead_bars.csv` export.

It does not run MT5.
It does not run Strategy Tester.
It does not change EA/source code.
It does not change presets.
It does not optimize.
It does not increase lot/risk.
It does not claim profitability.

## Current Context

The current target diagnostic run is:

- RunId: `run_20260707_172236`
- Symbol: `GOLD#`
- Timeframe: `H1`
- Diagnostic range: `2026-03-01` to `2026-03-08`
- Required lookahead horizon: `48` H1 bars

The required bar coverage is at least:

- From: `2026-03-01 00:00:00`
- Through: `2026-03-10 23:59:59`

## Why This Checkpoint Exists

The offline joiner and validator are ready, but the project still needs a verified real-market OHLC bar source for `GOLD#` H1.

Using the wrong symbol, wrong timeframe, wrong timezone, or non-XM broker data would make the shadow outcome analysis misleading.

## Data Source Rules

Allowed for the first real comparison:

- XM MT5 history export for `GOLD#` H1
- Another OHLC file only if it proves matching broker/server time and is explicitly marked as broker-comparable

Not allowed as equivalent evidence:

- Non-XM gold data without broker comparability proof
- Different gold symbols such as `XAUUSD`, `GOLDm#`, or CFD variants unless explicitly reviewed
- Timezone-shifted data without documented conversion
- Any manually edited prices

## Required Preflight Evidence

Before any future export, capture:

- exact `terminal64.exe` path if MT5 is used
- MT5 data folder from File > Open Data Folder
- whether another MT5 instance is running
- symbol shown as `GOLD#`
- timeframe shown as `H1`
- history coverage through at least `2026-03-10 23:59:59`
- output folder for `paf_lookahead_bars.csv`
- timestamp format and timezone/server-time evidence
- confirmation that data is not edited to improve outcomes

## Stop Conditions

Block export or analysis if:

- symbol is not `GOLD#`
- timeframe is not `H1`
- coverage is shorter than required
- event timestamps cannot match shadow outcome timestamps
- data source is not broker-specific or not labeled correctly
- MT5 or Strategy Tester would be opened without explicit approval
- EA/source code or presets changed unexpectedly
- optimization is enabled
- any order path is involved
- any lot/risk increase is proposed
- profitability is claimed

## Required Validation Before Join

Run `tools/paf_lookahead_bars_validator.py` on the real CSV before using `tools/paf_lookahead_joiner.py`.

The validator must pass with:

- required columns present
- timestamps parsed
- OHLC parsed as numeric values
- diagnostic event timestamps matched
- horizon coverage sufficient
- no unacceptable timeframe gaps

## Future Approval Phrase For Export

`Approved to execute Checkpoint BE one-time GOLD# H1 bars export for PAF lookahead with date range 2026-03-01 to 2026-03-10 using verified XM MT5 history only.`

This phrase approves only bar export/preparation. It does not approve Strategy Tester, orders, optimization, or profitability interpretation.

## Future Approval Phrase For Offline Join

`Approved to execute Checkpoint BB offline PAF lookahead join with bars CSV <absolute_path_to_csv> for RunId run_20260707_172236.`

This phrase approves only offline Python validation/joining against the supplied CSV.

## Decision

- `BARS_EXPORT_APPROVAL_PACKAGE_DEFINED`
- `REAL_MARKET_LOOKAHEAD_CSV_STILL_MISSING`
- `OFFLINE_JOIN_NOT_RUN`
- `MT5_STILL_BLOCKED_UNTIL_EXPLICIT_EXPORT_APPROVAL`
- `ORDER_PATH_STILL_BLOCKED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`
