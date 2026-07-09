# Checkpoint DI Diagnostic Coverage Summary

RunId: `run_20260709_225603`

Artifact root: `G:\AiServer\Codex\ForexAiTrade\_checkpoint_di_diagnostic_coverage_exec_worktree\mt5_artifacts\run_20260709_225603\`

This summary separates execution status from strategy interpretation. It is not profitability evidence and does not approve order logic.

## Execution

| Window | Period | Execution | Report | Trades | Diagnostics | Forbidden | Baseline fallback |
|---|---|---|---|---:|---:|---:|---:|
| DI-W1 | `2026-04-26` to `2026-05-03` | `PASS` | `FOUND` | 0 | 112 | 0 | 0 |
| DI-W2 | `2026-05-03` to `2026-05-10` | `PASS` | `FOUND` | 0 | 104 | 0 | 0 |
| DI-W3 | `2026-05-10` to `2026-05-17` | `PASS` | `FOUND` | 0 | 88 | 0 | 0 |
| DI-W4 | `2026-05-17` to `2026-05-24` | `PASS` | `FOUND` | 0 | 96 | 0 | 0 |
| DI-W5 | `2026-05-24` to `2026-05-31` | `PASS` | `FOUND` | 0 | 94 | 0 | 0 |
| DI-W6 | `2026-05-31` to `2026-06-07` | `PASS` | `FOUND` | 0 | 110 | 0 | 0 |
| DI-W7 | `2026-06-07` to `2026-06-14` | `PASS` | `FOUND` | 0 | 74 | 0 | 0 |

## DI Totals

| Metric | Count |
|---|---:|
| Diagnostic rows | 678 |
| Possible setup rows | 210 |
| Usable direction rows | 143 |
| Possible Fibo Pullback | 114 |
| Fibo usable first-touch rows | 99 |
| Fibo direction gap rows | 15 |

## Combined Gate View

| Gate | Requirement | Current | Decision |
|---|---:|---:|---|
| Diagnostic windows | >= 12 | 15 | PASS |
| Fibo usable first-touch rows | >= 150 | 184 | PASS |
| Total usable direction rows | >= 300 | 249 | FAIL |
| Rule candidate | all gates pass | not all gates pass | FAIL |
| Order logic | rule candidate approved | not approved | FAIL |

PAF remains `NOT_READY_FOR_ORDER_LOGIC`.

