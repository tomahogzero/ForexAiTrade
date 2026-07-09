# Checkpoint DE Fibo Pullback Diagnostic Slice Report

Checkpoint DE is an artifact-summary-only diagnostic report. No MT5 run was performed, no Strategy Tester run was performed, no EA/source code was changed, no presets were changed, no optimization was performed, no lot/risk was increased, and no order logic was added.

## Inputs

- Checkpoint CV summary
- Checkpoint CY summary
- Checkpoint DB summary
- Checkpoint DC diagnostic interpretation summary
- Checkpoint DD Fibo Pullback diagnostic plan

## Combined Counts

| Metric | Value |
|---|---:|
| Diagnostic rows | 621 |
| No-setup direction not required | 447 |
| Possible setup rows | 174 |
| Usable direction rows | 106 |
| Possible Fibo Pullback | 128 |
| Possible Zone Rejection | 33 |
| Possible Break Retest | 13 |
| Trend alignment conflict | 15 |
| Wick too small | 25 |
| Price between EMAs | 28 |

## Fibo Pullback Slice

`Possible Fibo Pullback` accounts for:

- 128 of 174 possible setup rows
- 73.6% of possible setup rows
- 20.6% of all diagnostic rows

This confirms Fibo Pullback as the first diagnostic focus only. It does not approve any entry signal, pending order, market order, or exit behavior.

## Gate Decision

| Gate | Decision |
|---|---|
| Diagnostic interpretation | PASS_LOW_MARGIN |
| Rule candidate | FAIL |
| Order logic | FAIL |

## Limitations

The committed summaries do not include enough row-level detail to calculate Fibo-specific direction quality, confidence, first-touch usability, EMA state distribution, spread distribution, regime distribution, or session distribution.

## Verdicts

- `FIBO_PULLBACK_DIAGNOSTIC_FOCUS_CONFIRMED`
- `FIBO_PULLBACK_ROW_LEVEL_SLICE_REQUIRED`
- `RULE_CANDIDATE_GATE_FAIL`
- `ORDER_LOGIC_NOT_APPROVED`
- `PAF_NOT_READY_FOR_ORDER_LOGIC`

## Next Safe Step

Checkpoint DF should create an artifact-only row-level Fibo Pullback slice extractor/report from existing logs/artifacts if available.

Do not run MT5, do not optimize, and do not implement order logic without separate approval.

