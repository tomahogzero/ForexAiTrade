# Checkpoint DC PAF Diagnostic Interpretation Summary

## Scope

Artifact-only review. No MT5 run. No Strategy Tester run. No source change. No preset change. No optimization. No profitability claim.

## Inputs

- CV: `run_20260709_182444`
- CY: `run_20260709_202415`
- DB: `run_20260709_212026`

## Combined Counts

| Metric | Count |
|---|---:|
| Diagnostic rows | 621 |
| No-setup direction not required | 447 |
| Possible setup rows | 174 |
| Usable direction rows | 106 |
| Trend alignment conflict | 15 |
| Wick too small | 25 |
| Price between EMAs | 28 |

## Gate Result

- Diagnostic interpretation gate 100: `PASS_LOW_MARGIN`
- Rule-candidate gate 300: `FAIL`

## Setup Family Distribution

| Setup family | Count | Share |
|---|---:|---:|
| Possible Fibo Pullback | 128 | 73.6% |
| Possible Zone Rejection | 33 | 19.0% |
| Possible Break Retest | 13 | 7.5% |

## Gap Reason Distribution

| Gap reason | Count |
|---|---:|
| Price between EMAs | 28 |
| Wick too small | 25 |
| Trend alignment conflict | 15 |

## Verdict

`DIAGNOSTIC_INTERPRETATION_ALLOWED_WITH_LOW_MARGIN`

`RULE_CANDIDATE_GATE_FAIL`

`PAF_NOT_READY_FOR_ORDER_LOGIC`

## Next Step

Checkpoint DD should be documentation/review-only and should define a diagnostic interpretation plan, starting with Fibo Pullback. No MT5 run and no order logic.
