# Checkpoint DQ Diagnostic Top-Up Approval Package

Date: 2026-07-09

## Scope

Checkpoint DQ is a documentation-only approval package for a possible future Checkpoint DR diagnostic-only top-up.

DQ does not run MT5, does not run Strategy Tester, does not create an execution matrix, does not change EA/MQL5 source, does not change presets, does not optimize, and does not approve order logic.

## Reason

Checkpoint DN found:

- total usable direction rows: `290 / 300`
- shortfall: `10`
- low-window weakness remains unresolved
- rule-candidate gate: `FAIL`
- order-logic gate: `FAIL`

## Future DR Target

If explicitly approved later, Future DR may run two completed historical pre-CV backfill windows:

- `2026-02-15` to `2026-02-22`
- `2026-02-22` to `2026-03-01`

Future DR remains Strategy Tester only, diagnostic-only, no optimization, no demo/live, no EA/preset changes, no order logic, and total trades must remain `0`.

## Exact Approval Phrase

`Approved to execute Checkpoint DR diagnostic-only GOLD# H1 PAF/Fibo usable-direction top-up with Strategy Tester only, no optimization, no demo/live forward test, no EA or preset changes, no order logic, total trades must remain 0, using windows 2026-02-15 to 2026-02-22 and 2026-02-22 to 2026-03-01 with the official AK runner/parser workflow.`

## Next Gate

If DR executes later, Checkpoint DS artifact-only review is required before any rule-candidate discussion.
