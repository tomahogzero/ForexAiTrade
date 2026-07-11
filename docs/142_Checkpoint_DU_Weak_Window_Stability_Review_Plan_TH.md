# Checkpoint DU: Weak-Window Stability Review Plan

วันที่: 2026-07-11

## สถานะ

Checkpoint DU เป็น documentation-only plan หลัง Checkpoint DS เพื่อกำหนดวิธี review weak-window stability ก่อน rule-candidate discussion

DU ไม่รัน MT5 ไม่รัน Strategy Tester ไม่สร้าง execution matrix ไม่แก้ EA/MQL5 ไม่แก้ preset ไม่ optimize ไม่เพิ่ม lot/risk ไม่เพิ่ม order logic ไม่ทำ demo/live forward test และไม่อ้าง profitability

PAF / Price Action Fibo ยังคงเป็น diagnostic-only และยังคงสถานะ:

`NOT_READY_FOR_ORDER_LOGIC`

## Current Coverage

| Metric | Current |
|---|---:|
| Diagnostic windows | 20 |
| Diagnostic rows | 1767 |
| Possible setup rows | 490 |
| Total usable direction rows | 311 |
| Fibo Pullback rows | 292 |
| Fibo usable first-touch rows | 219 |
| Fibo direction gap rows | 73 |

Coverage gates ผ่านแล้ว แต่ low-window stability gate ยัง `FAIL`

## Frozen Diagnostic Classification

DU ล็อก classification สำหรับ stability review เพื่อป้องกันการเปลี่ยน threshold ให้ gate ผ่าน:

| Classification | Fibo usable first-touch rows |
|---|---:|
| Weak | `< 5` |
| Watch | `5-6` |
| Normal for stability review | `>= 7` |

classification นี้เป็น diagnostic label เท่านั้น ไม่ใช่ trading parameter, entry filter หรือ optimization range

## Known Weak Windows

| Window | From | To | Fibo rows | Usable | Gaps | Chronology |
|---|---|---|---:|---:|---:|---|
| DR-W1 | 2026-02-15 | 2026-02-22 | 8 | 3 | 5 | isolated before DR-W2 |
| CY-W3 | 2026-03-22 | 2026-03-29 | 4 | 2 | 2 | consecutive before DB-W1 |
| DB-W1 | 2026-03-29 | 2026-04-05 | 6 | 2 | 4 | consecutive after CY-W3 |
| DI-W3 | 2026-05-10 | 2026-05-17 | 9 | 4 | 5 | isolated before DI-W4 |

Current repeated pattern:

- known weak windows: `4 / 20 = 20.0%`
- consecutive weak pair: `CY-W3 -> DB-W1`
- weak-window Fibo rows: `27 / 292 = 9.2%`
- weak-window Fibo usable rows: `11 / 219 = 5.0%`
- weak-window gaps: `16 / 27 = 59.3%`

Weak windows ไม่ dominate usable sample ทั้งหมด แต่เกิดซ้ำในหลายช่วงเวลาและมี gap share สูง จึงยังห้ามสรุปว่าเป็น sample noise, market filter หรือ no-trade rule

## Future Checkpoint DV

Checkpoint DV ต้องเป็น artifact-only chronological stability map จาก committed artifacts เท่านั้น

Required outputs:

- chronological table ของทั้ง 20 windows
- fixed weak/watch/normal classification ทุก window
- adjacent weak-window pair map
- weak-window Fibo usable share และ gap share
- gap-reason attribution เมื่อมี committed row-level evidence
- ระบุ summary-level limitation เมื่อไม่มี row-level evidence
- แยก historical observation กับ trailing observation
- ห้ามตีความเป็น trading filter หรือ profitability evidence

DV ห้ามรัน MT5 และไม่ต้องมี execution approval phrase

## Future Checkpoint DW

หลัง DV complete แล้ว Checkpoint DW จึงพิจารณา stability-gate specification ได้ใน docs-only scope

Allowed decisions:

- `KEEP_ABSOLUTE_HISTORICAL_GATE_FAIL`
- `PROPOSE_DUAL_HISTORICAL_AND_TRAILING_GATE_FOR_APPROVAL`
- `DATA_LIMITATION_BLOCKS_GATE_REVISION`

Forbidden decisions:

- เปลี่ยน threshold เพื่อ force pass
- optimize threshold
- อนุมัติ trading rule
- อนุมัติ order logic
- อนุมัติ MT5 execution โดยอัตโนมัติ

หากเสนอ dual gate ในอนาคต ต้องแยก historical weakness ออกจาก trailing stability อย่างโปร่งใส และต้องได้รับ review/approval ก่อนใช้กับ rule-candidate gate

## Current Gate Decisions

| Gate | Decision |
|---|---|
| Diagnostic windows >= 12 | `PASS` |
| Fibo usable first-touch >= 150 | `PASS` |
| Total usable direction >= 300 | `PASS` |
| Low-window weakness | `FAIL` |
| Rule-candidate gate | `FAIL` |
| Order-logic gate | `FAIL` |

## Verdicts

- `DU_STABILITY_REVIEW_PLAN_COMPLETE`
- `DOCUMENTATION_ONLY`
- `WEAK_WINDOW_THRESHOLD_FROZEN_BELOW_5`
- `FOUR_KNOWN_WEAK_WINDOWS`
- `ONE_CONSECUTIVE_WEAK_PAIR_REMAINS`
- `LOW_WINDOW_WEAKNESS_GATE_FAIL`
- `FUTURE_DV_ARTIFACT_ONLY_MAP_DEFINED`
- `FUTURE_DW_GATE_DECISION_DEFINED`
- `NO_MT5_RUN`
- `NO_STRATEGY_TESTER_RUN`
- `NO_EXECUTION_MATRIX_CREATED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_ORDER_LOGIC_APPROVED`
- `NO_DEMO_LIVE_FORWARD_TEST`
- `NO_PROFITABILITY_CLAIM`
- `PAF_NOT_READY_FOR_ORDER_LOGIC`

## Next Safe Step

Checkpoint DV artifact-only chronological stability map using committed artifacts only

## Progress Estimate

- Research infrastructure readiness: `96%`
- PAF diagnostic pipeline readiness: `92%`
- PAF diagnostic interpretation readiness: `87%`
- Fibo Pullback interpretation readiness: `88%`
- PAF rule-candidate readiness: `69%`
- PAF order-logic readiness: `0%`
- Demo/live readiness: `0%`
