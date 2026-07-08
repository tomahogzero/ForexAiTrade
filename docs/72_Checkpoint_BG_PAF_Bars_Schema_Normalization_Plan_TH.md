# Checkpoint BG: PAF Bars Schema Normalization Plan

วันที่จัดทำ: 2026-07-08

## สถานะ

Checkpoint BG เป็นเอกสารแผน schema normalization สำหรับไฟล์ OHLC bars ที่ export จาก MT5 หรือแหล่งข้อมูลที่ตรวจสอบได้เท่านั้น

ไม่มีการรัน MT5, ไม่มีการรัน Strategy Tester, ไม่มีการแก้ EA/source code, ไม่มีการแก้ presets, ไม่มี optimization, ไม่มีการเพิ่ม lot/risk และไม่มี profitability claim

## เหตุผล

Checkpoint BE ระบุวิธี manual export `paf_lookahead_bars.csv` แล้ว และ Checkpoint BF ระบุ intake/validation gate แล้ว

แต่ในทางปฏิบัติ MT5 อาจ export CSV ออกมาในรูปแบบที่ไม่ตรงกับ schema ที่ validator ต้องการ เช่น:

- date และ time แยก column กัน
- column เป็นตัวพิมพ์ใหญ่ เช่น `OPEN`, `HIGH`, `LOW`, `CLOSE`
- มี column เพิ่ม เช่น tick volume, spread, real volume
- ใช้ delimiter เป็น tab หรือ semicolon
- time format ไม่ใช่ `YYYY.MM.DD HH:MM:SS`

Checkpoint BG จึงกำหนดกติกาแปลง schema แบบ offline เพื่อให้แปลงรูปแบบไฟล์ได้โดยไม่แก้ราคาเองและไม่สร้างข้อมูลใหม่

## Target Normalized Schema

ไฟล์ normalized ที่ validator ใช้ต้องมี columns:

- `time`
- `open`
- `high`
- `low`
- `close`

รูปแบบ `time`:

`YYYY.MM.DD HH:MM:SS`

ตัวอย่าง:

```csv
time,open,high,low,close
2026.03.02 01:00:00,5263.27,5280.66,5257.26,5278.56
```

## Allowed Transformations

อนุญาตเฉพาะการแปลงเชิงรูปแบบ:

- รวม `date` + `time` เป็น `time`
- rename column ให้เป็น lowercase schema
- ตัด column ที่ไม่จำเป็นออก เช่น volume หรือ spread
- แปลง delimiter เป็น comma
- trim ช่องว่างรอบค่า
- แปลง timestamp format โดยไม่เปลี่ยน timezone
- แปลงตัวเลขให้เป็น decimal ที่อ่านได้

## Forbidden Transformations

ห้ามทำ:

- แก้ราคา open/high/low/close
- เติม bar ที่หายเองโดยไม่มี source
- shift timezone เพื่อให้ match โดยไม่มีหลักฐาน
- resample M1/M5 เป็น H1 โดยไม่มี checkpoint แยก
- ใช้ symbol อื่นแทน `GOLD#`
- ใช้ timeframe อื่นแทน `H1`
- ใช้ข้อมูลจาก broker/source อื่นโดยไม่ติดป้าย `NON_BROKER_COMPARABLE`
- ลบ rows ที่ทำให้ผลดูแย่
- เพิ่ม lookahead data เข้า EA decision path

## Raw File Preservation

ถ้า schema ยังไม่ตรง ต้องเก็บไฟล์ raw export ไว้เสมอ เช่น:

- `paf_lookahead_bars_raw.csv`
- `paf_lookahead_bars_normalized.csv`
- `normalization_notes.md`

ไฟล์ raw ห้ามถูก overwrite

## Proposed Future Tool

checkpoint ถัดไปอาจเพิ่ม tool offline ชื่อ:

`tools/paf_bars_schema_normalizer.py`

หน้าที่:

- อ่าน raw CSV
- ตรวจ delimiter
- map column แบบ explicit
- รวม date/time ถ้าจำเป็น
- เขียน normalized CSV เป็น `paf_lookahead_bars.csv`
- สร้าง summary ว่าแปลงอะไรไปบ้าง
- ไม่แก้ราคาและไม่เติมข้อมูลเอง

tool นี้ต้องเป็น offline-only และไม่รัน MT5

## Required Normalization Report

หลัง normalize ต้องมีรายงาน:

- raw file path
- normalized file path
- source symbol ที่ผู้ใช้ระบุ
- source timeframe ที่ผู้ใช้ระบุ
- input columns
- output columns
- delimiter detected
- timestamp transformation
- row count before
- row count after
- dropped columns
- dropped rows ถ้ามี พร้อมเหตุผล
- warnings
- verdict

## Validation After Normalization

หลัง normalize ต้องรัน validator ต่อ:

```powershell
python tools\paf_lookahead_bars_validator.py `
  --bars-csv <absolute_path_to_normalized_paf_lookahead_bars.csv> `
  --shadow-outcomes research\results\paf_shadow_outcomes_all_cases.csv `
  --results-root research\results `
  --symbol GOLD# `
  --timeframe H1 `
  --horizon-bars 48
```

ห้ามรัน joiner ถ้า validator ไม่ผ่าน

## Classification

ใช้ classification ต่อไปนี้:

- `NORMALIZATION_NOT_REQUIRED`
- `NORMALIZATION_REQUIRED`
- `NORMALIZATION_PASS_VALIDATION_PENDING`
- `NORMALIZATION_FAIL_NEEDS_MANUAL_REVIEW`
- `RAW_DATA_NOT_BROKER_COMPARABLE`
- `VALIDATOR_PASS_READY_FOR_JOIN`

## Stop Conditions

หยุดทันทีถ้า:

- raw file ไม่มีอยู่จริง
- ไม่ทราบว่าไฟล์มาจาก `GOLD#` H1 หรือไม่
- column OHLC หาย
- timestamp แปลงไม่ได้
- ต้อง shift timezone แต่ไม่มีหลักฐาน
- ต้องเติม bars ที่หายเอง
- raw file ดูเหมือนถูกแก้ราคา
- มีการเสนอให้ใช้ผลเป็น proof of profitability
- มีการพยายามข้าม validator ไป joiner

## Decision

- `SCHEMA_NORMALIZATION_PLAN_DEFINED`
- `NORMALIZER_TOOL_NOT_IMPLEMENTED`
- `REAL_MARKET_LOOKAHEAD_CSV_STILL_MISSING`
- `VALIDATOR_NOT_RUN`
- `JOINER_NOT_RUN`
- `MT5_NOT_RUN`
- `ORDER_PATH_STILL_BLOCKED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`

## Progress Estimate

- Research infrastructure readiness: `71%`
- PAF diagnostic readiness: `70%`
- PAF shadow-outcome readiness: `59%`
- Order implementation readiness: `0%`
- Demo/live readiness: `0%`

ขั้นต่อไปที่ปลอดภัยคือ implement offline schema normalizer หรือรอไฟล์ CSV จริงจากผู้ใช้แล้วทำ intake/validation ตาม Checkpoint BF
