# Checkpoint J Risk-Gate Variant Summary

Selected RunId: `run_20260621_214917`

This is a controlled diagnostic run for losing-streak gate behavior. It is not optimization and does not approve a live/demo candidate.

## Variant Phase Results

| Variant | Mode | Phase | Status | Net | PF | Rel DD | Trades | Max Loss Streak | Losing-Streak Blocks | Accepted After First Block | Initial SL | Trailing Profit | TP Hit |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| fixed_cooldown_24bars | DIAGNOSTIC_FIXED_COOLDOWN | out_of_sample | PASS | -61.97 | 0.86 | 1.62 | 116 | 6 | 6 | 54 | 50 | 51 | 13 |
| fixed_cooldown_24bars | DIAGNOSTIC_FIXED_COOLDOWN | train | PASS | -426.33 | 0.82 | 4.6 | 567 | 8 | 93 | 545 | 267 | 231 | 68 |
| fixed_cooldown_24bars | DIAGNOSTIC_FIXED_COOLDOWN | validation | PASS | -168.67 | 0.83 | 2.71 | 248 | 12 | 67 | 143 | 115 | 105 | 27 |
| next_day_reset | DIAGNOSTIC_NEXT_DAY_RESET | out_of_sample | PASS | -61.97 | 0.86 | 1.62 | 116 | 6 | 6 | 54 | 50 | 51 | 13 |
| next_day_reset | DIAGNOSTIC_NEXT_DAY_RESET | train | PASS | -447.57 | 0.81 | 4.73 | 582 | 7 | 57 | 560 | 275 | 236 | 70 |
| next_day_reset | DIAGNOSTIC_NEXT_DAY_RESET | validation | PASS | -129.69 | 0.87 | 2.32 | 258 | 6 | 43 | 153 | 117 | 110 | 30 |
| no_losing_streak_gate | DIAGNOSTIC_NO_LOSING_STREAK_GATE | out_of_sample | PASS | -82.29 | 0.82 | 1.82 | 121 | 6 | 0 | 0 | 53 | 53 | 13 |
| no_losing_streak_gate | DIAGNOSTIC_NO_LOSING_STREAK_GATE | train | PASS | -418.75 | 0.83 | 4.53 | 604 | 5 | 0 | 0 | 283 | 246 | 74 |
| no_losing_streak_gate | DIAGNOSTIC_NO_LOSING_STREAK_GATE | validation | PASS | -95.49 | 0.91 | 2.01 | 272 | 7 | 0 | 0 | 123 | 114 | 34 |
| normal | NORMAL | out_of_sample | PASS | 41.03 | 1.18 | 0.59 | 62 | 4 | 143 | 0 | 27 | 23 | 11 |
| normal | NORMAL | train | PASS | -40.96 | 0.57 | 0.59 | 22 | 4 | 1558 | 0 | 11 | 10 | 1 |
| normal | NORMAL | validation | PASS | 61.38 | 1.16 | 0.63 | 105 | 4 | 467 | 0 | 45 | 43 | 17 |

## Variant Classifications

| Variant | Classification | Failed Gates | Val+OOS Net | Val/OOS Max DD | Val/OOS Max Loss Streak | Accepted After First Block |
|---|---|---|---:|---:|---:|---:|
| fixed_cooldown_24bars | REJECT_FOR_NOW | validation_not_positive,out_of_sample_not_positive,drawdown_materially_worse_than_normal,max_consecutive_losses_worse_than_normal,validation_oos_net_worse_than_normal | -230.64 | 2.71 | 12.0 | 742 |
| next_day_reset | REJECT_FOR_NOW | validation_not_positive,out_of_sample_not_positive,drawdown_materially_worse_than_normal,max_consecutive_losses_worse_than_normal,validation_oos_net_worse_than_normal | -191.66 | 2.32 | 6.0 | 767 |
| no_losing_streak_gate | RISKY_FOR_LIVE | validation_not_positive,out_of_sample_not_positive,drawdown_materially_worse_than_normal,max_consecutive_losses_worse_than_normal,validation_oos_net_worse_than_normal,protective_gate_removed | -177.78 | 2.01 | 7.0 | 0 |
| normal | BASELINE_NORMAL | normal_gate_reference | 102.41 | 0.63 | 4.0 | 0 |

## Interpretation

- `NORMAL` remains the baseline reference. It intentionally blocks after the configured losing streak to protect capital.
- Removing or relaxing the gate increased trade count, but validation and out-of-sample results were worse than the normal gate in this run.
- The no-gate variant is marked `RISKY_FOR_LIVE` because it removes a protective capital-preservation gate.
- Cooldown/reset variants are diagnostic only. They should not be used on demo/live without a separate safety review.

## Safety Notes

- Diagnostic risk-gate modes are blocked outside Strategy Tester by EA safety gates.
- This checkpoint did not optimize parameters, did not add a new strategy, and did not claim profitability.
