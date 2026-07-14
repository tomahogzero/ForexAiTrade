# Checkpoint FE: Research Decision Gate

วันที่: 2026-07-15

## Integrity

FC frozen dimensions/ATR boundaries และ FD report ตรวจผ่าน `PASS` ไม่มี dimension ใหม่, optimization หรือ post-hoc filtering

## Full Population First

H6/H12/H24/H48 included/excluded: `1588/12`, `1561/39`, `1534/66`, `1471/129`.

TP_FIRST/SL_FIRST: H6 `460/750`, H12 `567/854`, H24 `622/878`, H48 `604/843`.

## Decision Matrix

| Disposition | Result | Reason |
|---|---|---|
| `REJECT_CURRENT_CANDIDATE` | **Selected** | ทุก full-population horizon มี TP_FIRST ต่ำกว่า SL_FIRST และห้ามเลือก subgroup มา override |
| `RESEARCH_MORE_WITH_NEW_HYPOTHESIS` | Not selected | ไม่มี hypothesis ใหม่ที่ preregistered โดยไม่ post-hoc selection |
| `INSUFFICIENT_EVIDENCE` | Not selected | evidence เพียงพอสำหรับ conservative rejection แต่ไม่พอสำหรับ execution design |
| `ELIGIBLE_FOR_SEPARATE_FORWARD_DIAGNOSTIC_DESIGN` | Not selected | consistency/adequacy ไม่ถึงเกณฑ์โดยไม่เลือก subgroup และ order logic ไม่อนุมัติ |

FD report ครบทุก preregistered direction/year/ATR group; setup subtype, diagnostic reason และ market session เป็น `NOT_AVAILABLE`; ไม่มี `INSUFFICIENT_SAMPLE` ใน available groups. ไม่มี unfavorable/inconclusive group ถูก discard.

## Limitations and Conditions

- broker-history completeness: `NOT_PROVEN`
- horizon populations ต่างกันจาก fail-closed exclusions
- outcome labels/rates ไม่ใช่ profitability, expected return หรือ trading edge
- ไม่มี checkpoint ต่อสำหรับ current candidate
- candidate ใหม่ในอนาคตต้องมี hypothesis preregistered แยก, frozen inputs และ materially new independent evidence ก่อน decision gate ใหม่

## Status

- strategy performance: `NOT_EVALUATED`
- profitability: `NOT_CLAIMED`
- order logic: `NOT_APPROVED`
- PAF: `NOT_READY_FOR_ORDER_LOGIC`

Decision: `FE_REJECT_CURRENT_CANDIDATE_DIAGNOSTIC_ONLY`.
