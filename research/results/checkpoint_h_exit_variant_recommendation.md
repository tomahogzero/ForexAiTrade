# Checkpoint H Exit Variant Recommendation

Selected RunId: `run_20260621_205032`

No final candidate is approved in this checkpoint.

## Summary

| Variant | Classification | Notes |
|---|---|---|
| baseline | BASELINE_REFERENCE | No final candidate approval in Checkpoint H. |
| no_trailing | INSUFFICIENT_TRADES | validation_or_oos_trade_count |
| trailing_looser | INSUFFICIENT_TRADES | validation_or_oos_trade_count |
| trailing_tighter | REJECT_FOR_NOW | validation_or_oos_not_positive |

## Recommendation

`KEEP_BASELINE_NO_CHANGE`: tested variants did not justify replacing the baseline in this checkpoint.

## Guardrails

- This was a pre-registered four-variant comparison, not an optimization sweep.
- No strategy entry logic was changed.
- No new strategy was added.
- OOS results are diagnostic evidence only and must not be used to curve-fit.
- No demo forward test should start from this checkpoint alone.
