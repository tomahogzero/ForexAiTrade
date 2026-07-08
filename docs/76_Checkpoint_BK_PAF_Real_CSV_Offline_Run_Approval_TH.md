# Checkpoint BK: PAF Real CSV Offline Run Approval Package

วันที่จัดทำ: 2026-07-08

## สถานะ

Checkpoint BK เป็นเอกสารอนุมัติล่วงหน้าสำหรับการรัน offline pipeline กับไฟล์ CSV จริงของ `GOLD#` H1 เท่านั้น

Checkpoint นี้ยังไม่รัน MT5, ไม่รัน Strategy Tester, ไม่รัน pipeline กับข้อมูลจริง, ไม่แก้ EA/source code, ไม่แก้ presets, ไม่ optimize, ไม่เพิ่ม lot/risk และไม่ claim profitability

## เป้าหมาย

หลัง Checkpoint BJ เรามี `tools/paf_offline_pipeline_runner.py` ที่ทดสอบผ่านกับ synthetic fixture แล้ว ขั้นตอนปลอดภัยถัดไปคือเตรียมกติกาให้ชัดก่อนรันกับไฟล์ CSV จริงจาก XM MT5

เป้าหมายของการรันในอนาคตคือ:

- รับไฟล์ bars CSV จริงของ `GOLD#` H1
- normalize ถ้าไฟล์เป็น raw MT5-style CSV
- validate schema, timestamp, coverage และ event matching
- join กับ PAF diagnostic shadow rows ของ RunId ที่กำหนด
- สรุป shadow outcome แบบ offline-only

ผลลัพธ์นี้ยังเป็นการวิเคราะห์ย้อนหลัง ไม่ใช่สัญญาณเทรดจริง และไม่ใช่หลักฐานกำไรในอนาคต

## Target Context

- Source diagnostic RunId: `run_20260707_172236`
- Symbol: `GOLD#`
- Timeframe: `H1`
- Diagnostic window: `2026-03-01` ถึง `2026-03-08`
- Required lookahead coverage: อย่างน้อยถึง `2026-03-10 23:59:59`
- Expected shadow input: `research/results/paf_shadow_outcomes_all_cases.csv`
- Offline runner: `tools/paf_offline_pipeline_runner.py`

## Allowed Input

อนุญาต input ได้ 2 แบบเท่านั้น:

1. Raw MT5-style CSV เช่นมี column `<DATE>`, `<TIME>`, `<OPEN>`, `<HIGH>`, `<LOW>`, `<CLOSE>`
2. Normalized CSV เช่นมี column `time`, `open`, `high`, `low`, `close`

ไฟล์ต้องเป็นข้อมูล `GOLD#` H1 จาก XM MT5 หรือแหล่งที่ผู้ใช้ยืนยันว่าเทียบกับ XM MT5 ได้เท่านั้น ถ้าเป็นข้อมูลจาก broker/source อื่น ต้องจัดเป็น `NON_BROKER_COMPARABLE_DIAGNOSTIC_ONLY`

## Preflight Checklist

ก่อนรัน offline pipeline ในอนาคต ต้องยืนยัน:

- path เป็น absolute path
- ไฟล์มีอยู่จริงและอ่านได้
- raw file ต้องถูกเก็บไว้ ไม่เขียนทับต้นฉบับ
- source เป็น `GOLD#` H1 จาก XM MT5 หรือมีคำอธิบาย source ชัดเจน
- coverage ต้องครอบคลุม diagnostic window และ lookahead horizon อย่างน้อย 48 แท่ง H1
- ไม่มีการแก้ราคา OHLC ด้วยมือ
- output folder แยกชัดเจนจาก self-test เดิม
- ใช้ runner แบบ offline เท่านั้น
- ไม่เปิด MT5
- ไม่เปิด Strategy Tester
- ไม่ส่งคำสั่ง order
- ไม่แก้ EA/source code หรือ presets

## Example Commands For Future Approval

ตัวอย่างเมื่อผู้ใช้ส่ง raw MT5-style CSV:

```powershell
python tools\paf_offline_pipeline_runner.py `
  --raw-csv <absolute_path_to_raw_csv> `
  --shadow-outcomes research\results\paf_shadow_outcomes_all_cases.csv `
  --results-root research\results\checkpoint_bk_real_csv_pipeline `
  --symbol GOLD# `
  --timeframe H1 `
  --horizon-bars 48 `
  --join-horizons 6,12,24,48 `
  --tp-atr-multiple 1.5 `
  --sl-atr-multiple 1.0
```

ตัวอย่างเมื่อผู้ใช้ส่ง normalized CSV:

```powershell
python tools\paf_offline_pipeline_runner.py `
  --bars-csv <absolute_path_to_normalized_csv> `
  --shadow-outcomes research\results\paf_shadow_outcomes_all_cases.csv `
  --results-root research\results\checkpoint_bk_real_csv_pipeline `
  --symbol GOLD# `
  --timeframe H1 `
  --horizon-bars 48 `
  --join-horizons 6,12,24,48 `
  --tp-atr-multiple 1.5 `
  --sl-atr-multiple 1.0
```

คำสั่งเหล่านี้ยังไม่ถูกรันใน Checkpoint BK

## Stop Conditions

ต้องหยุดทันทีถ้า:

- path ไม่ใช่ absolute path
- ไฟล์ไม่มีอยู่จริงหรืออ่านไม่ได้
- source symbol/timeframe ไม่ตรงกับ `GOLD#` H1
- coverage ไม่พอถึง lookahead horizon
- normalizer fail
- validator fail
- joiner fail
- มีการแก้ OHLC แบบไม่มีหลักฐาน
- มีคำขอให้ใช้ผลนี้เป็น proof of profitability
- มีคำขอให้เปิด order path, pending order, market order หรือ position modification
- มีคำขอให้รัน MT5/Strategy Tester ใน checkpoint นี้
- มีคำขอให้ optimize หรือเพิ่ม lot/risk

## Future Approval Phrase

การรันจริงยังถูก block จนกว่าผู้ใช้จะอนุมัติด้วยข้อความลักษณะนี้:

`Approved to execute Checkpoint BL offline PAF pipeline on real GOLD# H1 bars CSV <absolute_path_to_csv> for RunId run_20260707_172236.`

คำอนุมัตินี้อนุญาตเฉพาะ offline runner กับไฟล์ CSV ที่ระบุเท่านั้น ไม่อนุญาต MT5, Strategy Tester, market order, pending order, position modification, optimization, lot/risk increase หรือ profitability claim

## Expected Outputs For Future Run

เมื่อรันในอนาคต ควรได้ artifact เช่น:

- normalized bars CSV ถ้าจำเป็น
- normalization summary JSON/Markdown
- validation summary JSON/Markdown
- enriched shadow outcome CSV
- lookahead join summary JSON/Markdown
- offline pipeline runner summary JSON/Markdown

## Guardrails

- ไม่รัน MT5
- ไม่รัน Strategy Tester
- ไม่เปิด market order
- ไม่เปิด pending order
- ไม่ modify position
- ไม่แก้ EA/source code
- ไม่แก้ presets
- ไม่ optimize
- ไม่เพิ่ม lot/risk
- ไม่ claim profitability
- ไม่ใช้ lookahead data ใน EA decision path

## Decision

- `REAL_CSV_OFFLINE_RUN_APPROVAL_PACKAGE_DEFINED`
- `REAL_MARKET_LOOKAHEAD_CSV_STILL_MISSING`
- `OFFLINE_RUN_NOT_EXECUTED`
- `MT5_NOT_RUN`
- `STRATEGY_TESTER_NOT_RUN`
- `ORDER_PATH_STILL_BLOCKED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`

## Progress Estimate

- Research infrastructure readiness: `77%`
- PAF diagnostic readiness: `70%`
- PAF shadow-outcome readiness: `66%`
- Order implementation readiness: `0%`
- Demo/live readiness: `0%`

ขั้นตอนถัดไปที่ปลอดภัยคือให้ผู้ใช้ส่ง absolute path ของไฟล์ `GOLD#` H1 CSV จริง แล้วค่อยอนุมัติ Checkpoint BL เพื่อรัน offline pipeline เท่านั้น
