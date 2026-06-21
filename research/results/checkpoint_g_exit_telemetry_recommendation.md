# Checkpoint G Exit Telemetry Recommendation

Selected RunId: `run_20260621_202843`

This checkpoint is diagnostic-only. It does not optimize parameters, does not change strategy behavior, and does not prove future profitability.

## Scope

| Case | Phase | Status | Trades | Net Profit | Profit Factor |
|---|---|---|---:|---:|---:|
| EURUSD_H1_10000 | validation | PASS | 105 | 61.38 | 1.16 |
| EURUSD_H1_10000 | out_of_sample | PASS | 62 | 41.03 | 1.18 |

The train phase was intentionally not run in Checkpoint G. Any case-level approval remains incomplete.

## Exit Telemetry Findings

| Exit Classification | Count | Interpretation |
|---|---:|---|
| INITIAL_SL_LOSS | 72 | Actual losing stop-loss exits |
| BREAKEVEN_SL | 1 | Near-flat stop exit |
| TRAILING_SL_PROFIT | 66 | Stop-loss comment, but closed in profit after SL moved |
| TP_HIT | 28 | Take-profit exits |
| OTHER_CLOSE | 0 | No other close type detected |
| UNKNOWN | 0 | No unclassified close type detected |

Most MT5 `SL` close comments are not actual losses. Across validation and out-of-sample, 72 exits were actual initial SL losses, while 66 were trailing-profit exits and 1 was near breakeven.

## Answers

Are most SL exits actual losses, breakeven exits, or trailing profit exits?

They are split almost evenly between actual initial SL losses and trailing-profit exits. The raw MT5 report overstates "SL as bad exit" because many profitable trailing exits still carry an SL close comment.

Is exit logic likely the main weakness?

Exit behavior is a likely research area, but not proven to be the only or main weakness. TP exits are fewer than initial SL losses, while trailing-profit exits are common. This suggests exits matter, but entry quality, session timing, and low trade frequency still need to stay in the diagnostic frame.

Is the problem TP too far, SL too close, trailing behavior, or low trade frequency?

No optimized parameter conclusion should be made yet. The evidence points to three diagnostic questions: whether initial SL losses cluster by session/regime, whether trailing exits give back too much or protect too early, and whether TP distance is reached rarely enough to require exit research. Trade frequency is still modest: 167 trades across validation and out-of-sample only.

Is more logging still needed?

Yes. Telemetry now records OPEN, MODIFY, CLOSE, realized R, and exit classification. Future diagnostic runs should also preserve session/regime at close, spread/slippage at close, and maximum favorable/adverse excursion if available.

Next action:

`NEEDS_EXIT_RESEARCH`

This means research the exit behavior with diagnostics first. It does not mean changing parameters now, and it does not authorize live/demo forward testing.

## Guardrails

- No optimization was performed.
- No strategy entry logic was changed.
- No strategy exit behavior was changed for profitability.
- No MicroTrend, Fibo, Grid, or Pending strategy was added.
- These results are research evidence only, not a profitability claim.
