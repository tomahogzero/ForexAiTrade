# Checkpoint DR Diagnostic Top-Up Execution

Date: 2026-07-10

## Scope

Checkpoint DR executed the explicitly approved diagnostic-only `GOLD#` H1 PAF/Fibo usable-direction top-up for `2026-02-15` to `2026-02-22` and `2026-02-22` to `2026-03-01`.

## Execution

- Initial run `run_20260710_101355`: reports unresolved because terminal/tester data folders were omitted; no coverage evidence used.
- Selected run `run_20260710_101729`: both windows `execution_status=PASS`.
- Both selected windows: report `FOUND`, total trades `0`, diagnostics `FOUND`.
- Forbidden markers: `0`.
- Baseline fallback markers: `0`.
- Selected spawned PIDs: `27136`, `32088`.
- Runner stopped only PIDs it started.

## Coverage

DR added:

- diagnostic rows: `178`
- possible setup rows: `39`
- usable direction rows: `21`
- Fibo Pullback rows: `15`
- Fibo usable first-touch rows: `9`
- Fibo direction gaps: `6`

Combined CV + CY + DB + DI + DM + DR:

- windows: `20`
- diagnostic rows: `1767`
- possible setup rows: `490`
- total usable direction rows: `311`
- Fibo usable first-touch rows: `219`

## Decision

- total usable-direction gate: `PASS`
- low-window weakness: `FAIL`
- Checkpoint DS review: required
- rule-candidate gate: `FAIL_PENDING_REVIEW`
- order logic: not approved
- PAF: `NOT_READY_FOR_ORDER_LOGIC`

No optimization, demo/live forward test, EA/preset change, order logic, lot/risk increase, or profitability claim was made.
