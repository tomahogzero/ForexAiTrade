# Checkpoint EU Fail-Closed Shadow Analysis

Date: 2026-07-13

Decision: `EU_FAIL_CLOSED_SHADOW_DIAGNOSTIC_REPRODUCED`.

EU imported a verified handoff package and reproduced the offline fail-closed first-touch diagnostic from committed EM events, unchanged EO gap policy, and non-committed raw yearly GOLD# H1 CSVs.

- handoff SHA-256 manifest: `PASS 6/6`
- handoff/replay rows: `1600/1600`
- per-event/per-horizon field mismatches: `0` across `41` compared fields
- H6/H12/H24/H48 included: `1588/1561/1534/1471`
- H6/H12/H24/H48 excluded: `12/39/66/129`
- exclusion reason: `BLOCKED_GAP_INSIDE_LOOKAHEAD`
- execution status: `PASS`
- strategy performance: `NOT_EVALUATED`
- order logic: `NOT_APPROVED`
- PAF: `NOT_READY_FOR_ORDER_LOGIC`

No MT5/Strategy Tester, EA/preset change, optimization, order logic, lot/risk change, demo/live test, or profitability claim occurred. Raw broker CSVs, ZIP, and temporary extraction are not committed.
