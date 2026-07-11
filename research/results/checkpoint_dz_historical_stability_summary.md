# Checkpoint DZ Historical Stability Summary

Date: 2026-07-11

Checkpoint DZ executed the explicitly approved diagnostic-only `GOLD#` H1 PAF/Fibo historical stability backtest with the official AK runner/parser workflow.

## Execution

| Batch | Run ID | Windows | Execution gate |
|---|---|---:|---|
| DZ-B1 | `run_20260711_145612` | 52 | PASS |
| DZ-B2 | `run_20260711_152017` | 52 | PASS |
| DZ-B3 | `run_20260711_153941` | 52 | PASS |

All 156 consecutive weekly windows completed with fresh reports and PAF diagnostics. Total trades, forbidden action markers, and baseline fallback markers were all `0`.

## Frozen Stability Results

| Metric | Frozen requirement | Actual | Gate |
|---|---:|---:|---|
| Consecutive windows | 156 | 156 | PASS |
| Weak windows | <= 31 | 23 | PASS |
| Weak share | <= 20.0% | 14.74% | PASS |
| Maximum consecutive weak run | <= 2 | 2 | PASS |
| Median usable rows/window | >= 7 | 9.5 | PASS |
| Average usable rows/window | >= 7.0 | 10.2564 | PASS |
| Total usable rows | >= 1092 | 1600 | PASS |

Classification totals are 23 weak, 22 watch, and 111 normal windows. The maximum weak run is `w029-w030`.

| Frozen 52-window block | Weak | Weak share | Usable | Gate |
|---|---:|---:|---:|---|
| DZ-B1 | 6 | 11.54% | 647 | PASS |
| DZ-B2 | 8 | 15.38% | 500 | PASS |
| DZ-B3 | 9 | 17.31% | 453 | PASS |

Fibo totals are 2,353 rows, 1,600 usable first-touch rows, and 753 direction gaps. Gap attribution is complete: `PRICE_BETWEEN_EMAS=554`, `TREND_ALIGNMENT_CONFLICT=198`, and `EMA_SLOPE_FLAT=1`.

The complete per-window counts, classifications, gap reasons, execution status, and safety evidence are in `checkpoint_dz_historical_stability_summary.json`.

## Decision

The frozen three-year long-horizon stability gate is `PASS`. The existing 20-window historical gate remains a separately reported `FAIL`; DZ does not rewrite that historical result.

This pass permits only a later artifact-only rule-candidate readiness review. It does not approve order logic, optimization, EA/preset changes, demo/live forward testing, or any profitability claim. PAF remains `NOT_READY_FOR_ORDER_LOGIC`.
