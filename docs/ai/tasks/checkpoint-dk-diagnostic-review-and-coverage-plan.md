# Checkpoint DK Task: Diagnostic Review and Coverage Plan

Status: planned documentation-only checkpoint complete

## Scope

Checkpoint DK documents the next safe path after Checkpoint DJ.

Allowed:

- Create Thai checkpoint document under `docs/`
- Update AI current status
- Define artifact-only Checkpoint DL review scope
- Define blocked future Checkpoint DM approval phrase

Not allowed:

- Run MT5
- Run Strategy Tester
- Change EA/MQL5
- Change presets
- Optimize
- Add order logic
- Increase lot/risk
- Start demo/live forward test
- Claim profitability

## Inputs

- `docs/128_Checkpoint_DJ_DI_Artifact_Review_TH.md`
- `research/results/checkpoint_dj_di_artifact_review.json`
- `docs/ai/current-status.md`

## DK Decisions

- Immediate safe next step: Checkpoint DL artifact-only deep review.
- Future diagnostic-only coverage expansion is Checkpoint DM and remains blocked.
- Exact user approval phrase is required before any future Strategy Tester run.
- Rule-candidate discussion remains blocked.
- Order logic remains blocked.

## Future DM Target

Future DM, if explicitly approved, targets these `GOLD#` H1 Strategy Tester windows:

- `2026-06-14` to `2026-06-21`
- `2026-06-21` to `2026-06-28`
- `2026-06-28` to `2026-07-05`

Safety requirements:

- total trades must remain `0`
- official AK runner/parser workflow only
- no optimization
- no EA or preset changes
- no order logic
- no demo/live forward test

## Required Next Review

If Future DM is executed later, Checkpoint DN must review the artifacts before any rule-candidate discussion.

## Verdicts

- `DK_PLAN_COMPLETE`
- `DOCUMENTATION_ONLY`
- `NO_MT5_RUN`
- `NO_STRATEGY_TESTER_RUN`
- `NO_EA_OR_PRESET_CHANGE`
- `NO_OPTIMIZATION_APPROVED`
- `NO_ORDER_LOGIC_APPROVED`
- `FUTURE_DM_BLOCKED_UNTIL_EXACT_APPROVAL`
- `TOTAL_USABLE_DIRECTION_GATE_STILL_FAIL`
- `LOW_WINDOW_WEAKNESS_GATE_STILL_FAIL`
- `RULE_CANDIDATE_GATE_FAIL`
- `ORDER_LOGIC_NOT_APPROVED`
- `NO_PROFITABILITY_CLAIM`
- `PAF_NOT_READY_FOR_ORDER_LOGIC`

