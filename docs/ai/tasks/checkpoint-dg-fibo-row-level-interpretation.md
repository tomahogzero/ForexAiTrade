# Checkpoint DG: Fibo Row-Level Interpretation

Date: 2026-07-09

## Scope

Checkpoint DG interprets Checkpoint DF row-level Fibo Pullback outputs.

It is artifact-only and documentation-only. It does not run MT5, does not run Strategy Tester, does not modify EA/MQL5, does not modify presets, does not change trading logic, does not optimize, does not increase lot/risk, and does not add order logic.

## Inputs

- `research/results/checkpoint_df_fibo_pullback_row_level_slice.csv`
- `research/results/checkpoint_df_fibo_pullback_row_level_slice_summary.md`
- `research/results/checkpoint_df_fibo_pullback_row_level_slice_summary.json`

## Interpretation

Fibo Pullback diagnostic context is improving, but it remains below the threshold required for rule-candidate discussion.

Important counts:

- Fibo rows: `128`
- Fibo usable first-touch rows: `85`
- Fibo direction gap rows: `43`
- SELL rows: `53`
- BUY rows: `32`
- DIRECTION_UNKNOWN rows: `43`
- forbidden action markers: `0`
- baseline fallback markers: `0`

## Decisions

- Fibo row-level slice exists: `PASS`
- Fibo-specific usable row gate 150: `FAIL`
- 12-window coverage gate: `FAIL`
- rule-candidate gate: `FAIL`
- order logic approval: `FAIL`

## Verdict

- `FIBO_DIAGNOSTIC_CONTEXT_IMPROVING`
- `FIBO_USABLE_ROWS_STILL_INSUFFICIENT`
- `FIBO_DIRECTION_GAPS_REMAIN_MATERIAL`
- `FIBO_WINDOW_COVERAGE_STILL_INSUFFICIENT`
- `RULE_CANDIDATE_GATE_FAIL`
- `ORDER_LOGIC_NOT_APPROVED`
- `PAF_NOT_READY_FOR_ORDER_LOGIC`

## Next Safe Step

Checkpoint DH should prepare a diagnostic-only data coverage expansion plan/approval package.

The goal is to increase windows and Fibo usable rows, not to implement orders or optimize.

