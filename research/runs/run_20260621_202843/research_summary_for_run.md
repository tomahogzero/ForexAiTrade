# ForexAiTrade Research Summary

This summary separates MT5 execution status from strategy performance. Results are not proof of future profitability.

Selected RunId: `run_20260621_202843`

## Case-Level Summary

| Case | Classification | Failed Gates |
|---|---|---|
| EURUSD_H1_10000 | INCOMPLETE_PHASES | missing_train |

## Phase Results

| Case | Phase | Symbol | TF | Status | Net Profit | PF | DD | Trades |
|---|---|---|---|---|---:|---:|---:|---:|
| EURUSD_H1_10000 | out_of_sample | EURUSD | H1 | PASS | 41.03 | 1.18 | 0.59 | 62 |
| EURUSD_H1_10000 | validation | EURUSD | H1 | PASS | 61.38 | 1.16 | 0.63 | 105 |

## Phase Classifications

| Case | Phase | Phase Classification | Score | Failed Gates |
|---|---|---|---:|---|
| EURUSD_H1_10000 | out_of_sample | VALID_RESULT | 49.88 |  |
| EURUSD_H1_10000 | validation | VALID_RESULT | 69.83 |  |

## Failed Gates

| Case | Phase | Phase Gates | Case Gates |
|---|---|---|---|
| EURUSD_H1_10000 | out_of_sample |  | missing_train |
| EURUSD_H1_10000 | validation |  | missing_train |

## Provisional Candidate Ranking

No provisional research candidates yet. No final candidate label is used in this checkpoint.

## Warnings

| Warning | Detail |
|---|---|
| Not Profit Proof | Backtest results do not prove future profitability. |
| No Optimization | This run uses controlled existing parameters only. |
| No Live Readiness | Demo forward testing has not started and should not start from this checkpoint alone. |

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
