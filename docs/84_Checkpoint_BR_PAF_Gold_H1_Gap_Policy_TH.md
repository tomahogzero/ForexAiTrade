# Checkpoint BR: PAF Gold H1 Gap Policy Review

เอกสารนี้เป็นการรีวิว policy สำหรับ gap ของข้อมูล `GOLD#` H1 หลังจาก Checkpoint BQ แยกประเภท gap จากไฟล์ normalized bars แล้ว

รอบนี้เป็น documentation / research-policy only:

- ไม่รัน MT5
- ไม่รัน Strategy Tester
- ไม่แก้ EA/source code
- ไม่แก้ preset
- ไม่แก้ validator implementation
- ไม่รัน joiner
- ไม่ optimize
- ไม่สรุปกำไร

## บริบท

Checkpoint BP รัน offline PAF pipeline กับ real `GOLD#` H1 CSV ได้ถึง normalization แต่ validator หยุดเพราะพบ gap มากกว่า timeframe step จำนวน 6 จุด

Checkpoint BQ แยกประเภท gap ได้ดังนี้:

| ประเภท | จำนวน |
|---|---:|
| `WEEKEND_MARKET_CLOSURE` | 1 |
| `SHORT_SESSION_OR_HISTORY_GAP` | 5 |
| รวม | 6 |

รายละเอียด gap:

| Previous time | Next time | Delta hours | Classification |
|---|---|---:|---|
| 2026-03-02 23:00:00 | 2026-03-03 01:00:00 | 2.0 | `SHORT_SESSION_OR_HISTORY_GAP` |
| 2026-03-03 23:00:00 | 2026-03-04 01:00:00 | 2.0 | `SHORT_SESSION_OR_HISTORY_GAP` |
| 2026-03-04 23:00:00 | 2026-03-05 01:00:00 | 2.0 | `SHORT_SESSION_OR_HISTORY_GAP` |
| 2026-03-05 23:00:00 | 2026-03-06 01:00:00 | 2.0 | `SHORT_SESSION_OR_HISTORY_GAP` |
| 2026-03-06 23:00:00 | 2026-03-09 00:00:00 | 49.0 | `WEEKEND_MARKET_CLOSURE` |
| 2026-03-09 22:00:00 | 2026-03-10 00:00:00 | 2.0 | `SHORT_SESSION_OR_HISTORY_GAP` |

## Policy แยกประเภท Gap ที่เสนอ

### 1. Weekend Market Closure

อนุญาตให้พิจารณาเป็น market closure candidate ได้เมื่อ:

- gap ข้ามจากวันศุกร์ไปวันจันทร์
- ไม่มีข้อมูลแทรกกลางช่วง weekend
- symbol เป็นตลาดที่ปิดช่วง weekend ตามปกติ
- gap ไม่ถูกใช้เพื่อกลบ missing data ในวันทำการ

สถานะใน BR:

`WEEKEND_MARKET_CLOSURE_CANDIDATE_ACCEPTABLE_FOR_REVIEW`

ยังไม่ใช่การแก้ code หรือ bypass validator

### 2. Daily Broker-Session Gap

ช่องว่างรายวัน เช่น `23:00 -> 01:00` หรือ `22:00 -> 00:00` อาจเป็น broker maintenance / session break ของ `GOLD#` แต่ต้องตรวจด้วยหลักฐานก่อน

ควรอนุญาตใน validator เฉพาะเมื่อ:

- pattern ซ้ำตามเวลาใกล้เคียงกันหลายวัน
- gap อยู่ในช่วง market/session break ที่ broker ใช้จริง
- ไม่มี expected signal/event อยู่ในช่วง missing bar
- มีเอกสารหรือ export เพิ่มเติมยืนยันว่า MT5 chart ไม่มี bar ในช่วงนั้นจริง
- rule ถูกจำกัดเฉพาะ symbol/timeframe/profile ที่ระบุ ไม่ใช่ global bypass

สถานะใน BR:

`DAILY_BROKER_SESSION_GAP_NEEDS_REVIEW`

ยังไม่ควรถือว่า safe โดยอัตโนมัติ

### 3. True Missing Data

ควรถือเป็น blocker เมื่อ:

- gap เกิดในเวลาที่ตลาดควรมี bar
- gap ไม่ตรงกับ weekend หรือ broker session break
- gap ไม่ซ้ำ pattern เดิม
- มีโอกาสทำให้ lookahead bars หรือ shadow outcome ผิด
- อาจทำให้ entry/SL/TP simulation ใช้ข้อมูลไม่ครบ

สถานะใน BR:

`TRUE_MISSING_DATA_MUST_BLOCK_JOINER`

## ข้อห้าม

- ห้าม bypass validator แบบกว้างๆ
- ห้ามรัน joiner ต่อจนกว่า gap policy จะถูก review และ implement แบบจำกัด scope
- ห้ามใช้ OOS/shadow outcome ที่ผ่าน gap ไม่ชัดเจนเป็นหลักฐาน
- ห้ามสรุป profitability จากข้อมูลที่ validator ยัง reject
- ห้ามปรับ risk/lot เพื่อชดเชยปัญหาข้อมูล

## การตัดสินใจของ Checkpoint BR

- `GAP_POLICY_REVIEW_DONE`
- `WEEKEND_GAP_POLICY_CANDIDATE_DEFINED`
- `DAILY_SESSION_GAP_POLICY_CANDIDATE_DEFINED`
- `DAILY_SESSION_GAPS_NOT_AUTO_APPROVED`
- `TRUE_MISSING_DATA_REMAINS_BLOCKER`
- `VALIDATOR_NOT_CHANGED`
- `JOINER_STILL_BLOCKED`
- `MT5_NOT_RUN`
- `STRATEGY_TESTER_NOT_RUN`
- `EA_SOURCE_NOT_CHANGED`
- `PRESETS_NOT_CHANGED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`

## Next Safe Step

Checkpoint BS ควรเป็น tool-only หรือ docs+tool checkpoint เพื่อเพิ่ม validator dry-run policy แบบ explicit:

- รับ policy file สำหรับ allowed market-session gaps
- แสดงว่า gap ไหนถูกจัดเป็น weekend, daily session, หรือ true missing data
- ไม่แก้ EA/source code
- ไม่รัน MT5
- ไม่รัน joiner แบบ production จนกว่าผล dry-run จะผ่าน review

หากจะอนุญาต daily session gap ต้องทำแบบจำกัด symbol/timeframe เช่น `GOLD# H1` เท่านั้น และต้องบันทึกเหตุผลทุก gap ที่ถูกอนุญาต
