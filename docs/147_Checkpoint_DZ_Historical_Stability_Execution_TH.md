# Checkpoint DZ: Historical Stability Execution

วันที่: 2026-07-11

## ขอบเขตที่ได้รับอนุมัติ

Checkpoint DZ ได้รับข้อความอนุมัติตรงตาม Checkpoint DY และรันเฉพาะ Strategy Tester แบบ diagnostic-only สำหรับ broker-specific `GOLD#` H1 ด้วย official AK runner/parser workflow

- ช่วงข้อมูล: `2023-01-01` ถึง `2025-12-28`
- หน้าต่าง: 156 สัปดาห์ต่อเนื่อง ขนาด 7 วัน
- ใช้ทุกหน้าต่างโดยไม่มี sampling หรือเลือกช่วงหลังเห็นผล
- ไม่ optimize
- ไม่ทำ demo/live forward test
- ไม่แก้ EA/MQL5 หรือ preset
- ไม่เพิ่ม order logic
- ไม่เพิ่ม lot/risk
- total trades ต้องเป็น `0`

PAF ยังคงเป็น diagnostic-only และ `NOT_READY_FOR_ORDER_LOGIC`

## Execution Status

การรันแบ่งเป็น 3 batch แบบ sequential เพื่อลดการปะปนของ MT5 data folder และ artifact:

| Batch | Run ID | Window | ช่วง | Execution |
|---|---|---:|---|---|
| DZ-B1 | `run_20260711_145612` | 52 | w001-w052 | PASS |
| DZ-B2 | `run_20260711_152017` | 52 | w053-w104 | PASS |
| DZ-B3 | `run_20260711_153941` | 52 | w105-w156 | PASS |

ผล safety gate รวม:

- execution status `PASS`: 156/156
- report artifact `FOUND`: 156/156
- PAF diagnostics `FOUND`: 156/156
- report สร้างหลังเวลาเริ่ม run และไม่เป็น stale report: 156/156
- authoritative source เป็น `ea_mirror.log`: 156/156
- total trades รวม: `0`
- forbidden action markers รวม: `0`
- baseline fallback markers รวม: `0`
- runner ปิดเฉพาะ PID ที่ตัวเอง spawn

Execution status ข้างต้นแยกจาก diagnostic stability result และไม่ใช่ strategy performance หรือ profitability evidence

## Frozen Classification Results

ใช้เกณฑ์จาก DY โดยไม่เปลี่ยนหลังเห็นข้อมูล:

| Class | Frozen definition | จำนวน |
|---|---:|---:|
| Weak | usable `< 5` | 23 |
| Watch | usable `5-6` | 22 |
| Normal | usable `>= 7` | 111 |

Maximum consecutive weak run เท่ากับ `2` ที่ `dz_w029_20230716_20230723` ถึง `dz_w030_20230723_20230730`

## Frozen Long-Horizon Gate

| Criterion | Frozen requirement | Actual | Gate |
|---|---:|---:|---|
| หน้าต่างต่อเนื่องครบ | 156 | 156 | PASS |
| weak windows | ไม่เกิน 31 | 23 | PASS |
| weak share | ไม่เกิน 20.0% | 14.74% | PASS |
| maximum consecutive weak run | ไม่เกิน 2 | 2 | PASS |
| median usable/window | อย่างน้อย 7 | 9.5 | PASS |
| average usable/window | อย่างน้อย 7.0 | 10.2564 | PASS |
| total usable | อย่างน้อย 1092 | 1600 | PASS |
| per-window counts/gaps/reasons | ครบ | 156/156 | PASS |
| report และ diagnostics | ครบ | 156/156 | PASS |
| trades/forbidden/baseline markers | 0 ทุก window | 0 ทุก window | PASS |

ผล 52-window annual blocks:

| Block | Weak | Weak share | Usable | Gate |
|---|---:|---:|---:|---|
| DZ-B1 | 6/52 | 11.54% | 647 | PASS |
| DZ-B2 | 8/52 | 15.38% | 500 | PASS |
| DZ-B3 | 9/52 | 17.31% | 453 | PASS |

ทุก block ผ่าน frozen limit ที่ weak ไม่เกิน `13/52` หรือ `25.0%`

## Fibo Coverage and Gap Attribution

- Fibo Pullback rows: `2353`
- Fibo usable first-touch rows: `1600`
- Fibo direction gap rows: `753`
- `PRICE_BETWEEN_EMAS`: `554`
- `TREND_ALIGNMENT_CONFLICT`: `198`
- `EMA_SLOPE_FLAT`: `1`
- gap reason attribution: `753/753` ครบ

ข้อมูลรายสัปดาห์ครบ 156 แถว รวม execution status, Fibo rows, usable, gaps, reasons, classification และ safety markers อยู่ใน `research/results/checkpoint_dz_historical_stability_summary.json`

## Gate Interpretation

- three-year historical long-horizon stability gate: `PASS`
- existing 20-window historical gate: `FAIL_REPORTED_SEPARATELY`
- ผล DZ ไม่แก้ย้อนหลังหรือซ่อนผล FAIL เดิม
- DZ pass อนุญาตเพียงการเปิด checkpoint ถัดไปเพื่อ artifact-only rule-candidate readiness review
- rule-candidate ยังไม่ถูกอนุมัติใน DZ
- order-logic gate ยังคง `FAIL_NOT_APPROVED`
- PAF ยังคง `NOT_READY_FOR_ORDER_LOGIC`
- ห้ามตีความ coverage/stability เป็น profitability

## Verdicts

- `DZ_EXECUTION_PASS`
- `ALL_156_CONSECUTIVE_WINDOWS_COMPLETE`
- `NO_TRADE_CONFIRMED_ALL_WINDOWS`
- `FORBIDDEN_AND_BASELINE_MARKERS_ZERO`
- `LONG_HORIZON_STABILITY_GATE_PASS`
- `EXISTING_20_WINDOW_HISTORICAL_GATE_REMAINS_SEPARATE_FAIL`
- `LATER_RULE_CANDIDATE_REVIEW_ONLY`
- `ORDER_LOGIC_NOT_APPROVED`
- `NO_OPTIMIZATION_PERFORMED`
- `NO_DEMO_LIVE_FORWARD_TEST`
- `NO_PROFITABILITY_CLAIM`
- `PAF_NOT_READY_FOR_ORDER_LOGIC`

## Next Safe Step

Checkpoint EA ควรเป็น artifact-only rule-candidate readiness review โดยใช้ frozen DZ evidence เท่านั้น:

- ไม่รัน MT5 หรือ Strategy Tester
- ไม่ optimize
- ไม่แก้ EA/MQL5 หรือ preset
- ไม่เพิ่ม order logic
- ไม่ทำ demo/live forward test
- ไม่อ้าง profitability

## Progress Estimate

- Research infrastructure readiness: `97%`
- PAF diagnostic pipeline readiness: `96%`
- PAF diagnostic interpretation readiness: `95%`
- Fibo Pullback interpretation readiness: `96%`
- PAF rule-candidate readiness: `82%`
- PAF order-logic readiness: `0%`
- Demo/live readiness: `0%`
