# Checkpoint DM Diagnostic Coverage Summary

RunId: `run_20260709_234906`

Artifact root: `G:\AiServer\Codex\ForexAiTrade\_checkpoint_dm_diagnostic_coverage_exec_worktree\mt5_artifacts\run_20260709_234906\`

This summary separates execution status from strategy interpretation. It is not profitability evidence and does not approve order logic.

## Execution

| Window | Period | Execution | Report | Trades | Diagnostics | Forbidden | Baseline fallback | Spawned PID |
|---|---|---|---|---:|---:|---:|---:|---:|
| DM-W1 | `2026-06-14` to `2026-06-21` | `PASS` | `FOUND` | 0 | 93 | 0 | 0 | 39980 |
| DM-W2 | `2026-06-21` to `2026-06-28` | `PASS` | `FOUND` | 0 | 102 | 0 | 0 | 20088 |
| DM-W3 | `2026-06-28` to `2026-07-05` | `PASS` | `FOUND` | 0 | 95 | 0 | 0 | 35272 |

The runner detected completion and reports for all three windows, and it closed only the process IDs it started.

## DM Totals

| Metric | Count |
|---|---:|
| Diagnostic rows | 290 |
| No-trade rows | 337 |
| Possible setup rows | 67 |
| Usable direction rows | 41 |
| Possible Fibo Pullback rows | 35 |
| Fibo usable first-touch rows | 26 |
| Fibo direction gap rows | 9 |
| Fibo SELL rows | 23 |
| Fibo BUY rows | 3 |
| Fibo DIRECTION_UNKNOWN rows | 9 |
| Fibo `PRICE_BETWEEN_EMAS` gaps | 3 |
| Fibo `TREND_ALIGNMENT_CONFLICT` gaps | 6 |

## Combined Gate View

| Gate | Requirement | Current | Decision |
|---|---:|---:|---|
| Diagnostic windows | >= 12 | 18 | PASS |
| Fibo usable first-touch rows | >= 150 | 210 | PASS |
| Total usable direction rows | >= 300 | 290 | FAIL |
| Low-window weakness | no repeated/consecutive weak-window issue | historical weakness remains | FAIL |
| Rule candidate | all pre-rule gates pass | not all gates pass | FAIL |
| Order logic | rule candidate approved | not approved | FAIL |

## Interpretation Boundary

DM is an execution-safety pass for the approved diagnostic-only Strategy Tester scope. It is not a profitability test, not an optimization run, not a demo/live forward test, and not evidence that order logic should be implemented.

PAF remains `NOT_READY_FOR_ORDER_LOGIC`.

Next safe step: Checkpoint DN artifact-only review of DM artifacts and combined CV + CY + DB + DI + DM coverage.
