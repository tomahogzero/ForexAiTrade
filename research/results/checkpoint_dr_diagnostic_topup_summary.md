# Checkpoint DR Diagnostic Top-Up Summary

Date: 2026-07-10

Checkpoint DR executed the explicitly approved diagnostic-only `GOLD#` H1 PAF/Fibo usable-direction top-up with the official AK runner/parser workflow.

Selected run: `run_20260710_101729`

The initial run `run_20260710_101355` produced tester/EA logs but could not resolve MT5 reports because the terminal/tester data folders were omitted. It is recorded as an infrastructure retry and none of its coverage counts are used. The selected retry used the same approved windows and unchanged diagnostic settings.

| Window | Execution | Report | Trades | Diagnostics | Usable direction | Fibo usable | Fibo gaps |
|---|---|---|---:|---:|---:|---:|---:|
| DR-W1 | PASS | FOUND | 0 | 86 | 8 | 3 | 5 |
| DR-W2 | PASS | FOUND | 0 | 92 | 13 | 6 | 1 |

DR added 178 diagnostic rows, 39 possible setup rows, 21 usable-direction rows, 15 Fibo Pullback rows, and 9 Fibo usable first-touch rows.

Combined CV + CY + DB + DI + DM + DR now has 20 windows, 1767 diagnostic rows, 490 possible setup rows, 311 total usable-direction rows, and 219 Fibo usable first-touch rows.

The total usable-direction gate is now `PASS` at `311 / 300`. The low-window weakness gate remains `FAIL` because historical weakness remains and DR-W1 added only 3 Fibo usable rows. Checkpoint DS artifact-only review is required before any rule-candidate discussion.

No optimization, EA/preset change, order logic, demo/live forward test, lot/risk increase, or profitability claim is included. PAF remains `NOT_READY_FOR_ORDER_LOGIC`.
