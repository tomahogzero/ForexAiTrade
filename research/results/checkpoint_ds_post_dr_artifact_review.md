# Checkpoint DS Post-DR Artifact Review

Date: 2026-07-11

Checkpoint DS reviewed committed DR artifacts only. No MT5 or Strategy Tester run was performed.

DR execution safety passes for selected run `run_20260710_101729`: both approved windows passed, reports and diagnostics were found, total trades remained 0, forbidden and baseline-fallback markers remained 0, and the runner stopped only its spawned PIDs. The initial report-path retry is recorded but not used as coverage evidence.

Combined CV + CY + DB + DI + DM + DR has 20 windows, 1767 diagnostic rows, 311 usable-direction rows, 292 Fibo Pullback rows, and 219 Fibo usable first-touch rows. The usable-direction gate passes with an 11-row margin.

The stability gate still fails. Historical weak windows remain and DR-W1 has only 3 Fibo usable rows. DR-W2 has 6, so the DR pair itself is not a consecutive weak pair.

Usable Fibo direction changed from SELL 78.1% / BUY 21.9% before DR to SELL 76.3% / BUY 23.7% combined. This distribution is reviewed only and is not an approved trading bias.

Fibo gap share changed from 24.2% before DR to 25.0% combined; DR alone was 40.0%. Gaps remain material and are not approved as trading filters.

Rule-candidate and order-logic gates remain `FAIL`. PAF remains `NOT_READY_FOR_ORDER_LOGIC`.
