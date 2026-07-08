# Checkpoint BF: PAF Lookahead Bars CSV Intake Validation

วันที่จัดทำ: 2026-07-08

## สถานะ

Checkpoint BF เป็นเอกสารกำหนดขั้นตอนรับไฟล์และตรวจสอบ `paf_lookahead_bars.csv` ก่อนนำไปใช้กับ offline joiner เท่านั้น

ไม่มีการรัน MT5, ไม่มีการรัน Strategy Tester, ไม่มีการแก้ EA/source code, ไม่มีการแก้ presets, ไม่มี optimization, ไม่มีการเพิ่ม lot/risk และไม่มี profitability claim

## เหตุผล

หลัง Checkpoint BE ผู้ใช้อาจ export ไฟล์ `paf_lookahead_bars.csv` จาก XM MT5 เองได้แล้ว แต่ก่อนนำไฟล์ไป join กับ PAF shadow outcomes ต้องมี intake gate ชัดเจน

เป้าหมายคือป้องกันปัญหาเหล่านี้:

- ไฟล์เป็นคนละ symbol เช่น `GOLDm#`, `XAUUSD`, หรือ `GOLD`
- timeframe ไม่ใช่ `H1`
- date coverage ไม่พอสำหรับ lookahead 48 bars
- timestamp ไม่ตรงกับ event time จาก PAF diagnostics
- CSV schema ไม่ตรงกับที่ parser ต้องการ
- ใช้ข้อมูลจาก broker/source อื่นโดยไม่ติดป้าย
- เอาไฟล์ที่ไม่ผ่าน validator ไปสรุปเป็น strategy quality

## Target CSV

ไฟล์ที่ต้องการ:

`paf_lookahead_bars.csv`

บริบทที่ต้อง match:

- RunId: `run_20260707_172236`
- Symbol: `GOLD#`
- Timeframe: `H1`
- Diagnostic range: `2026-03-01` ถึง `2026-03-08`
- Required coverage: `2026-03-01 00:00:00` ถึงอย่างน้อย `2026-03-10 23:59:59`
- Lookahead horizon: `48` H1 bars

## Intake Checklist

เมื่อผู้ใช้ส่ง path ของ CSV มา ต้องตรวจให้ครบ:

- path เป็น absolute path
- ไฟล์มีอยู่จริง
- ไฟล์อ่านได้
- ไฟล์ไม่ใช่ zip หรือ binary
- มีข้อมูล OHLC
- ระบุได้ว่า data source มาจาก XM MT5 `GOLD#` H1
- มีหลักฐานหรือ note ว่าไม่ได้แก้ราคาเอง
- ถ้า schema ยังไม่ตรง ต้องเก็บ raw CSV ไว้และทำ schema-normalization แบบ offline เท่านั้น

## Validation Command

ใช้ validator ที่มีอยู่แล้ว:

```powershell
python tools\paf_lookahead_bars_validator.py `
  --bars-csv <absolute_path_to_paf_lookahead_bars.csv> `
  --shadow-outcomes research\results\paf_shadow_outcomes_all_cases.csv `
  --results-root research\results `
  --symbol GOLD# `
  --timeframe H1 `
  --horizon-bars 48
```

การรัน validator เป็น offline Python analysis เท่านั้น ไม่ใช่ MT5, ไม่ใช่ Strategy Tester และไม่ใช่ trading run

## Required Validation Outputs

หลัง validation ต้องมีหรือสรุปได้:

- validation verdict
- bar count
- event count
- matched event count
- missing event count
- gap count
- first bar time
- last bar time
- whether horizon coverage is sufficient
- whether schema is usable
- whether data source remains broker-comparable

## Classification

ผล intake/validation ต้องจัดเป็นหนึ่งในนี้:

- `INTAKE_BLOCKED_NO_FILE`
- `INTAKE_BLOCKED_UNREADABLE_FILE`
- `SCHEMA_CONVERSION_REQUIRED`
- `VALIDATOR_FAIL_NEEDS_FIX`
- `NON_BROKER_COMPARABLE_DIAGNOSTIC_ONLY`
- `VALIDATOR_PASS_READY_FOR_JOIN`

ห้ามใช้คำว่า ready for order, ready for demo, หรือ proof of profitability

## Join Gate

ห้ามรัน `tools/paf_lookahead_joiner.py` ถ้า validator ไม่ได้สถานะ:

`VALIDATOR_PASS_READY_FOR_JOIN`

ถ้า validator fail ต้องทำ diagnosis หรือ schema conversion checkpoint ก่อน

## Stop Conditions

หยุดทันทีถ้า:

- path ไม่ใช่ absolute path
- ไฟล์ไม่มีอยู่จริง
- symbol/timeframe/source ไม่ชัดเจน
- ข้อมูลไม่ครอบคลุมถึง `2026-03-10 23:59:59`
- timestamp ไม่ match diagnostic events
- missing event count สูงจนทำให้ join ไม่น่าเชื่อถือ
- มีการแก้ราคาเอง
- มีการเสนอให้เพิ่ม lot/risk
- มีการตีความผล validator เป็นกำไร
- มีการพยายามใช้ข้อมูล lookahead ใน EA decision path

## Future Approval Phrase

ถ้าผู้ใช้มีไฟล์ CSV และต้องการให้ Codex รัน offline validation กับ joiner ให้ใช้:

`Approved to execute Checkpoint BB offline PAF lookahead join with bars CSV <absolute_path_to_csv> for RunId run_20260707_172236.`

แต่ Codex ต้องรัน validator ก่อนเสมอ ถ้า validator ไม่ผ่าน ให้หยุดและไม่รัน joiner

## Decision

- `CSV_INTAKE_VALIDATION_GATE_DEFINED`
- `REAL_MARKET_LOOKAHEAD_CSV_STILL_MISSING`
- `VALIDATOR_NOT_RUN`
- `JOINER_NOT_RUN`
- `MT5_NOT_RUN`
- `ORDER_PATH_STILL_BLOCKED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`

## Progress Estimate

- Research infrastructure readiness: `70%`
- PAF diagnostic readiness: `70%`
- PAF shadow-outcome readiness: `58%`
- Order implementation readiness: `0%`
- Demo/live readiness: `0%`

ขั้นต่อไปที่ปลดล็อกงานจริงคือผู้ใช้ส่ง absolute path ของ `paf_lookahead_bars.csv` หรืออนุมัติ checkpoint แยกให้ Codex ทำ one-time bars export
