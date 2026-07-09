# Checkpoint CF: First-Touch Diagnostic Interpretation

## Status

`DIAGNOSTIC_INTERPRETATION_ONLY`

## Source

Checkpoint CE first-touch relabel output.

## Key Counts

- Rows read: `33`
- Relabel-ready rows: `17`
- Data-missing rows: `2`
- Direction-missing rows: `14`

## Key Findings

- `SL_FIRST` is greater than `TP_FIRST` in all horizons.
- Direction missing is high and remains the largest data blocker.
- Sample size is too small for strategy approval.
- Same-bar ambiguity exists and must stay conservative.

## Recommendation

`NOT_READY_FOR_ORDER_LOGIC`

Next step should be diagnostic attribution by classification/session/spread/regime only.

## Guardrails

- No MT5 run
- No Strategy Tester run
- No EA/source changes
- No preset changes
- No optimization
- No order logic
- No profitability claim
