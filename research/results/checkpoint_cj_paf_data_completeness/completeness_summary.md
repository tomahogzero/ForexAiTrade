# Checkpoint CJ: PAF Data Completeness Audit Summary

This is an offline data completeness audit. It does not run MT5, does not run Strategy Tester, does not change EA/source code, and does not approve order logic.

## Verdict

- Status: `PASS_OFFLINE_COMPLETENESS_AUDIT`
- Classification: `DATA_COMPLETENESS_GATE_FAIL`
- Rows read: `33`
- Relabel-ready rows: `17` (`51.52%`)
- Direction-missing rows: `14` (`42.42%`)
- Data-missing rows: `2` (`6.06%`)

## Readiness Counts

| Readiness status | Rows |
| --- | --- |
| RELABEL_READY | 17 |
| DIRECTION_MISSING | 14 |
| DATA_MISSING | 2 |

## Diagnostic Gates

| Gate | Result |
| --- | --- |
| direction_missing_rate_lte_10_percent | FAIL |
| data_missing_rate_lte_5_percent | FAIL |
| relabel_ready_rows_gte_100 | FAIL |
| relabel_ready_rows_gte_300 | FAIL |

## Missing Required Fields

| Field | Rows |
| --- | --- |
| None | 0 |

## Missing Recommended Fields

| Field | Rows |
| --- | --- |
| offline_atr_14 | 16 |

## Interpretation

- Current data does not pass the CI gates for order logic.
- Direction missing remains too high.
- Relabel-ready sample size remains too small.
- This result is a data-quality diagnosis, not a trading-performance result.

## Guardrails

- No MT5 run.
- No Strategy Tester run.
- No EA/source code changes.
- No preset changes.
- No order logic approved.
- No optimization.
- No profitability claim.
