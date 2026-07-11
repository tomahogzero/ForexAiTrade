# Checkpoint DW: Stability-Gate Specification Decision

วันที่: 2026-07-11

## สถานะ

Checkpoint DW เป็น docs-only decision หลัง DV chronological stability map

DW ไม่รัน MT5 ไม่รัน Strategy Tester ไม่สร้าง execution matrix ไม่แก้ EA/MQL5 ไม่แก้ preset ไม่ optimize ไม่เพิ่ม order logic ไม่ทำ demo/live forward test และไม่อ้าง profitability

PAF ยังคง `NOT_READY_FOR_ORDER_LOGIC`

## Evidence Reviewed

| Evidence | Result |
|---|---|
| Total windows | 20 |
| Weak / watch / normal | 4 / 2 / 14 |
| Historical consecutive weak pair | CY-W3 -> DB-W1 |
| Absolute historical gate | `FAIL` |
| Latest 6 weak windows | 0 |
| Latest 8 weak windows | 1, isolated |
| DI-W3 per-window gap reasons | unresolved, summary-level only |

## Decision Alternatives

| Alternative | DW Decision |
|---|---|
| `KEEP_ABSOLUTE_HISTORICAL_GATE_FAIL` | supported as current state |
| `PROPOSE_DUAL_HISTORICAL_AND_TRAILING_GATE_FOR_APPROVAL` | not supported yet |
| `DATA_LIMITATION_BLOCKS_GATE_REVISION` | `SELECTED` |

Final decision:

`DATA_LIMITATION_BLOCKS_GATE_REVISION`

## Reasons

1. Historical evidence ยังมี consecutive weak pair `CY-W3 -> DB-W1`
2. Trailing horizons 6 และ 8 windows ถูก inspect หลังเห็น outcomes แล้ว
3. ยังไม่มี preregistration ว่าต้องใช้ horizon ใดและผ่านด้วยเกณฑ์ใด
4. การเลือก horizon ที่ดูดีที่สุดตอนนี้เสี่ยงเป็น post-hoc gate fitting
5. DI-W3 ยังไม่มี committed per-window gap-reason attribution
6. Trailing observations จึงเป็น descriptive evidence เท่านั้นและยัง override historical fail ไม่ได้

DW ไม่เปลี่ยน threshold `<5` และไม่เลือก trailing horizon เพื่อทำให้ gate ผ่าน

## Current Gate State

| Gate | Decision |
|---|---|
| Coverage gates | `PASS` |
| Absolute historical stability | `FAIL` |
| Trailing stability gate | `NOT_DEFINED_OR_APPROVED` |
| Dual gate proposal | `BLOCKED_PENDING_PREREGISTRATION` |
| Rule-candidate gate | `FAIL` |
| Order-logic gate | `FAIL` |

## Future Checkpoint DX

DX ต้องเป็น docs-only stability-gate preregistration package ก่อน evidence ใหม่หรือ execution approval ใด ๆ

DX must freeze:

- trailing horizon โดยไม่ใช้ future outcomes
- weak threshold `<5` เว้นแต่มีเหตุผลแยกก่อน evidence
- adjacency และ weak-count pass criteria
- วิธีรายงาน watch windows โดยไม่เปลี่ยนเป็น weak
- minimum independent evidence สำหรับ validation
- fail-safe handling เมื่อ row-level attribution ขาด
- historical weakness ต้องยังแสดงเสมอ แม้ future trailing gate จะผ่าน

DX ไม่อนุมัติ:

- MT5 / Strategy Tester execution
- optimization
- rule candidate
- order logic
- demo/live forward test

## Verdicts

- `DW_GATE_DECISION_COMPLETE`
- `DOCUMENTATION_ONLY`
- `DATA_LIMITATION_BLOCKS_GATE_REVISION`
- `ABSOLUTE_HISTORICAL_GATE_REMAINS_FAIL`
- `TRAILING_OBSERVATIONS_REMAIN_DESCRIPTIVE`
- `POST_HOC_HORIZON_SELECTION_PROHIBITED`
- `DUAL_GATE_PROPOSAL_BLOCKED_PENDING_PREREGISTRATION`
- `FUTURE_DX_PREREGISTRATION_REQUIRED`
- `RULE_CANDIDATE_GATE_FAIL`
- `ORDER_LOGIC_NOT_APPROVED`
- `NO_MT5_RUN`
- `NO_STRATEGY_TESTER_RUN`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`
- `PAF_NOT_READY_FOR_ORDER_LOGIC`

## Next Safe Step

Checkpoint DX docs-only stability-gate preregistration package

## Progress Estimate

- Research infrastructure readiness: `96%`
- PAF diagnostic pipeline readiness: `92%`
- PAF diagnostic interpretation readiness: `90%`
- Fibo Pullback interpretation readiness: `91%`
- PAF rule-candidate readiness: `72%`
- PAF order-logic readiness: `0%`
- Demo/live readiness: `0%`
