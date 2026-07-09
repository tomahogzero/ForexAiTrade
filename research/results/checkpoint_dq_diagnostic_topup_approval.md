# Checkpoint DQ Diagnostic Top-Up Approval Package

Date: 2026-07-09

Checkpoint DQ is documentation-only. It does not run MT5, does not run Strategy Tester, does not create an execution matrix, does not change EA/MQL5 source, does not change presets, does not optimize, and does not approve order logic.

## Current Blocker

After Checkpoint DN:

| Metric | Current |
|---|---:|
| Diagnostic windows | 18 |
| Diagnostic rows | 1589 |
| Possible setup rows | 451 |
| Total usable direction rows | 290 |
| Total usable direction gate | 300 |
| Shortfall | 10 |
| Fibo usable first-touch rows | 210 |

The total usable direction gate remains `FAIL`, so rule-candidate and order-logic gates remain `FAIL`.

## Future DR Scope

Future Checkpoint DR is blocked until exact approval. If approved later, DR should be a small diagnostic-only top-up:

| Window | From | To |
|---|---|---|
| DR-W1 | 2026-02-15 | 2026-02-22 |
| DR-W2 | 2026-02-22 | 2026-03-01 |

Required constraints:

- `GOLD#` broker-specific symbol.
- H1 timeframe.
- Strategy Tester only.
- Official AK runner/parser workflow.
- No optimization.
- No demo/live forward test.
- No EA or preset changes.
- No order logic.
- Total trades must remain `0`.

## Exact Approval Phrase

Future DR remains blocked until this exact phrase is provided:

`Approved to execute Checkpoint DR diagnostic-only GOLD# H1 PAF/Fibo usable-direction top-up with Strategy Tester only, no optimization, no demo/live forward test, no EA or preset changes, no order logic, total trades must remain 0, using windows 2026-02-15 to 2026-02-22 and 2026-02-22 to 2026-03-01 with the official AK runner/parser workflow.`

## Post-Run Gate

If DR is approved and executed later, Checkpoint DS must review DR artifacts before any rule-candidate discussion.

PAF remains `NOT_READY_FOR_ORDER_LOGIC`.
