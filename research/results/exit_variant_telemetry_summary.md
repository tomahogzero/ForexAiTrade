# Checkpoint H Exit Variant Telemetry Summary

Selected RunId: `run_20260621_205032`

This is a controlled, pre-registered diagnostic comparison. It is not optimization and does not approve a final candidate.

## Variant Phase Results

| Variant | Phase | Status | Net | PF | DD | Trades | Initial SL Loss | Breakeven | Trailing Profit | TP Hit | Total R |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | out_of_sample | PASS | 41.03 | 1.18 | 0.59 | 62 | 27 | 1 | 23 | 11 | 3.548768 |
| baseline | train | PASS | -40.96 | 0.57 | 0.59 | 22 | 11 | 0 | 10 | 1 | -3.984758 |
| baseline | validation | PASS | 61.38 | 1.16 | 0.63 | 105 | 45 | 0 | 43 | 17 | 7.821652 |
| no_trailing | out_of_sample | PASS | 72.84 | 2.06 | 0.38 | 17 | 8 | 0 | 0 | 9 | 8.233195 |
| no_trailing | train | PASS | -22.85 | 0.76 | 0.44 | 17 | 12 | 0 | 0 | 5 | -3.172618 |
| no_trailing | validation | PASS | -1.57 | 0.98 | 0.4 | 11 | 7 | 0 | 0 | 4 | 0.206033 |
| trailing_looser | out_of_sample | PASS | 97.33 | 1.86 | 0.4 | 33 | 13 | 0 | 9 | 11 | 10.011908 |
| trailing_looser | train | PASS | -47.75 | 0.49 | 0.67 | 21 | 11 | 0 | 9 | 1 | -5.124583 |
| trailing_looser | validation | PASS | 12.51 | 1.13 | 0.35 | 22 | 11 | 0 | 6 | 5 | 0.768798 |
| trailing_tighter | out_of_sample | PASS | 9.06 | 1.04 | 0.75 | 78 | 28 | 1 | 43 | 6 | -0.250103 |
| trailing_tighter | train | PASS | -45.63 | 0.52 | 0.59 | 24 | 11 | 0 | 13 | 0 | -4.829778 |
| trailing_tighter | validation | PASS | -49.31 | 0.89 | 0.75 | 146 | 52 | 1 | 83 | 10 | -4.981704 |

## Variant Classifications

| Variant | Classification | Failed Gates | Validation Net | OOS Net | Validation/OOS Initial SL | Validation/OOS Trailing Profit | Validation/OOS TP |
|---|---|---|---:|---:|---:|---:|---:|
| baseline | BASELINE_REFERENCE |  | 61.38 | 41.03 | 72.0 | 66.0 | 28.0 |
| no_trailing | INSUFFICIENT_TRADES | validation_or_oos_trade_count | -1.57 | 72.84 | 15.0 | 0.0 | 13.0 |
| trailing_looser | INSUFFICIENT_TRADES | validation_or_oos_trade_count | 12.51 | 97.33 | 24.0 | 15.0 | 16.0 |
| trailing_tighter | REJECT_FOR_NOW | validation_or_oos_not_positive | -49.31 | 9.06 | 80.0 | 126.0 | 16.0 |

## Interpretation Guardrails

- `EXIT_VARIANT_PROMISING` is still not final approval.
- OOS is used only as a diagnostic check, not for overfitting.
- No parameter values should be optimized from this checkpoint alone.
- Demo forward testing remains blocked until later review.
