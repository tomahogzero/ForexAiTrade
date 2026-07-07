# Checkpoint BD: PAF Lookahead Bars Export Approval

วันที่จัดทำ: 2026-07-07

## สถานะ

Checkpoint BD เป็นเอกสารอนุมัติและแผน preflight สำหรับการสร้างไฟล์ `paf_lookahead_bars.csv` จริงในอนาคตเท่านั้น

ไม่มีการรัน MT5, ไม่มีการรัน Strategy Tester, ไม่มีการแก้ EA/source code, ไม่มีการแก้ presets, ไม่มี optimization, ไม่มีการเพิ่ม lot/risk และไม่มี profitability claim

## เหตุผล

Checkpoint AX ยืนยันแล้วว่า PAF diagnostic logging fields ปรากฏครบใน `ea_mirror.log` และไม่มี order เกิดขึ้น แต่ shadow outcome ยังติดสถานะ `BLOCKED_BY_MISSING_LOOKAHEAD_DATA`

Checkpoint AZ เพิ่ม offline joiner แล้ว และ Checkpoint BC เพิ่ม validator แล้ว แต่ยังไม่มี `paf_lookahead_bars.csv` จากข้อมูลตลาดจริงที่ตรวจสอบแหล่งที่มาได้

ดังนั้นก่อนทำ offline join จริง ต้องล็อกวิธีสร้าง/export bar data ให้ปลอดภัยและตรวจสอบซ้ำได้ก่อน

## Target Context

ข้อมูล bar ที่ต้องการใช้กับ shadow outcome ชุดแรก:

- RunId: `run_20260707_172236`
- Case: `GOLD_HASH_H1_PAF_FIELD_VERIFY_AX_ax_field_verify_20260301_20260308`
- Symbol: `GOLD#`
- Timeframe: `H1`
- Diagnostic date range: `2026-03-01` ถึง `2026-03-08`
- Required lookahead horizon: `48` H1 bars

ช่วง bar ที่ต้องครอบคลุมอย่างน้อย:

- เริ่ม: `2026-03-01 00:00:00`
- สิ้นสุดขั้นต่ำ: `2026-03-10 23:59:59`

ถ้าใช้ช่วงอื่น ต้องมี checkpoint ใหม่อธิบายเหตุผล และห้ามเลือกช่วงย้อนหลังเพื่อให้ผลดูดี

## Approved Data Source Requirement

แหล่งข้อมูลที่อนุญาตสำหรับไฟล์จริงควรเป็นหนึ่งในนี้เท่านั้น:

- Export จาก XM MT5 history ของ symbol `GOLD#` timeframe `H1`
- ไฟล์ OHLC ที่พิสูจน์ได้ว่าใช้ broker/server time เดียวกับ diagnostic run

ห้ามถือว่าข้อมูลจาก broker อื่น, symbol อื่น, หรือ timezone อื่นเทียบเท่า `GOLD#` ของ XM โดยอัตโนมัติ

ถ้าจำเป็นต้องใช้ข้อมูลจากแหล่งอื่นเพื่อทดสอบ parser ให้ติดป้ายชัดเจนว่า `NON_BROKER_COMPARABLE` และห้ามใช้เป็นข้อสรุป strategy quality

## Required CSV Schema

ไฟล์เป้าหมาย:

`paf_lookahead_bars.csv`

columns ที่ต้องมี:

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

## Preflight Evidence Required Before Export

ก่อน export หรือสร้างไฟล์จริง ต้องบันทึกหลักฐานต่อไปนี้:

- terminal64.exe path ที่จะใช้ ถ้ามีการใช้ MT5
- MT5 data folder จาก File > Open Data Folder
- ยืนยันว่า symbol เป็น `GOLD#`
- ยืนยัน timeframe เป็น `H1`
- ยืนยันว่า history ครอบคลุม `2026-03-01` ถึงอย่างน้อย `2026-03-10 23:59:59`
- ยืนยันว่า timestamp เป็น broker/server time เดียวกับ diagnostic logs
- output folder ที่จะเขียนไฟล์ CSV
- วิธีตรวจว่าการ export ไม่ได้เปลี่ยน timezone เอง
- วิธีตรวจว่าไม่มีการเติม/แก้ราคาเองเพื่อให้ผลดีขึ้น

## Stop Conditions

หยุดทันทีถ้าเจอเงื่อนไขใดเงื่อนไขหนึ่ง:

- symbol ไม่ใช่ `GOLD#`
- timeframe ไม่ใช่ `H1`
- coverage ไม่ถึง lookahead horizon 48 H1 bars หลัง diagnostic event ล่าสุด
- timestamp ไม่ match กับ event time จาก shadow outcomes
- data source ไม่ชัดเจนว่าเป็น XM/broker-specific
- ใช้ข้อมูลจาก broker อื่นแต่ไม่ได้ติดป้าย `NON_BROKER_COMPARABLE`
- ต้องเปิด MT5 หรือ Strategy Tester โดยไม่มี approval แยก
- มีการแก้ EA/source code หรือ presets
- มี market order, pending order, หรือ position modification
- มี optimization
- มีการเพิ่ม lot/risk
- มีการตีความผลเป็นกำไรหรืออนุมัติ demo/live

## Validator Required Before Join

หลังได้ `paf_lookahead_bars.csv` แล้ว ต้องรัน validator ก่อน join:

```powershell
python tools\paf_lookahead_bars_validator.py `
  --bars-csv <absolute_path_to_paf_lookahead_bars.csv> `
  --shadow-outcomes research\results\paf_shadow_outcomes_all_cases.csv `
  --results-root research\results `
  --symbol GOLD# `
  --timeframe H1 `
  --horizon-bars 48
```

ถ้า validator ไม่ผ่าน ห้ามรัน joiner และต้องทำ diagnosis ก่อน

## Future Approval Phrase For Export

ถ้าจะให้ Codex ทำ one-time export หรือเตรียม bar CSV จริง ต้องใช้ approval phrase แยก:

`Approved to execute Checkpoint BE one-time GOLD# H1 bars export for PAF lookahead with date range 2026-03-01 to 2026-03-10 using verified XM MT5 history only.`

approval นี้ยังไม่อนุญาตให้รัน Strategy Tester, ไม่อนุญาต order, ไม่อนุญาต optimization และไม่อนุญาตตีความ profitability

## Future Approval Phrase For Offline Join

หลังมี CSV ที่ validate ผ่านแล้ว ถ้าจะรัน offline joiner ให้ใช้ approval phrase เดิม:

`Approved to execute Checkpoint BB offline PAF lookahead join with bars CSV <absolute_path_to_csv> for RunId run_20260707_172236.`

## Decision

- `BARS_EXPORT_APPROVAL_PACKAGE_DEFINED`
- `REAL_MARKET_LOOKAHEAD_CSV_STILL_MISSING`
- `OFFLINE_JOIN_NOT_RUN`
- `MT5_STILL_BLOCKED_UNTIL_EXPLICIT_EXPORT_APPROVAL`
- `ORDER_PATH_STILL_BLOCKED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`

## Next Safe Step

ถ้าผู้ใช้พร้อมให้สร้าง/export bar CSV จริง ให้ใช้ approval phrase ของ Checkpoint BE ด้านบน

ถ้าผู้ใช้มีไฟล์ `paf_lookahead_bars.csv` อยู่แล้ว ให้ส่ง absolute path แล้วค่อยใช้ approval phrase ของ Checkpoint BB เพื่อรัน validator และ offline joiner
