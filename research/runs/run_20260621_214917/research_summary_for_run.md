# ForexAiTrade Research Summary

This summary separates MT5 execution status from strategy performance. Results are not proof of future profitability.

Selected RunId: `run_20260621_214917`

## Case-Level Summary

| Case | Classification | Failed Gates |
|---|---|---|
| EURUSD_H1_RISKGATE_FIXED_COOLDOWN_24BARS_10000 | REJECTED | validation_or_oos_not_positive_valid |
| EURUSD_H1_RISKGATE_NEXT_DAY_RESET_10000 | REJECTED | validation_or_oos_not_positive_valid |
| EURUSD_H1_RISKGATE_NORMAL_10000 | TRAIN_FAILED_VALIDATION_OOS_PASS | train_negative_or_insufficient |
| EURUSD_H1_RISKGATE_NO_LOSING_STREAK_GATE_10000 | REJECTED | validation_or_oos_not_positive_valid |

## Phase Results

| Case | Phase | Symbol | TF | Status | Net Profit | PF | DD | Trades |
|---|---|---|---|---|---:|---:|---:|---:|
| EURUSD_H1_RISKGATE_FIXED_COOLDOWN_24BARS_10000 | out_of_sample | EURUSD | H1 | PASS | -61.97 | 0.86 | 1.62 | 116 |
| EURUSD_H1_RISKGATE_FIXED_COOLDOWN_24BARS_10000 | train | EURUSD | H1 | PASS | -426.33 | 0.82 | 4.6 | 567 |
| EURUSD_H1_RISKGATE_FIXED_COOLDOWN_24BARS_10000 | validation | EURUSD | H1 | PASS | -168.67 | 0.83 | 2.71 | 248 |
| EURUSD_H1_RISKGATE_NEXT_DAY_RESET_10000 | out_of_sample | EURUSD | H1 | PASS | -61.97 | 0.86 | 1.62 | 116 |
| EURUSD_H1_RISKGATE_NEXT_DAY_RESET_10000 | train | EURUSD | H1 | PASS | -447.57 | 0.81 | 4.73 | 582 |
| EURUSD_H1_RISKGATE_NEXT_DAY_RESET_10000 | validation | EURUSD | H1 | PASS | -129.69 | 0.87 | 2.32 | 258 |
| EURUSD_H1_RISKGATE_NO_LOSING_STREAK_GATE_10000 | out_of_sample | EURUSD | H1 | PASS | -82.29 | 0.82 | 1.82 | 121 |
| EURUSD_H1_RISKGATE_NO_LOSING_STREAK_GATE_10000 | train | EURUSD | H1 | PASS | -418.75 | 0.83 | 4.53 | 604 |
| EURUSD_H1_RISKGATE_NO_LOSING_STREAK_GATE_10000 | validation | EURUSD | H1 | PASS | -95.49 | 0.91 | 2.01 | 272 |
| EURUSD_H1_RISKGATE_NORMAL_10000 | out_of_sample | EURUSD | H1 | PASS | 41.03 | 1.18 | 0.59 | 62 |
| EURUSD_H1_RISKGATE_NORMAL_10000 | train | EURUSD | H1 | PASS | -40.96 | 0.57 | 0.59 | 22 |
| EURUSD_H1_RISKGATE_NORMAL_10000 | validation | EURUSD | H1 | PASS | 61.38 | 1.16 | 0.63 | 105 |

## Phase Classifications

| Case | Phase | Phase Classification | Risk-Adjusted | Annualized | Calmar | Score | Failed Gates |
|---|---|---|---|---:|---:|---:|---|
| EURUSD_H1_RISKGATE_FIXED_COOLDOWN_24BARS_10000 | out_of_sample | VALID_RESULT | NOT_VIABLE | -1.3384 | -0.8262 | -61.47 |  |
| EURUSD_H1_RISKGATE_FIXED_COOLDOWN_24BARS_10000 | train | VALID_RESULT | NOT_VIABLE | -2.1287 | -0.4628 | -441.13 |  |
| EURUSD_H1_RISKGATE_FIXED_COOLDOWN_24BARS_10000 | validation | VALID_RESULT | NOT_VIABLE | -1.6867 | -0.6224 | -173.92 |  |
| EURUSD_H1_RISKGATE_NEXT_DAY_RESET_10000 | out_of_sample | VALID_RESULT | NOT_VIABLE | -1.3384 | -0.8262 | -61.47 |  |
| EURUSD_H1_RISKGATE_NEXT_DAY_RESET_10000 | train | VALID_RESULT | NOT_VIABLE | -2.2348 | -0.4725 | -463.12 |  |
| EURUSD_H1_RISKGATE_NEXT_DAY_RESET_10000 | validation | VALID_RESULT | NOT_VIABLE | -1.2969 | -0.559 | -132.59 |  |
| EURUSD_H1_RISKGATE_NORMAL_10000 | out_of_sample | VALID_RESULT | BELOW_FOREX_RISK_PREMIUM | 0.8862 | 1.502 | 49.88 |  |
| EURUSD_H1_RISKGATE_NORMAL_10000 | train | INSUFFICIENT_TRADES | BELOW_FOREX_RISK_PREMIUM | -0.2045 | -0.3466 |  | insufficient_trades |
| EURUSD_H1_RISKGATE_NORMAL_10000 | validation | VALID_RESULT | BELOW_FOREX_RISK_PREMIUM | 0.6138 | 0.9743 | 69.83 |  |
| EURUSD_H1_RISKGATE_NO_LOSING_STREAK_GATE_10000 | out_of_sample | VALID_RESULT | NOT_VIABLE | -1.7773 | -0.9765 | -83.19 |  |
| EURUSD_H1_RISKGATE_NO_LOSING_STREAK_GATE_10000 | train | VALID_RESULT | NOT_VIABLE | -2.0909 | -0.4616 | -433.1 |  |
| EURUSD_H1_RISKGATE_NO_LOSING_STREAK_GATE_10000 | validation | VALID_RESULT | NOT_VIABLE | -0.9549 | -0.4751 | -96.44 |  |

## Failed Gates

| Case | Phase | Phase Gates | Case Gates |
|---|---|---|---|
| EURUSD_H1_RISKGATE_FIXED_COOLDOWN_24BARS_10000 | out_of_sample |  | validation_or_oos_not_positive_valid |
| EURUSD_H1_RISKGATE_FIXED_COOLDOWN_24BARS_10000 | train |  | validation_or_oos_not_positive_valid |
| EURUSD_H1_RISKGATE_FIXED_COOLDOWN_24BARS_10000 | validation |  | validation_or_oos_not_positive_valid |
| EURUSD_H1_RISKGATE_NEXT_DAY_RESET_10000 | out_of_sample |  | validation_or_oos_not_positive_valid |
| EURUSD_H1_RISKGATE_NEXT_DAY_RESET_10000 | train |  | validation_or_oos_not_positive_valid |
| EURUSD_H1_RISKGATE_NEXT_DAY_RESET_10000 | validation |  | validation_or_oos_not_positive_valid |
| EURUSD_H1_RISKGATE_NORMAL_10000 | out_of_sample |  | train_negative_or_insufficient |
| EURUSD_H1_RISKGATE_NORMAL_10000 | train | insufficient_trades | train_negative_or_insufficient |
| EURUSD_H1_RISKGATE_NORMAL_10000 | validation |  | train_negative_or_insufficient |
| EURUSD_H1_RISKGATE_NO_LOSING_STREAK_GATE_10000 | out_of_sample |  | validation_or_oos_not_positive_valid |
| EURUSD_H1_RISKGATE_NO_LOSING_STREAK_GATE_10000 | train |  | validation_or_oos_not_positive_valid |
| EURUSD_H1_RISKGATE_NO_LOSING_STREAK_GATE_10000 | validation |  | validation_or_oos_not_positive_valid |

## Provisional Candidate Ranking

No provisional research candidates yet. No final candidate label is used in this checkpoint.

## Warnings

| Warning | Detail |
|---|---|
| Not Profit Proof | Backtest results do not prove future profitability. |
| No Optimization | This run uses controlled existing parameters only. |
| Annualization Caution | Annualized return and CAGR are informational when the period is short or trade count is low. |
| No Live Readiness | Demo forward testing has not started and should not start from this checkpoint alone. |
| Train Warning | EURUSD_H1_RISKGATE_NORMAL_10000 has validation/OOS pass but train is negative or insufficient. |

## Debug / Infrastructure Failed Runs

| RunId | Case | Status | Message |
|---|---|---|---|
| run_20260619_220639 | EURUSD_H1_10000_out_of_sample | NO_REPORT | MT5 report file was not created. |
| run_20260619_220639 | GOLD_HASH_H4_10000_out_of_sample | NO_REPORT | MT5 report file was not created. |
| run_20260619_220639 | USDJPY_HASH_H1_10000_out_of_sample | NO_REPORT | MT5 report file was not created. |
| run_20260619_221044 | EURUSD_H1_10000_out_of_sample | NO_REPORT | MT5 report file was not created. |
| run_20260619_221044 | GOLD_HASH_H4_10000_out_of_sample | NO_REPORT | MT5 report file was not created. |
| run_20260619_221044 | USDJPY_HASH_H1_10000_out_of_sample | NO_REPORT | MT5 report file was not created. |
| run_20260619_221346 | EURUSD_H1_10000_out_of_sample | NO_REPORT | MT5 report file was not created. |
| run_20260619_221346 | GOLD_HASH_H4_10000_out_of_sample | NO_REPORT | MT5 report file was not created. |
| run_20260619_221346 | USDJPY_HASH_H1_10000_out_of_sample | NO_REPORT | MT5 report file was not created. |
| run_20260620_004004 | EURUSD_H1_10000_validation | NO_REPORT | MT5 report file was not created. |

## Explicit Warning

Backtest and smoke-test results are research artifacts only. They do not prove future profitability and must be followed by validation, out-of-sample checks, and demo forward testing.
