# Baseline Attribution Summary

Selected RunId: `run_20260621_205032`

Scope: `EURUSD_H1_EXIT_BASELINE_10000` only. This is attribution analysis, not optimization.

Recommendation: `KEEP_BASELINE_RESEARCH_MORE`

## By Phase

| phase | trades | net_profit | win_rate | profit_factor | average_r | initial_sl_losses | trailing_profit_exits | tp_hits | max_consecutive_losses |
|---|---|---|---|---|---|---|---|---|---|
| out_of_sample | 62 | 41.03 | 54.84 | 1.1817 | 0.057238 | 27 | 23 | 11 | 4 |
| train | 22 | -40.96 | 50.0 | 0.5662 | -0.181125 | 11 | 10 | 1 | 4 |
| validation | 105 | 61.38 | 57.14 | 1.1571 | 0.074492 | 45 | 43 | 17 | 4 |

## By Session

| phase | session | trades | net_profit | win_rate | profit_factor | average_r | initial_sl_losses | trailing_profit_exits | tp_hits |
|---|---|---|---|---|---|---|---|---|---|
| out_of_sample | Asia | 9 | -10.25 | 55.56 | 0.5968 | -0.129103 | 3 | 5 | 0 |
| out_of_sample | London | 26 | 42.84 | 57.69 | 1.4902 | 0.140955 | 11 | 9 | 6 |
| out_of_sample | London/New York overlap | 13 | 4.78 | 46.15 | 1.0757 | 0.044768 | 7 | 3 | 3 |
| out_of_sample | New York | 13 | 0.32 | 53.85 | 1.0064 | -0.014011 | 6 | 5 | 2 |
| out_of_sample | Other/Unknown | 1 | 3.34 | 100.0 | 999.0 | 0.646035 | 0 | 1 | 0 |
| train | Asia | 1 | -9.42 | 0.0 | 0.0 | -1.0 | 1 | 0 | 0 |
| train | London | 8 | -24.56 | 37.5 | 0.4372 | -0.311086 | 5 | 2 | 1 |
| train | London/New York overlap | 5 | -15.76 | 40.0 | 0.3746 | -0.372436 | 3 | 2 | 0 |
| train | New York | 7 | 17.45 | 85.71 | 3.3267 | 0.341909 | 1 | 6 | 0 |
| train | Other/Unknown | 1 | -8.67 | 0.0 | 0.0 | -1.027251 | 1 | 0 | 0 |
| validation | Asia | 23 | 58.17 | 60.87 | 1.7569 | 0.305547 | 9 | 8 | 6 |
| validation | London | 27 | -18.34 | 51.85 | 0.8433 | -0.067631 | 13 | 11 | 3 |
| validation | London/New York overlap | 26 | 26.35 | 61.54 | 1.3039 | 0.123984 | 10 | 12 | 4 |
| validation | New York | 24 | -3.58 | 54.17 | 0.9617 | -0.035736 | 11 | 10 | 3 |
| validation | Other/Unknown | 5 | -1.22 | 60.0 | 0.9264 | 0.050833 | 2 | 2 | 1 |

## By Direction

| phase | direction | trades | net_profit | win_rate | profit_factor | average_r | initial_sl_losses | trailing_profit_exits | tp_hits |
|---|---|---|---|---|---|---|---|---|---|
| out_of_sample | buy | 18 | -10.44 | 50.0 | 0.8423 | -0.110974 | 8 | 7 | 2 |
| out_of_sample | sell | 44 | 51.47 | 56.82 | 1.3225 | 0.126052 | 19 | 16 | 9 |
| train | buy | 18 | -34.7 | 50.0 | 0.5547 | -0.173921 | 9 | 8 | 1 |
| train | sell | 4 | -6.26 | 50.0 | 0.6206 | -0.213547 | 2 | 2 | 0 |
| validation | buy | 59 | 118.0 | 66.1 | 1.6756 | 0.238988 | 20 | 27 | 12 |
| validation | sell | 46 | -56.62 | 45.65 | 0.7378 | -0.136492 | 25 | 16 | 5 |

## By Exit Type

| phase | exit_type | trades | net_profit | win_rate | profit_factor | average_r |
|---|---|---|---|---|---|---|
| out_of_sample | BREAKEVEN_SL | 1 | -0.1 | 0.0 | 0.0 | -0.010582 |
| out_of_sample | INITIAL_SL_LOSS | 27 | -225.71 | 0.0 | 0.0 | -1.004437 |
| out_of_sample | TP_HIT | 11 | 185.13 | 100.0 | 999.0 | 1.896818 |
| out_of_sample | TRAILING_SL_PROFIT | 23 | 81.71 | 100.0 | 999.0 | 0.426703 |
| train | INITIAL_SL_LOSS | 11 | -94.43 | 0.0 | 0.0 | -1.004277 |
| train | TP_HIT | 1 | 14.25 | 100.0 | 999.0 | 1.841085 |
| train | TRAILING_SL_PROFIT | 10 | 39.22 | 100.0 | 999.0 | 0.522121 |
| validation | INITIAL_SL_LOSS | 45 | -390.64 | 0.0 | 0.0 | -1.008708 |
| validation | TP_HIT | 17 | 263.41 | 100.0 | 999.0 | 1.802734 |
| validation | TRAILING_SL_PROFIT | 43 | 188.61 | 100.0 | 999.0 | 0.524815 |

## By Regime

| phase | regime | trades | net_profit | win_rate | profit_factor | average_r |
|---|---|---|---|---|---|---|
| out_of_sample | breakout | 14 | 9.26 | 42.86 | 1.1583 | 0.00866 |
| out_of_sample | trend | 48 | 31.77 | 58.33 | 1.1899 | 0.071407 |
| train | breakout | 2 | -2.0 | 50.0 | 0.7333 | 0.033683 |
| train | trend | 20 | -38.96 | 50.0 | 0.5518 | -0.202606 |
| validation | breakout | 22 | 32.22 | 54.55 | 1.374 | 0.150827 |
| validation | trend | 83 | 29.16 | 57.83 | 1.0958 | 0.054259 |

## By Spread Bucket

| phase | spread_bucket | trades | net_profit | win_rate | profit_factor | average_r |
|---|---|---|---|---|---|---|
| out_of_sample | 16-20 | 57 | 4.17 | 52.63 | 1.0192 | -0.004712 |
| out_of_sample | 21-25 | 5 | 36.86 | 80.0 | 5.4517 | 0.763468 |
| train | 16-20 | 22 | -40.96 | 50.0 | 0.5662 | -0.181125 |
| validation | 16-20 | 102 | 64.23 | 56.86 | 1.1681 | 0.079152 |
| validation | 21-25 | 3 | -2.85 | 66.67 | 0.6678 | -0.083949 |

## Monthly / Drawdown Concentration

| phase | month | monthly_net_profit | phase_max_trade_sequence_drawdown | phase_worst_drawdown_month |
|---|---|---|---|---|
| train | 2023-01 | -40.96 | 53.18 | 2023-01 |
| validation | 2025-01 | 31.17 | 54.8 | 2025-02 |
| validation | 2025-02 | -31.03 | 54.8 | 2025-02 |
| validation | 2025-03 | 49.01 | 54.8 | 2025-02 |
| validation | 2025-04 | 27.45 | 54.8 | 2025-02 |
| validation | 2025-05 | -15.22 | 54.8 | 2025-02 |
| out_of_sample | 2026-01 | 70.02 | 49.56 | 2026-03 |
| out_of_sample | 2026-02 | -33.09 | 49.56 | 2026-03 |
| out_of_sample | 2026-03 | 4.1 | 49.56 | 2026-03 |

## Guardrail

Do not recommend filters from OOS alone. A filter hypothesis requires consistent validation and OOS evidence with enough trades.
