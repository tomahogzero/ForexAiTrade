# Checkpoint DG Fibo Row-Level Interpretation Summary

Checkpoint DG interprets Checkpoint DF row-level Fibo Pullback outputs only. It does not run MT5 or Strategy Tester and does not change EA/MQL5, presets, trading logic, optimization, lot/risk, or order logic.

## Main Counts

| Metric | Value |
|---|---:|
| Fibo Pullback rows | 128 |
| Fibo usable first-touch rows | 85 |
| Fibo direction gap rows | 43 |
| Usable first-touch share | 66.4% |
| Direction gap share | 33.6% |
| Forbidden action markers | 0 |
| Baseline fallback markers | 0 |

## Direction Counts

| Direction | Count |
|---|---:|
| SELL | 53 |
| BUY | 32 |
| DIRECTION_UNKNOWN | 43 |

## Gap Reasons

| Gap reason | Count |
|---|---:|
| PRICE_BETWEEN_EMAS | 28 |
| TREND_ALIGNMENT_CONFLICT | 15 |

## Gate Decisions

| Gate | Decision |
|---|---|
| Fibo row-level slice exists | PASS |
| Fibo usable rows >= 150 | FAIL |
| Window count >= 12 | FAIL |
| Rule-candidate gate | FAIL |
| Order logic gate | FAIL |

## Verdicts

- `FIBO_DIAGNOSTIC_CONTEXT_IMPROVING`
- `FIBO_USABLE_ROWS_STILL_INSUFFICIENT`
- `FIBO_DIRECTION_GAPS_REMAIN_MATERIAL`
- `FIBO_WINDOW_COVERAGE_STILL_INSUFFICIENT`
- `RULE_CANDIDATE_GATE_FAIL`
- `ORDER_LOGIC_NOT_APPROVED`
- `PAF_NOT_READY_FOR_ORDER_LOGIC`

## Next Safe Step

Checkpoint DH should prepare a diagnostic-only data coverage expansion plan or approval package.

Do not implement order logic, do not optimize, and do not treat Fibo rows as trading signals.

