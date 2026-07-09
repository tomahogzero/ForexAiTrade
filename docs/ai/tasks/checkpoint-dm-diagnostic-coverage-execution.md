# Checkpoint DM Diagnostic Coverage Execution

Date: 2026-07-09

## Scope

Checkpoint DM executed the explicitly approved diagnostic-only `GOLD#` H1 PAF/Fibo usable-direction coverage expansion.

Approved windows:

| Window | From | To |
|---|---|---|
| DM-W1 | 2026-06-14 | 2026-06-21 |
| DM-W2 | 2026-06-21 | 2026-06-28 |
| DM-W3 | 2026-06-28 | 2026-07-05 |

## Guardrails

- Strategy Tester only.
- No optimization.
- No demo/live forward test.
- No EA/MQL5 changes.
- No preset changes.
- No order logic.
- Total trades must remain `0`.
- No profitability claim.
- Runner may stop only the process IDs it started.

## Result

- RunId: `run_20260709_234906`
- All 3 windows: `execution_status=PASS`
- All 3 windows: report artifact `FOUND`
- All 3 windows: `total_trades=0`
- All 3 windows: PAF diagnostics `FOUND`
- Forbidden action markers: `0`
- Baseline fallback markers: `0`
- Spawned PIDs: `39980`, `20088`, `35272`

## Coverage Delta

DM added:

- diagnostic rows: `290`
- possible setup rows: `67`
- usable direction rows: `41`
- Fibo Pullback rows: `35`
- Fibo usable first-touch rows: `26`
- Fibo direction gap rows: `9`

Combined CV + CY + DB + DI + DM:

- diagnostic windows: `18`
- diagnostic rows: `1589`
- possible setup rows: `451`
- total usable direction rows: `290`
- Fibo Pullback rows: `277`
- Fibo usable first-touch rows: `210`
- Fibo direction gap rows: `67`

## Gate Decision

- window count >= `12`: `PASS`
- Fibo usable first-touch rows >= `150`: `PASS`
- total usable direction rows >= `300`: `FAIL`
- low-window weakness: `FAIL_HISTORICAL_WEAKNESS_REMAINS`
- rule-candidate gate: `FAIL`
- order-logic gate: `FAIL`

PAF remains `NOT_READY_FOR_ORDER_LOGIC`.

## Next Safe Step

Checkpoint DN should be an artifact-only review of DM artifacts and combined CV + CY + DB + DI + DM coverage.

Do not run MT5 again automatically. Do not optimize. Do not implement order logic. Do not claim profitability.
