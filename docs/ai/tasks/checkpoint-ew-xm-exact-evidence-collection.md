# Checkpoint EW XM Exact Evidence Collection

Status: blocked at safe-export-interface preflight

## Approved Scope

Evidence-only collection for EQ layers A/B on the frozen 28 `GOLD#` H1 gaps, using only an EW-owned MT5 PID. No Strategy Tester, policy/validator change, joiner, shadow backtest, EA/preset change, optimization, order logic, risk change, demo/live, or automatic gap release.

## Preflight Result

- no `terminal64.exe` process was running before EW
- XM executable exists at `C:\Program Files\XM Global MT5\terminal64.exe`
- no usable UI automation or non-UI exporter exists in this environment/repository for the required per-gap Layer A evidence bundle
- EW did not start MT5 because the safe-export-interface precondition failed

## Result

- `EW_BLOCKED_NO_SAFE_EXPORT_INTERFACE`
- execution status: `BLOCKED`
- EW-owned MT5 PIDs: `0`
- EQ layers A/B and exact broker evidence: `0/28`, `0/28`, `0/28`
- strategy performance: `NOT_EVALUATED`
- order logic: `NOT_APPROVED`
- PAF: `NOT_READY_FOR_ORDER_LOGIC`

## Next Safe Step

Do not open MT5 automatically. Require a separately reviewed safe export interface or a user-provided per-gap evidence bundle matching the EQ contract, then obtain renewed exact approval before any evidence collection retry.
