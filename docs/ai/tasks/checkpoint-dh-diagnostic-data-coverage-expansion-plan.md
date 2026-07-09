# Checkpoint DH: Diagnostic Data Coverage Expansion Plan

Date: 2026-07-09

## Scope

Checkpoint DH is docs-only and approval-plan-only.

It does not run MT5, does not run Strategy Tester, does not change EA/MQL5, does not change presets, does not optimize, does not increase lot/risk, does not add order logic, and does not claim profitability.

## Reason

Checkpoint DG found:

- Fibo Pullback rows: `128`
- Fibo usable first-touch rows: `85`
- Fibo direction gap rows: `43`
- SELL rows: `53`
- BUY rows: `32`
- DIRECTION_UNKNOWN rows: `43`
- diagnostic windows: `8`

Gate status:

- Fibo usable first-touch rows >= `150`: `FAIL`
- window count >= `12`: `FAIL`
- rule-candidate gate: `FAIL`
- order-logic gate: `FAIL`

PAF remains `NOT_READY_FOR_ORDER_LOGIC`.

## Future DI Target

Future Checkpoint DI may be considered only after exact user approval. It should be diagnostic-only `GOLD#` H1 Strategy Tester coverage expansion using consecutive windows after DB:

- `2026-04-26` to `2026-05-03`
- `2026-05-03` to `2026-05-10`
- `2026-05-10` to `2026-05-17`
- `2026-05-17` to `2026-05-24`
- `2026-05-24` to `2026-05-31`
- `2026-05-31` to `2026-06-07`
- `2026-06-07` to `2026-06-14`

This would raise the planned total from `8` to `15` windows and target Fibo usable first-touch rows from `85` toward `150+`.

## Required Approval Phrase

`Approved to execute Checkpoint DI diagnostic-only GOLD# H1 PAF/Fibo coverage expansion with Strategy Tester only, no optimization, no demo/live forward test, no EA or preset changes, no order logic, total trades must remain 0, using windows 2026-04-26 to 2026-05-03, 2026-05-03 to 2026-05-10, 2026-05-10 to 2026-05-17, 2026-05-17 to 2026-05-24, 2026-05-24 to 2026-05-31, 2026-05-31 to 2026-06-07, and 2026-06-07 to 2026-06-14 with the official AK runner/parser workflow.`

## Decision

- `DH_APPROVAL_PLAN_CREATED`
- `FIBO_COVERAGE_EXPANSION_SCOPE_DEFINED`
- `FUTURE_DI_REQUIRES_EXACT_APPROVAL`
- `MT5_NOT_RUN`
- `STRATEGY_TESTER_NOT_RUN`
- `EA_MQL5_NOT_CHANGED`
- `PRESETS_NOT_CHANGED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_ORDER_LOGIC_APPROVED`
- `NO_PROFITABILITY_CLAIM`
- `PAF_NOT_READY_FOR_ORDER_LOGIC`

