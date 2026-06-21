# Checkpoint J Risk-Gate Recommendation

Selected RunId: `run_20260621_214917`

Recommendation: `KEEP_NORMAL_GATE_AS_BASELINE`.

The diagnostic variants increased trading activity after losing-streak events, but they did not improve validation/out-of-sample robustness. The normal losing-streak gate should remain enabled for the baseline.

| Variant | Classification | Reason |
|---|---|---|
| fixed_cooldown_24bars | REJECT_FOR_NOW | validation_not_positive,out_of_sample_not_positive,drawdown_materially_worse_than_normal,max_consecutive_losses_worse_than_normal,validation_oos_net_worse_than_normal |
| next_day_reset | REJECT_FOR_NOW | validation_not_positive,out_of_sample_not_positive,drawdown_materially_worse_than_normal,max_consecutive_losses_worse_than_normal,validation_oos_net_worse_than_normal |
| no_losing_streak_gate | RISKY_FOR_LIVE | validation_not_positive,out_of_sample_not_positive,drawdown_materially_worse_than_normal,max_consecutive_losses_worse_than_normal,validation_oos_net_worse_than_normal,protective_gate_removed |
| normal | BASELINE_NORMAL | normal_gate_reference |

## Before Any Future Cooldown Research

- Keep diagnostic modes Strategy Tester only.
- Keep low risk and do not increase lot size to rescue results.
- Compare drawdown, maximum consecutive losses, and trade concentration before looking at net profit.
- Do not start demo forward testing from this checkpoint.

This is not a profitability claim and not a final candidate selection.
