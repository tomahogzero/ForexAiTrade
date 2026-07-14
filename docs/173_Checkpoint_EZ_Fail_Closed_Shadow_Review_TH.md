# Checkpoint EZ: Fail-Closed Shadow Review

วันที่: 2026-07-14

## Decision

`PARTIAL_EVIDENCE_ACCEPTED_WITH_FAIL_CLOSED_EXCLUSIONS`

หลักฐาน XM Layer B historical timezone/DST และ holiday close/reopen สำหรับ 28 gaps ยังหาไม่ได้ จึงคง gaps ทั้งหมดเป็น `UNVERIFIED` ห้าม relabel เป็น confirmed closure และห้ามเปลี่ยนหรือ bypass raw-data validator

EZ ใช้ EU merged outcomes แบบ artifact-only; ไม่ recreate shadow analysis และไม่แก้ EU raw outcome rows

## Conservation และผลต่อ Horizon

- total/unique event keys: `1600/1600`
- broker-history completeness: `NOT_PROVEN`

| Horizon | Included | Excluded | Exclusion rate | DATA_INCOMPLETE_GAP | TP_FIRST | SL_FIRST | AMBIGUOUS_SAME_BAR | NO_RESOLUTION |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| H6 | 1588 | 12 | 0.75% | 12 | 460 | 750 | 22 | 356 |
| H12 | 1561 | 39 | 2.44% | 39 | 567 | 854 | 24 | 116 |
| H24 | 1534 | 66 | 4.12% | 66 | 622 | 878 | 26 | 8 |
| H48 | 1471 | 129 | 8.06% | 129 | 604 | 843 | 24 | 0 |

ทุก excluded event/horizon ไม่มี TP_FIRST, SL_FIRST, AMBIGUOUS_SAME_BAR หรือ NO_RESOLUTION ถูกนับเข้าไป Original EU reason `BLOCKED_GAP_INSIDE_LOOKAHEAD` ถูกเก็บไว้เป็น provenance และ EZ semantic reason คือ `DATA_INCOMPLETE_GAP`

## Boundaries

- execution status: `PASS`
- strategy performance: `NOT_EVALUATED`
- profitability: `NOT_CLAIMED`
- order logic: `NOT_APPROVED`
- PAF: `NOT_READY_FOR_ORDER_LOGIC`
- no fill, interpolation, reconstruction, inference หรือ silent bridge
- no MT5/Strategy Tester, EA/preset change, optimization, parameter search, order, lot/risk or demo/live work

Decision: `EZ_FAIL_CLOSED_VALID_SHADOW_POPULATION_REVIEWED`.
