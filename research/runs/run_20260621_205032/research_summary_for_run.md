# ForexAiTrade Research Summary

This summary separates MT5 execution status from strategy performance. Results are not proof of future profitability.

Selected RunId: `run_20260621_205032`

## Case-Level Summary

| Case | Classification | Failed Gates |
|---|---|---|
| EURUSD_H1_EXIT_BASELINE_10000 | TRAIN_FAILED_VALIDATION_OOS_PASS | train_negative_or_insufficient |
| EURUSD_H1_EXIT_NO_TRAILING_10000 | REJECTED | validation_or_oos_not_positive_valid |
| EURUSD_H1_EXIT_TRAILING_LOOSER_10000 | REJECTED | validation_or_oos_not_positive_valid |
| EURUSD_H1_EXIT_TRAILING_TIGHTER_10000 | REJECTED | validation_or_oos_not_positive_valid |

## Phase Results

| Case | Phase | Symbol | TF | Status | Net Profit | PF | DD | Trades |
|---|---|---|---|---|---:|---:|---:|---:|
| EURUSD_H1_EXIT_BASELINE_10000 | out_of_sample | EURUSD | H1 | PASS | 41.03 | 1.18 | 0.59 | 62 |
| EURUSD_H1_EXIT_BASELINE_10000 | train | EURUSD | H1 | PASS | -40.96 | 0.57 | 0.59 | 22 |
| EURUSD_H1_EXIT_BASELINE_10000 | validation | EURUSD | H1 | PASS | 61.38 | 1.16 | 0.63 | 105 |
| EURUSD_H1_EXIT_NO_TRAILING_10000 | out_of_sample | EURUSD | H1 | PASS | 72.84 | 2.06 | 0.38 | 17 |
| EURUSD_H1_EXIT_NO_TRAILING_10000 | train | EURUSD | H1 | PASS | -22.85 | 0.76 | 0.44 | 17 |
| EURUSD_H1_EXIT_NO_TRAILING_10000 | validation | EURUSD | H1 | PASS | -1.57 | 0.98 | 0.4 | 11 |
| EURUSD_H1_EXIT_TRAILING_LOOSER_10000 | out_of_sample | EURUSD | H1 | PASS | 97.33 | 1.86 | 0.4 | 33 |
| EURUSD_H1_EXIT_TRAILING_LOOSER_10000 | train | EURUSD | H1 | PASS | -47.75 | 0.49 | 0.67 | 21 |
| EURUSD_H1_EXIT_TRAILING_LOOSER_10000 | validation | EURUSD | H1 | PASS | 12.51 | 1.13 | 0.35 | 22 |
| EURUSD_H1_EXIT_TRAILING_TIGHTER_10000 | out_of_sample | EURUSD | H1 | PASS | 9.06 | 1.04 | 0.75 | 78 |
| EURUSD_H1_EXIT_TRAILING_TIGHTER_10000 | train | EURUSD | H1 | PASS | -45.63 | 0.52 | 0.59 | 24 |
| EURUSD_H1_EXIT_TRAILING_TIGHTER_10000 | validation | EURUSD | H1 | PASS | -49.31 | 0.89 | 0.75 | 146 |

## Phase Classifications

| Case | Phase | Phase Classification | Score | Failed Gates |
|---|---|---|---:|---|
| EURUSD_H1_EXIT_BASELINE_10000 | out_of_sample | VALID_RESULT | 49.88 |  |
| EURUSD_H1_EXIT_BASELINE_10000 | train | INSUFFICIENT_TRADES |  | insufficient_trades |
| EURUSD_H1_EXIT_BASELINE_10000 | validation | VALID_RESULT | 69.83 |  |
| EURUSD_H1_EXIT_NO_TRAILING_10000 | out_of_sample | INSUFFICIENT_TRADES |  | insufficient_trades |
| EURUSD_H1_EXIT_NO_TRAILING_10000 | train | INSUFFICIENT_TRADES |  | insufficient_trades |
| EURUSD_H1_EXIT_NO_TRAILING_10000 | validation | INSUFFICIENT_TRADES |  | insufficient_trades |
| EURUSD_H1_EXIT_TRAILING_LOOSER_10000 | out_of_sample | VALID_RESULT | 113.93 |  |
| EURUSD_H1_EXIT_TRAILING_LOOSER_10000 | train | INSUFFICIENT_TRADES |  | insufficient_trades |
| EURUSD_H1_EXIT_TRAILING_LOOSER_10000 | validation | INSUFFICIENT_TRADES |  | insufficient_trades |
| EURUSD_H1_EXIT_TRAILING_TIGHTER_10000 | out_of_sample | VALID_RESULT | 15.71 |  |
| EURUSD_H1_EXIT_TRAILING_TIGHTER_10000 | train | INSUFFICIENT_TRADES |  | insufficient_trades |
| EURUSD_H1_EXIT_TRAILING_TIGHTER_10000 | validation | VALID_RESULT | -44.16 |  |

## Failed Gates

| Case | Phase | Phase Gates | Case Gates |
|---|---|---|---|
| EURUSD_H1_EXIT_BASELINE_10000 | out_of_sample |  | train_negative_or_insufficient |
| EURUSD_H1_EXIT_BASELINE_10000 | train | insufficient_trades | train_negative_or_insufficient |
| EURUSD_H1_EXIT_BASELINE_10000 | validation |  | train_negative_or_insufficient |
| EURUSD_H1_EXIT_NO_TRAILING_10000 | out_of_sample | insufficient_trades | validation_or_oos_not_positive_valid |
| EURUSD_H1_EXIT_NO_TRAILING_10000 | train | insufficient_trades | validation_or_oos_not_positive_valid |
| EURUSD_H1_EXIT_NO_TRAILING_10000 | validation | insufficient_trades | validation_or_oos_not_positive_valid |
| EURUSD_H1_EXIT_TRAILING_LOOSER_10000 | out_of_sample |  | validation_or_oos_not_positive_valid |
| EURUSD_H1_EXIT_TRAILING_LOOSER_10000 | train | insufficient_trades | validation_or_oos_not_positive_valid |
| EURUSD_H1_EXIT_TRAILING_LOOSER_10000 | validation | insufficient_trades | validation_or_oos_not_positive_valid |
| EURUSD_H1_EXIT_TRAILING_TIGHTER_10000 | out_of_sample |  | validation_or_oos_not_positive_valid |
| EURUSD_H1_EXIT_TRAILING_TIGHTER_10000 | train | insufficient_trades | validation_or_oos_not_positive_valid |
| EURUSD_H1_EXIT_TRAILING_TIGHTER_10000 | validation |  | validation_or_oos_not_positive_valid |

## Provisional Candidate Ranking

No provisional research candidates yet. No final candidate label is used in this checkpoint.

## Warnings

| Warning | Detail |
|---|---|
| Not Profit Proof | Backtest results do not prove future profitability. |
| No Optimization | This run uses controlled existing parameters only. |
| No Live Readiness | Demo forward testing has not started and should not start from this checkpoint alone. |
| Train Warning | EURUSD_H1_EXIT_BASELINE_10000 has validation/OOS pass but train is negative or insufficient. |

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
