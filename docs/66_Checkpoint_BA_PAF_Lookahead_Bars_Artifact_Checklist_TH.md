# Checkpoint BA: PAF Lookahead Bars Artifact Checklist

วันที่จัดทำ: 2026-07-07

## สถานะ

Checkpoint BA เป็น documentation / artifact-checklist-only checkpoint

ไม่มีการแก้ EA/source code, ไม่มีการแก้ presets, ไม่มีการแก้ strategy logic, ไม่มีการรัน MT5, ไม่มีการรัน Strategy Tester, ไม่มี optimization, ไม่มีการเพิ่ม lot/risk และไม่มี profitability claim

## เหตุผล

Checkpoint AZ เพิ่ม `tools/paf_lookahead_joiner.py` แล้ว แต่ยังไม่มี `paf_lookahead_bars.csv` ที่ตรวจสอบแหล่งที่มาได้

ถ้าสร้าง bar CSV แบบไม่ตรวจสอบ อาจเกิดปัญหา:

- timezone ไม่ตรงกับ `ea_mirror.log`
- symbol ไม่ตรงกับ diagnostic run
- timeframe ไม่ตรงกับ diagnostic run
- bars ขาดหายช่วง weekend/session
- มี future leak กลับเข้า EA decision path
- สรุปผลผิดจาก sample น้อยหรือข้อมูลไม่ตรง

BA จึงกำหนด checklist ก่อนสร้างหรือใช้ `paf_lookahead_bars.csv`

## Scope ของข้อมูลที่ต้องการ

สำหรับผล AX:

- RunId: `run_20260707_172236`
- Case: `GOLD_HASH_H1_PAF_FIELD_VERIFY_AX_ax_field_verify_20260301_20260308`
- Symbol: `GOLD#`
- Timeframe: `H1`
- Diagnostic date range: `2026-03-01` ถึง `2026-03-08`

แต่เพราะ joiner ใช้ horizon สูงสุด 48 bars หลัง event จึงต้องมี bar data หลังจุด diagnostic ล่าสุดด้วย

ช่วงข้อมูลที่ควรเตรียม:

- เริ่ม: `2026-03-01 00:00:00`
- สิ้นสุดอย่างน้อย: `2026-03-10 23:59:59`

หากใช้ window อื่น ต้องระบุเหตุผลและห้ามใช้เพื่อเลือกผลที่ดูดี

## Required CSV Schema

ไฟล์ชื่อที่แนะนำ:

`paf_lookahead_bars.csv`

ต้องมี columns:

- `time`
- `open`
- `high`
- `low`
- `close`

รูปแบบเวลาที่แนะนำ:

`YYYY.MM.DD HH:MM:SS`

ตัวอย่าง:

```csv
time,open,high,low,close
2026.03.02 01:00:00,5263.27,5280.66,5257.26,5278.56
```

ไฟล์ schema ตัวอย่าง:

`research/templates/paf_lookahead_bars_schema.csv`

## Data Source Checklist

ก่อนใช้ `paf_lookahead_bars.csv` ต้องตอบให้ครบ:

- แหล่งข้อมูลมาจากไหน
- เป็น broker/server time เดียวกับ XM MT5 หรือไม่
- symbol เป็น `GOLD#` จริงหรือไม่
- timeframe เป็น `H1` จริงหรือไม่
- ช่วงเวลา cover diagnostic events และ lookahead horizon หรือไม่
- มี missing bars หรือไม่
- open/high/low/close เป็นตัวเลข decimal ปกติหรือไม่
- ไม่มีการปรับ timezone เองโดยไม่บันทึกเหตุผล
- ไม่มีการแก้ราคาเองเพื่อให้ผลดูดี

## Timestamp Alignment Checklist

ต้องตรวจว่า event time จาก `paf_shadow_outcomes_all_cases.csv` match กับ bar timestamp ได้

อย่างน้อยต้องตรวจ event สำคัญจาก AX:

- `2026.03.02 01:00:00`
- `2026.03.02 10:00:00`
- `2026.03.02 23:00:00`
- `2026.03.03 01:00:00`

ถ้า exact match ไม่ได้ ให้หยุดและทำ diagnosis ก่อน ห้ามเลื่อนเวลาเองเพื่อให้ match โดยไม่มีเอกสารรองรับ

## Guardrails

การสร้างหรือใช้ `paf_lookahead_bars.csv` ต้องยืนยัน:

- ไม่รัน MT5 เว้นแต่มี approval phrase แยก
- ไม่รัน Strategy Tester เว้นแต่มี approval phrase แยก
- ไม่เปิด market order
- ไม่เปิด pending order
- ไม่ modify position
- ไม่ optimize parameter
- ไม่เพิ่ม lot/risk
- ไม่ claim profitability
- ไม่ใช้ lookahead data ใน EA decision path
- ไม่ใช้ผลเพื่อ approve demo/live trading

## Stop Conditions

หยุดทันทีถ้า:

- symbol ไม่ใช่ `GOLD#`
- timeframe ไม่ใช่ `H1`
- timestamp ไม่ตรงกับ diagnostic event
- bar data ไม่ cover 48 bars หลัง event สำคัญ
- CSV missing required columns
- มีการเปิด MT5/Strategy Tester โดยไม่ได้ approval
- มีการแก้ EA/source หรือ presets โดยไม่อยู่ใน checkpoint scope
- มีการตีความผลเป็นกำไรหรือใช้เพื่อเพิ่ม risk

## Future Approval Phrase

ถ้าจะให้ Codex รัน offline joiner กับ bar CSV ที่เตรียมไว้ ต้องใช้ approval phrase แบบนี้:

`Approved to execute Checkpoint BB offline PAF lookahead join with bars CSV <absolute_path_to_csv> for RunId run_20260707_172236.`

การ approval นี้อนุญาตเฉพาะ offline Python joiner เท่านั้น ไม่อนุญาต MT5, Strategy Tester, order, optimization, หรือ risk increase

## Expected Future Outputs

หลังรัน joiner ควรได้:

- `research/results/paf_shadow_outcomes_enriched.csv`
- `research/results/paf_lookahead_join_summary.json`
- `research/results/paf_lookahead_join_summary.md`

ผลลัพธ์ต้องอ่านเป็น diagnostic-only:

- ดูว่า data join สำเร็จหรือไม่
- ดู MFE/MAE เบื้องต้น
- ดู outcome label แบบ hypothetical เท่านั้น
- ไม่สรุป profitability
- ไม่ approve order path

## Decision

- `LOOKAHEAD_BARS_CHECKLIST_DEFINED`
- `OFFLINE_JOIN_NOT_RUN`
- `MT5_STILL_BLOCKED`
- `ORDER_PATH_STILL_BLOCKED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`

## Next Safe Step

Checkpoint BB ควรเกิดขึ้นหลังมี `paf_lookahead_bars.csv` ที่ผ่าน checklist แล้วเท่านั้น

ถ้ายังไม่มีไฟล์ CSV ให้เตรียม data source ก่อน ไม่ควรเดาหรือสร้างข้อมูลจำลองเพื่อสรุป strategy quality
