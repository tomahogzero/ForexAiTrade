# Checkpoint DY: Historical Stability Readiness and Approval Package

วันที่: 2026-07-11

## สถานะและการแก้ไข

Checkpoint DY แก้ assumption ของ DX ที่รอ future data ถึง 2026-08-30

ForexAiTrade อยู่ใน backtest-only stage และใช้ historical broker data ได้ จึงไม่จำเป็นต้องรอข้อมูลอนาคต DX future wait block ถูก supersede โดย DY historical holdout specification

DY เป็น docs-only approval package ไม่รัน MT5 ไม่รัน Strategy Tester ไม่สร้าง execution matrix ไม่แก้ EA/MQL5 ไม่แก้ preset ไม่ optimize ไม่เพิ่ม order logic ไม่ทำ demo/live forward test และไม่อ้าง profitability

PAF ยังคง `NOT_READY_FOR_ORDER_LOGIC`

## Frozen Historical Holdout

| Field | Value |
|---|---|
| Symbol | broker-specific `GOLD#` |
| Timeframe | H1 |
| From | 2023-01-01 |
| To | 2025-12-28 |
| Window size | 7 days |
| Window count | 156 |
| Selection | all consecutive weekly windows |
| Sampling | prohibited |

ใช้ทุกสัปดาห์ต่อเนื่องครบ 3 ปีเพื่อลด selection bias ห้ามเลือกเฉพาะเดือน ไตรมาส หรือช่วงที่ผลดูดี

## Frozen Classification

| Class | Fibo usable first-touch rows |
|---|---:|
| Weak | `< 5` |
| Watch | `5-6` |
| Normal | `>= 7` |

ห้ามเปลี่ยน classification หลังเห็น historical holdout results

## Frozen Long-Horizon Criteria

Future DZ result จะ reviewable เป็น long-horizon pass ได้เมื่อผ่านทุกข้อ:

1. windows ครบ 156 ช่วงและต่อเนื่องโดยไม่มี omission/duplication
2. weak-window share ไม่เกิน `20.0%` หรือไม่เกิน `31 / 156`
3. maximum consecutive weak run ไม่เกิน `2`
4. weak share ของแต่ละ 52-window annual block ไม่เกิน `25.0%` หรือ `13 / 52`
5. median Fibo usable rows ต่อ window อย่างน้อย `7`
6. average Fibo usable rows ต่อ windowอย่างน้อย `7.0`
7. total Fibo usable rows อย่างน้อย `1092`
8. watch windows ต้องรายงานแยก
9. มี per-window Fibo rows, usable, gaps และ gap reasons ครบ
10. report และ PAF diagnostics พบทุก window
11. total trades เท่ากับ `0` ทุก window
12. forbidden action markers และ baseline fallback markers เท่ากับ `0` ทุก window

ห้ามปรับ criteria หลังเห็นผล หาก criteria ใดไม่ผ่านต้องรายงาน fail ตามจริง ไม่ optimize เพื่อให้ผ่าน

## Reporting Contract

- existing 20-window historical gate ยังรายงานแยกเป็น `FAIL`
- three-year holdout gate ปัจจุบัน `NOT_RUN`
- ต้องรายงาน breakdown ปี 2023, 2024, 2025
- ต้องรายงาน maximum weak run และตำแหน่ง
- ต้องรายงาน gap-reason distribution
- ห้ามตีความ diagnostic coverage เป็น profitability
- holdout pass อนุญาตได้เพียง future rule-candidate review checkpoint
- holdout pass ไม่อนุมัติ order logic

## Future Checkpoint DZ Scope

Future DZ ต้องเป็น:

- Strategy Tester only
- `GOLD#` H1 broker-specific
- official AK runner/parser workflow
- all 156 consecutive weekly windows
- no optimization
- no demo/live forward test
- no EA/MQL5 or preset changes
- no order logic
- total trades exactly `0`
- runner stops only its own spawned PID

## Exact Future Approval Phrase

Future DZ จะรันได้เมื่อผู้ใช้ส่งข้อความนี้ตรงตัว:

`Approved to execute Checkpoint DZ diagnostic-only GOLD# H1 PAF/Fibo historical stability backtest with Strategy Tester only, no optimization, no demo/live forward test, no EA or preset changes, no order logic, total trades must remain 0, using all 156 consecutive weekly windows from 2023-01-01 through 2025-12-28 exactly as preregistered in Checkpoint DY with the official AK runner/parser workflow.`

## Stop Conditions

ต้องหยุดแบบ fail-safe หาก:

- exact approval phrase ไม่มีหรือไม่ตรง
- symbol ไม่ใช่ `GOLD#` หรือ timeframe ไม่ใช่ H1
- window ใดถูกข้าม ซ้ำ เลื่อน หรือ sampled
- historical data ไม่ครบใน window ใด
- report หรือ PAF diagnostics ขาด
- total trades มากกว่า 0
- forbidden action หรือ baseline fallback marker มากกว่า 0
- ต้องแก้ EA/preset, lot/risk, optimization หรือ order logic
- runner ต้องหยุด process ที่ไม่ได้ spawn เอง

## Verdicts

- `DY_HISTORICAL_CORRECTION_COMPLETE`
- `DX_FUTURE_WAIT_BLOCK_SUPERSEDED`
- `DOCUMENTATION_ONLY`
- `THREE_YEAR_HISTORICAL_HOLDOUT_FROZEN`
- `ALL_156_WEEKLY_WINDOWS_REQUIRED`
- `NO_HISTORICAL_SAMPLING_ALLOWED`
- `LONG_HORIZON_CRITERIA_FROZEN`
- `FUTURE_DZ_BLOCKED_UNTIL_EXACT_APPROVAL`
- `NO_MT5_RUN`
- `NO_STRATEGY_TESTER_RUN`
- `NO_EXECUTION_MATRIX_CREATED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_ORDER_LOGIC_APPROVED`
- `NO_DEMO_LIVE_FORWARD_TEST`
- `NO_PROFITABILITY_CLAIM`
- `PAF_NOT_READY_FOR_ORDER_LOGIC`

## Progress Estimate

- Research infrastructure readiness: `96%`
- PAF diagnostic pipeline readiness: `92%`
- PAF diagnostic interpretation readiness: `91%`
- Fibo Pullback interpretation readiness: `92%`
- PAF rule-candidate readiness: `74%`
- PAF order-logic readiness: `0%`
- Demo/live readiness: `0%`
