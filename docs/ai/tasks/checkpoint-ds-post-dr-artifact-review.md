# Checkpoint DS Post-DR Artifact Review

Date: 2026-07-11

## Scope

Artifact-only review of committed Checkpoint DR evidence and combined CV + CY + DB + DI + DM + DR coverage.

## Result

- DR selected execution: `PASS`
- all selected reports/diagnostics found
- total trades: `0` in both windows
- forbidden and baseline-fallback markers: `0`
- combined usable-direction rows: `311 / 300`, `PASS`
- combined Fibo usable first-touch rows: `219`, `PASS`
- DR-W1 Fibo usable rows: `3`, weak window
- low-window weakness gate: `FAIL`
- combined SELL/BUY shares: `76.3% / 23.7%`, reviewed but not approved as bias
- combined Fibo gap share: `25.0%`, still material
- rule-candidate gate: `FAIL`
- order logic: not approved

No MT5, Strategy Tester, optimization, EA/preset changes, demo/live forward test, or profitability claim.

## Next Safe Step

Checkpoint DU docs-only weak-window stability review plan.
