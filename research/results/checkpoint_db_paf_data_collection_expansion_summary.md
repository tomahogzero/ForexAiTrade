# Checkpoint DB PAF Data Collection Expansion Summary

RunId: `run_20260709_212026`

Artifact root: `G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\run_20260709_212026\`

## Execution

| Window | Period | Execution | Report | Trades | Diagnostics | Usable direction | Forbidden | Baseline fallback |
|---|---|---|---|---:|---:|---:|---:|---:|
| DB-W1 | `2026-03-29` to `2026-04-05` | `PASS` | `FOUND` | 0 | 58 | 5 | 0 | 0 |
| DB-W2 | `2026-04-05` to `2026-04-12` | `PASS` | `FOUND` | 0 | 94 | 12 | 0 | 0 |
| DB-W3 | `2026-04-12` to `2026-04-19` | `PASS` | `FOUND` | 0 | 82 | 13 | 0 | 0 |
| DB-W4 | `2026-04-19` to `2026-04-26` | `PASS` | `FOUND` | 0 | 113 | 13 | 0 | 0 |

## DB Totals

| Metric | Count |
|---|---:|
| Diagnostic rows | 347 |
| Possible setup rows | 83 |
| Usable direction rows | 43 |
| No-setup direction not required | 264 |
| Trend alignment conflict | 3 |
| Wick too small | 14 |
| Price between EMAs | 23 |
| Possible Fibo Pullback | 59 |
| Possible Zone Rejection | 19 |
| Possible Break Retest | 5 |

## Combined CV + CY + DB

| Metric | Count |
|---|---:|
| Diagnostic rows | 621 |
| Possible setup rows | 174 |
| Usable direction rows | 106 |
| No-setup direction not required | 447 |
| Trend alignment conflict | 15 |
| Wick too small | 25 |
| Price between EMAs | 28 |
| Possible Fibo Pullback | 128 |
| Possible Zone Rejection | 33 |
| Possible Break Retest | 13 |

## Gate Result

- Diagnostic interpretation gate 100: `PASS_LOW_MARGIN`
- Rule-candidate gate 300: `FAIL`

## Verdict

`DB_EXECUTION_PASS`

`NO_TRADE_CONFIRMED_ALL_WINDOWS`

`DIAGNOSTIC_INTERPRETATION_GATE_PASS_LOW_MARGIN`

`RULE_CANDIDATE_GATE_FAIL`

`PAF_NOT_READY_FOR_ORDER_LOGIC`

This is not profitability evidence and does not approve order logic.
