# Checkpoint EV XM Exact Gap Evidence Collection Approval

Status: documentation-only approval package complete

## Scope

Define the exact approval boundary for a future EW collection of EQ layer A/B evidence for the frozen 28 `GOLD#` H1 gaps. EV does not open MT5, collect evidence, change policy, or run any analysis.

## Frozen Gates

- ET CSV confirmation: `28/28`
- EQ layer A/B: `0/28` / `0/28`
- exact broker evidence: `0/28`
- global acceptance: `28/28` complete with no missing, duplicate, unmapped, conflicting, or sensitive rows
- otherwise: `BLOCKED_EXACT_XM_EVIDENCE_INCOMPLETE`

## EW Preconditions

- exact user approval using the phrase recorded in `docs/169_Checkpoint_EV_XM_Exact_Gap_Evidence_Collection_Approval_TH.md`
- a safe verifiable export interface
- any MT5 process must be started by EW; only that exact PID may be stopped
- raw evidence stays outside Git and sensitive data is redacted before staging

## Non-Approval Boundary

No Strategy Tester, optimization, policy/validator change, joiner, shadow backtest, EA/preset change, order logic, lot/risk change, demo/live test, automatic gap release, or profitability claim is approved.

## Result

- `EV_EVIDENCE_COLLECTION_APPROVAL_PACKAGE_CREATED`
- strategy performance: `NOT_EVALUATED`
- order logic: `NOT_APPROVED`
- PAF: `NOT_READY_FOR_ORDER_LOGIC`
- future EW: `BLOCKED_UNTIL_EXACT_USER_APPROVAL`
