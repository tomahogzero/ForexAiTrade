# ForexAiTrade Research Summary

This summary separates MT5 execution status from strategy performance. Results are not proof of future profitability.

Selected RunId: `run_20260621_173616`

## Case-Level Summary

| Case | Classification | Failed Gates |
|---|---|---|
| EURUSD_H1_10000 | TRAIN_FAILED_VALIDATION_OOS_PASS | train_negative_or_insufficient |
| GOLD_HASH_H4_30000 | REJECTED | validation_or_oos_not_positive_valid |
| USDJPY_HASH_H1_10000 | REJECTED | validation_or_oos_not_positive_valid |

## Phase Results

| Case | Phase | Symbol | TF | Status | Net Profit | PF | DD | Trades |
|---|---|---|---|---|---:|---:|---:|---:|
| EURUSD_H1_10000 | out_of_sample | EURUSD | H1 | PASS | 41.03 | 1.18 | 0.59 | 62 |
| EURUSD_H1_10000 | train | EURUSD | H1 | PASS | -40.96 | 0.57 | 0.59 | 22 |
| EURUSD_H1_10000 | validation | EURUSD | H1 | PASS | 61.38 | 1.16 | 0.63 | 105 |
| GOLD_HASH_H4_30000 | out_of_sample | GOLD# | H4 | PASS | 0 | 0 | 0.0 | 0 |
| GOLD_HASH_H4_30000 | train | GOLD# | H4 | PASS | 135.85 | 2.12 | 0.17 | 30 |
| GOLD_HASH_H4_30000 | validation | GOLD# | H4 | PASS | 0 | 0 | 0.0 | 0 |
| USDJPY_HASH_H1_10000 | out_of_sample | USDJPY# | H1 | PASS | -30.79 | 0.48 | 0.4 | 12 |
| USDJPY_HASH_H1_10000 | train | USDJPY# | H1 | PASS | -31.87 | 0.39 | 0.55 | 13 |
| USDJPY_HASH_H1_10000 | validation | USDJPY# | H1 | PASS | -63.99 | 0.8 | 0.88 | 91 |

## Phase Classifications

| Case | Phase | Phase Classification | Score | Failed Gates |
|---|---|---|---:|---|
| EURUSD_H1_10000 | out_of_sample | VALID_RESULT | 49.88 |  |
| EURUSD_H1_10000 | train | INSUFFICIENT_TRADES |  | insufficient_trades |
| EURUSD_H1_10000 | validation | VALID_RESULT | 69.83 |  |
| GOLD_HASH_H4_30000 | out_of_sample | NO_RISK_BUDGET |  | broker_min_lot_exceeds_risk_budget |
| GOLD_HASH_H4_30000 | train | VALID_RESULT | 156.2 |  |
| GOLD_HASH_H4_30000 | validation | NO_RISK_BUDGET |  | broker_min_lot_exceeds_risk_budget |
| USDJPY_HASH_H1_10000 | out_of_sample | INSUFFICIENT_TRADES |  | insufficient_trades |
| USDJPY_HASH_H1_10000 | train | INSUFFICIENT_TRADES |  | insufficient_trades |
| USDJPY_HASH_H1_10000 | validation | VALID_RESULT | -60.39 |  |

## Failed Gates

| Case | Phase | Phase Gates | Case Gates |
|---|---|---|---|
| EURUSD_H1_10000 | out_of_sample |  | train_negative_or_insufficient |
| EURUSD_H1_10000 | train | insufficient_trades | train_negative_or_insufficient |
| EURUSD_H1_10000 | validation |  | train_negative_or_insufficient |
| GOLD_HASH_H4_30000 | out_of_sample | broker_min_lot_exceeds_risk_budget | validation_or_oos_not_positive_valid |
| GOLD_HASH_H4_30000 | train |  | validation_or_oos_not_positive_valid |
| GOLD_HASH_H4_30000 | validation | broker_min_lot_exceeds_risk_budget | validation_or_oos_not_positive_valid |
| USDJPY_HASH_H1_10000 | out_of_sample | insufficient_trades | validation_or_oos_not_positive_valid |
| USDJPY_HASH_H1_10000 | train | insufficient_trades | validation_or_oos_not_positive_valid |
| USDJPY_HASH_H1_10000 | validation |  | validation_or_oos_not_positive_valid |

## Provisional Candidate Ranking

No provisional research candidates yet. No final candidate label is used in this checkpoint.

## Warnings

| Warning | Detail |
|---|---|
| Not Profit Proof | Backtest results do not prove future profitability. |
| No Optimization | This run uses controlled existing parameters only. |
| No Live Readiness | Demo forward testing has not started and should not start from this checkpoint alone. |
| Train Warning | EURUSD_H1_10000 has validation/OOS pass but train is negative or insufficient. |

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
