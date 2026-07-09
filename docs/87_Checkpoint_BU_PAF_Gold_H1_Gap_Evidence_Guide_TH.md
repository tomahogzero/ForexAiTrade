# Checkpoint BU: PAF Gold H1 Gap Evidence Collection Guide

เอกสารนี้เป็นคู่มือเก็บหลักฐานด้วยมือสำหรับ daily session gaps ของ `GOLD#` H1 ก่อนจะพิจารณาอนุมัติ gap policy หรือรัน offline joiner ต่อ

รอบนี้เป็น documentation-only:

- ไม่รัน MT5 โดย Codex
- ไม่รัน Strategy Tester
- ไม่แก้ EA/source code
- ไม่แก้ preset
- ไม่แก้ production validator
- ไม่รัน joiner
- ไม่ optimize
- ไม่เพิ่ม lot/risk
- ไม่สรุป profitability

## ทำไมต้องเก็บหลักฐาน

Checkpoint BS พบว่า gap policy dry-run ยังเป็น `REVIEW_REQUIRED`

Checkpoint BT สรุปว่า daily broker-session gaps ของ `GOLD#` H1 ยังไม่ควรถูกอนุมัติ เพราะยังไม่มีหลักฐานพอว่า gap เหล่านี้เป็น session break ปกติของ broker ไม่ใช่ข้อมูลขาด

ถ้าเราอนุญาต gap ผิด อาจทำให้ shadow outcome ใช้ข้อมูลไม่ครบ และทำให้ผลวิจัยผิดได้

## Gap ที่ต้องตรวจ

| Previous time | Next time | Delta hours |
|---|---|---:|
| 2026-03-02 23:00:00 | 2026-03-03 01:00:00 | 2.0 |
| 2026-03-03 23:00:00 | 2026-03-04 01:00:00 | 2.0 |
| 2026-03-04 23:00:00 | 2026-03-05 01:00:00 | 2.0 |
| 2026-03-05 23:00:00 | 2026-03-06 01:00:00 | 2.0 |
| 2026-03-09 22:00:00 | 2026-03-10 00:00:00 | 2.0 |

## หลักฐานที่ต้องการ

### 1. Screenshot จาก MT5 Chart

ให้เปิด MT5 ด้วยบัญชี demo เดิม แล้วตรวจ:

- Symbol: `GOLD#`
- Timeframe: `H1`
- Chart type: Candlesticks หรือ Bar Chart
- เปิดช่วงวันที่ที่มี gap
- ให้เห็นแท่งก่อน gap และแท่งหลัง gap ชัดเจน
- ให้เห็น time axis ด้านล่างชัดเจน

Screenshot ที่ต้องการ:

- `GOLD_HASH_H1_gap_20260302_2300_to_20260303_0100.png`
- `GOLD_HASH_H1_gap_20260303_2300_to_20260304_0100.png`
- `GOLD_HASH_H1_gap_20260304_2300_to_20260305_0100.png`
- `GOLD_HASH_H1_gap_20260305_2300_to_20260306_0100.png`
- `GOLD_HASH_H1_gap_20260309_2200_to_20260310_0000.png`

ถ้าทำทีละภาพยาก สามารถทำ screenshot กว้างๆ 1-2 ภาพที่เห็นหลาย gap พร้อมกันได้ แต่ต้องเห็นเวลาและแท่งชัดเจน

### 2. CSV Export จาก MT5

Export `GOLD#` H1 เพิ่มอีกอย่างน้อย 1-3 เดือน ถ้าเป็นไปได้

ช่วงแนะนำ:

- `2026-02-01` ถึง `2026-04-01`
- หรืออย่างน้อย `2026-03-01` ถึง `2026-03-15`

ชื่อไฟล์แนะนำ:

- `GOLD_HASH_H1_20260201_20260401_raw_mt5_H1.csv`
- หรือ `GOLD_HASH_H1_20260301_20260315_raw_mt5_H1.csv`

ไฟล์ควรอยู่ที่:

`G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\manual_exports\`

หลัง export ให้เปิดไฟล์ดู 3 แถวแรก โดยควรเป็น H1 เช่น:

- `2026.03.02 01:00`
- `2026.03.02 02:00`
- `2026.03.02 03:00`

ถ้าเป็น `01:00`, `01:01`, `01:02` แปลว่าเป็น M1 ไม่ใช่ H1 และใช้ไม่ได้

### 3. MT5 Symbol/Session Evidence

ถ้าทำได้ ให้เก็บ screenshot หรือ note จาก:

- Market Watch -> `GOLD#`
- Specification / Contract details
- Trading sessions หรือ quote sessions ถ้ามีแสดง

หลักฐานนี้ช่วยบอกว่า broker มีช่วงปิดตลาด/maintenance ช่วงไหน

## โฟลเดอร์หลักฐาน

ให้เก็บไฟล์ไว้ที่:

`G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\manual_gap_evidence\GOLD_HASH_H1\`

โครงสร้างที่แนะนำ:

```text
mt5_artifacts/
  manual_gap_evidence/
    GOLD_HASH_H1/
      screenshots/
      csv/
      notes/
```

ไฟล์ note ที่แนะนำ:

`notes/GOLD_HASH_H1_gap_evidence_notes.md`

ใน note ให้ใส่:

- MT5 terminal ที่ใช้
- Account type: demo
- Symbol exact name: `GOLD#`
- Timeframe: `H1`
- Timezone/server time ถ้ารู้
- วันที่ export
- สรุปว่าช่วง gap มีแท่งใน chart หรือไม่มี

## Pass Criteria สำหรับ Evidence

หลักฐานถือว่าเพียงพอสำหรับกลับมา review policy ถ้า:

- Screenshot เห็นว่าไม่มี H1 bar ในช่วง gap ที่ตรวจ
- CSV export เพิ่มเติมยังแสดง pattern gap คล้ายกันหลายวัน
- Pattern ไม่ใช่ random missing data
- Rule ยังจำกัดเฉพาะ `GOLD#` H1
- ยังมีหลักฐานแยก true missing data ออกจาก session gap

## Fail / Block Criteria

ต้อง block ต่อถ้า:

- screenshot เห็นว่าจริงๆ แล้วมี bar แต่ CSV ขาด
- CSV เพิ่มเติมมี gap แปลกๆ นอกช่วง session
- export เป็น M1 หรือ timeframe ผิด
- ไม่เห็น time axis ชัดเจน
- ไม่สามารถยืนยันว่าเป็น `GOLD#` H1
- evidence มาจาก symbol อื่น เช่น `GOLDm#`, `XAUUSD`, หรือ `GOLD` โดยไม่ได้แยก profile

## สิ่งที่ยังห้ามทำ

- ห้าม approve daily session gap จาก assumption อย่างเดียว
- ห้าม bypass validator
- ห้ามรัน joiner
- ห้ามใช้ผล shadow outcome ที่ validator ยัง reject เป็นหลักฐาน
- ห้ามเริ่ม demo/live
- ห้าม optimize parameter
- ห้ามเพิ่ม lot/risk

## Decision

- `MANUAL_GAP_EVIDENCE_GUIDE_CREATED`
- `DAILY_SESSION_GAP_STILL_NOT_APPROVED`
- `JOINER_STILL_BLOCKED`
- `VALIDATOR_PRODUCTION_NOT_CHANGED`
- `MT5_NOT_RUN_BY_CODEX`
- `STRATEGY_TESTER_NOT_RUN`
- `EA_SOURCE_NOT_CHANGED`
- `PRESETS_NOT_CHANGED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`

## Next Safe Step

Checkpoint BV ควรเกิดหลังจากผู้ใช้ส่งหลักฐาน manual กลับมาแล้วเท่านั้น

ถ้าหลักฐานครบ:

- วิเคราะห์ screenshot/CSV evidence
- rerun offline gap attribution บน CSV ที่ยาวขึ้นได้
- dry-run policy อีกครั้ง
- ยังไม่รัน joiner จนกว่า dry-run verdict เป็น `PASS`

ถ้าหลักฐานยังไม่ครบ:

- gap policy ยังต้อง block
- joiner ยังไม่ควรรัน
