# Checkpoint DJ DI Artifact Review

Checkpoint DJ reviews committed Checkpoint DI summary artifacts only. It does not run MT5 or Strategy Tester.

## Combined Counts

| Metric | Count |
|---|---:|
| Diagnostic windows | 15 |
| Diagnostic rows | 1299 |
| Possible setup rows | 384 |
| Total usable direction rows | 249 |
| Fibo Pullback rows | 242 |
| Fibo usable first-touch rows | 184 |
| Fibo direction gap rows | 58 |
| Fibo SELL rows | 141 |
| Fibo BUY rows | 43 |
| Fibo DIRECTION_UNKNOWN rows | 58 |

## Gate Decisions

| Gate | Requirement | Current | Decision |
|---|---:|---:|---|
| Diagnostic windows | >= 12 | 15 | PASS |
| Fibo usable first-touch rows | >= 150 | 184 | PASS |
| Total usable direction rows | >= 300 | 249 | FAIL |
| Low-window weakness | no repeated weakness | repeated weakness remains | FAIL |
| Rule candidate | all gates pass | not all gates pass | FAIL |
| Order logic | rule candidate approved | not approved | FAIL |

## Verdict

PAF remains `NOT_READY_FOR_ORDER_LOGIC`.

This review is not profitability evidence and does not approve market orders, pending orders, optimization, or demo/live trading.

