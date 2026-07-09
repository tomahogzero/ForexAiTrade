# Checkpoint DN Post-DM Artifact Review

Date: 2026-07-09

Checkpoint DN reviews committed Checkpoint DM artifacts only. It does not run MT5, does not run Strategy Tester, does not change EA/MQL5 source, does not change presets, does not optimize, and does not approve order logic.

## Execution Safety

| Check | Result |
|---|---|
| DM RunId | `run_20260709_234906` |
| Approved windows present | PASS |
| Execution status | PASS for all 3 windows |
| Reports | FOUND for all 3 windows |
| Total trades | 0 for all 3 windows |
| PAF diagnostics | FOUND for all 3 windows |
| Forbidden action markers | 0 |
| Baseline fallback markers | 0 |
| Process safety | runner stopped only spawned PIDs |

DN classifies DM execution safety as `DM_EXECUTION_STATUS_PASS`.

## Combined Coverage

| Metric | Count |
|---|---:|
| Diagnostic windows | 18 |
| Diagnostic rows | 1589 |
| Possible setup rows | 451 |
| Total usable direction rows | 290 |
| Fibo Pullback rows | 277 |
| Fibo usable first-touch rows | 210 |
| Fibo direction gap rows | 67 |
| Fibo SELL rows | 164 |
| Fibo BUY rows | 46 |
| Fibo DIRECTION_UNKNOWN rows | 67 |

The total usable direction gate remains short by `10` rows: `290 / 300`.

## Direction Review

| Scope | SELL | BUY | SELL share | BUY share |
|---|---:|---:|---:|---:|
| Pre-DM | 141 | 43 | 76.6% | 23.4% |
| DM only | 23 | 3 | 88.5% | 11.5% |
| Combined | 164 | 46 | 78.1% | 21.9% |

The distribution remains SELL-heavy, but DN does not approve SELL bias, BUY bias, or any entry rule from this distribution.

## Gap Review

| Scope | Fibo rows | Gap rows | Gap share |
|---|---:|---:|---:|
| Pre-DM | 242 | 58 | 24.0% |
| DM only | 35 | 9 | 25.7% |
| Combined | 277 | 67 | 24.2% |

Combined Fibo gaps remain material:

- `PRICE_BETWEEN_EMAS`: 43
- `TREND_ALIGNMENT_CONFLICT`: 24

## Gate Decisions

| Gate | Decision |
|---|---|
| Diagnostic windows >= 12 | PASS |
| Fibo usable first-touch rows >= 150 | PASS |
| Total usable direction rows >= 300 | FAIL |
| Low-window weakness | FAIL_HISTORICAL_WEAKNESS_REMAINS |
| Rule-candidate gate | FAIL |
| Order-logic gate | FAIL |

PAF remains `NOT_READY_FOR_ORDER_LOGIC`.

Next safe step: Checkpoint DQ docs-only approval package for a small diagnostic-only coverage top-up if more rows are desired; otherwise pause.
