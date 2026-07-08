# Checkpoint BE: PAF Lookahead Bars Manual Export Guide

วันที่จัดทำ: 2026-07-08

## สถานะ

Checkpoint BE เป็นเอกสารคู่มือ manual export สำหรับ `paf_lookahead_bars.csv` เท่านั้น

ไม่มีการรัน MT5 โดย Codex, ไม่มีการรัน Strategy Tester, ไม่มีการแก้ EA/source code, ไม่มีการแก้ presets, ไม่มี optimization, ไม่มีการเพิ่ม lot/risk และไม่มี profitability claim

เอกสารนี้ช่วยให้ผู้ใช้ export ข้อมูล `GOLD#` H1 จาก XM MT5 ด้วยตัวเองอย่างตรวจสอบได้ แล้วจึงค่อยให้ Codex validate/join แบบ offline ใน checkpoint ถัดไป

## เป้าหมายของไฟล์

ไฟล์ที่ต้องการ:

`paf_lookahead_bars.csv`

ใช้สำหรับ offline shadow-outcome analysis ของ PAF diagnostic run:

- RunId: `run_20260707_172236`
- Symbol: `GOLD#`
- Timeframe: `H1`
- Diagnostic range: `2026-03-01` ถึง `2026-03-08`
- Lookahead horizon: `48` H1 bars

ช่วงข้อมูลที่ต้อง export:

- เริ่ม: `2026-03-01 00:00:00`
- สิ้นสุดขั้นต่ำ: `2026-03-10 23:59:59`

ถ้า export ได้ยาวกว่านี้เล็กน้อย เช่นถึง `2026-03-11` ถือว่าใช้ได้ แต่ห้ามตัดให้สั้นกว่าขอบเขตขั้นต่ำ

## วิธี Export จาก MT5 แบบ Manual

ขั้นตอนนี้ให้ผู้ใช้ทำเองใน MT5 ถ้าพร้อม ไม่ใช่ให้ Codex เปิด MT5 อัตโนมัติ:

1. เปิด XM MT5 instance ที่ใช้บัญชี demo เดิม
2. ตรวจว่า Market Watch มี symbol `GOLD#`
3. เปิดหน้าต่าง Symbols ด้วย `Ctrl+U`
4. เลือก `GOLD#`
5. ไปที่แท็บ `Bars`
6. เลือก timeframe เป็น `H1`
7. เลือกช่วงวันที่ให้ครอบคลุม `2026-03-01` ถึงอย่างน้อย `2026-03-10`
8. กด `Request` หรือคำสั่งที่ MT5 ใช้โหลดข้อมูล history
9. กด `Export`
10. บันทึกเป็นไฟล์ CSV เช่น:

`G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\paf_lookahead_bars\run_20260707_172236\paf_lookahead_bars.csv`

ถ้า MT5 UI แสดงเมนูต่างจากนี้ ให้ยึดหลักว่าไฟล์ต้องเป็น `GOLD#` timeframe `H1` และมี OHLC bars ตามช่วงเวลาข้างต้น

## Schema ที่ต้องได้

ไฟล์ CSV ต้องมีข้อมูลที่แปลงเป็น schema นี้ได้:

- `time`
- `open`
- `high`
- `low`
- `close`

รูปแบบเวลาที่ต้องการ:

`YYYY.MM.DD HH:MM:SS`

ตัวอย่าง:

```csv
time,open,high,low,close
2026.03.02 01:00:00,5263.27,5280.66,5257.26,5278.56
```

ถ้า MT5 export ออกมาเป็นชื่อ column หรือรูปแบบเวลาอื่น ยังไม่ต้องแก้ราคาเอง ให้เก็บไฟล์ดิบไว้ก่อน แล้วให้ Codex ช่วยสร้าง checkpoint แปลง schema แบบ offline

## หลักฐานที่ควรเก็บ

เพื่อให้ตรวจสอบที่มาของข้อมูลได้ ควรเก็บ:

- path ของไฟล์ CSV ที่ export
- screenshot หน้าต่าง Symbols/Bars ที่เห็น `GOLD#`, `H1`, และช่วงวันที่
- screenshot หรือ note ว่า MT5 Data Folder คืออะไร
- note ว่าใช้ XM MT5 demo instance เดิม
- note ว่าไม่ได้แก้ราคาเอง
- note ว่าไม่ได้รัน Strategy Tester ในขั้นตอนนี้

## ห้ามทำในขั้นตอนนี้

- ห้ามรัน Strategy Tester เพื่อสร้างผลเทรด
- ห้ามกด optimization
- ห้าม attach EA เพื่อให้เทรด
- ห้ามเปิด market order
- ห้ามเปิด pending order
- ห้าม modify position
- ห้ามแก้ EA/source code
- ห้ามแก้ presets
- ห้ามแก้ราคาใน CSV เพื่อให้ผลดีขึ้น
- ห้ามตีความว่าไฟล์ CSV นี้พิสูจน์กำไร

## Stop Conditions

หยุดและถามก่อน ถ้า:

- หา `GOLD#` ไม่เจอ
- export ได้ symbol อื่น เช่น `GOLDm#`, `XAUUSD`, หรือ `GOLD`
- timeframe ไม่ใช่ `H1`
- date range ไม่ครอบคลุมถึง `2026-03-10 23:59:59`
- CSV ไม่มี OHLC
- timestamp ไม่ดูเหมือน broker/server time ของ MT5
- MT5 เปิดหน้าต่าง Strategy Tester แทน history export
- ไม่แน่ใจว่าไฟล์มาจาก XM MT5 หรือแหล่งอื่น

## หลัง Export แล้วต้องทำอะไร

ส่ง absolute path ของไฟล์ CSV ให้ Codex เช่น:

`G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\paf_lookahead_bars\run_20260707_172236\paf_lookahead_bars.csv`

หลังจากนั้น checkpoint ถัดไปควรเป็น offline validation:

1. รัน `tools/paf_lookahead_bars_validator.py`
2. ถ้า validator ผ่าน จึงรัน `tools/paf_lookahead_joiner.py`
3. สรุป shadow outcome แบบ diagnostic-only

approval phrase สำหรับ offline join ยังคงเป็น:

`Approved to execute Checkpoint BB offline PAF lookahead join with bars CSV <absolute_path_to_csv> for RunId run_20260707_172236.`

## Decision

- `MANUAL_EXPORT_GUIDE_DEFINED`
- `REAL_MARKET_LOOKAHEAD_CSV_STILL_MISSING`
- `OFFLINE_JOIN_NOT_RUN`
- `MT5_NOT_RUN_BY_CODEX`
- `ORDER_PATH_STILL_BLOCKED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`

## Progress Estimate

- Research infrastructure readiness: `69%`
- PAF diagnostic readiness: `69%`
- PAF shadow-outcome readiness: `57%`
- Order implementation readiness: `0%`
- Demo/live readiness: `0%`

ความคืบหน้าหลักที่ยังขาดคือไฟล์ `paf_lookahead_bars.csv` จริงที่ผ่าน validator
