# Exit Diagnostics Summary

Selected RunId: `run_20260621_183001`

Exit diagnostics are inferred from MT5 close deal comments. No exit logic was changed.

| Case | Trades | SL | TP | Other/Unknown | Avg Win | Avg Loss | Win/Loss Ratio | Avg Hold Min | Quick <60m | Long >24h | Largest Loss % of Total Loss |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| EURUSD_H1_10000 | 189 | 160 | 29 | 0 | 7.3555 | -8.4629 | 0.8691 | 722.9193 | 16 | 20 | 1.47 |
| EURUSD_H4_10000 | 50 | 44 | 6 | 0 | 6.5695 | -7.5257 | 0.8729 | 3294.7804 | 1 | 32 | 4.64 |
| EURUSD_M30_10000 | 97 | 83 | 14 | 0 | 7.0588 | -9.3358 | 0.7561 | 421.373 | 10 | 6 | 2.75 |

## EURUSD H1 Phase-Level Exit Diagnostics

| Phase | Trades | SL | TP | Avg Win | Avg Loss | Win/Loss Ratio | Avg Hold Min | Max Consecutive Losses | Net Profit |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| train | 22 | 21 | 1 | 4.8609 | -8.5845 | 0.5662 | 776.2691 | 4 | -40.96 |
| validation | 105 | 88 | 17 | 7.5337 | -8.6809 | 0.8678 | 781.5276 | 4 | 61.38 |
| out_of_sample | 62 | 51 | 11 | 7.8482 | -8.0646 | 0.9732 | 604.7327 | 4 | 41.03 |

## Trailing / Breakeven Visibility

The current reports do not reliably show trailing-stop or breakeven modifications. Future EA logging should record every position modification with old/new SL, old/new TP, reason, and timestamp before exit research is implemented.
