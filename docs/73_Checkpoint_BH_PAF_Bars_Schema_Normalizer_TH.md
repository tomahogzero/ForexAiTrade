# Checkpoint BH: PAF Bars Schema Normalizer

วันที่จัดทำ: 2026-07-08

## สถานะ

Checkpoint BH เพิ่มเครื่องมือ offline สำหรับ normalize schema ของไฟล์ OHLC bars ที่ export จาก MT5 หรือแหล่งข้อมูลที่ตรวจสอบได้

ไม่มีการรัน MT5, ไม่มีการรัน Strategy Tester, ไม่มีการแก้ EA/source code, ไม่มีการแก้ presets, ไม่มี optimization, ไม่มีการเพิ่ม lot/risk และไม่มี profitability claim

## Files Added

- `tools/paf_bars_schema_normalizer.py`
- `research/selftests/checkpoint_bh/paf_lookahead_bars_raw_mt5_style.csv`
- `research/selftests/checkpoint_bh/paf_shadow_outcomes_fixture.csv`
- `research/selftests/checkpoint_bh/output/paf_lookahead_bars.csv`
- `research/selftests/checkpoint_bh/output/paf_lookahead_bars_raw.csv`
- `research/selftests/checkpoint_bh/output/paf_bars_schema_normalization_summary.json`
- `research/selftests/checkpoint_bh/output/paf_bars_schema_normalization_summary.md`
- `research/selftests/checkpoint_bh/output/paf_lookahead_bars_validation_summary.json`
- `research/selftests/checkpoint_bh/output/paf_lookahead_bars_validation_summary.md`
- `docs/73_Checkpoint_BH_PAF_Bars_Schema_Normalizer_TH.md`
- `docs/ai/tasks/checkpoint-bh-paf-bars-schema-normalizer.md`

## เหตุผล

Checkpoint BG กำหนดแผน schema normalization แล้ว แต่ยังไม่มี tool

เมื่อผู้ใช้ export history จาก MT5 จริง ไฟล์อาจออกมาเป็นรูปแบบเช่น:

- `<DATE>` และ `<TIME>` แยก column
- `<OPEN>`, `<HIGH>`, `<LOW>`, `<CLOSE>` เป็นชื่อแบบ MT5
- delimiter เป็น tab
- มี column เพิ่ม เช่น tick volume, volume, spread

tool นี้ช่วยแปลงไฟล์ raw export ให้เป็น schema:

`time,open,high,low,close`

โดยไม่แก้ราคาเองและไม่เติมข้อมูลเอง

## Tool

`tools/paf_bars_schema_normalizer.py`

หน้าที่:

- detect delimiter แบบ auto
- map column แบบ conservative
- รวม `<DATE>` + `<TIME>` เป็น `time`
- rename OHLC columns เป็น lowercase schema
- ตัด column ที่ไม่จำเป็นออก
- preserve raw CSV copy
- เขียน normalized CSV
- เขียน JSON/Markdown summary

## Guardrails ของ Tool

tool นี้:

- ไม่รัน MT5
- ไม่รัน Strategy Tester
- ไม่เปิด market order
- ไม่เปิด pending order
- ไม่ modify position
- ไม่แก้ OHLC price
- ไม่เติม missing bars
- ไม่ shift timezone โดยไม่มีหลักฐาน
- ไม่ optimize
- ไม่ claim profitability

ถ้า row ใด parse timestamp หรือ OHLC ไม่ได้ tool จะให้ verdict `FAIL` แทนการแอบข้ามข้อมูล

## Self-Test

ใช้ fixture จำลอง MT5-style export:

`research/selftests/checkpoint_bh/paf_lookahead_bars_raw_mt5_style.csv`

schema ตัวอย่าง:

```csv
<DATE>	<TIME>	<OPEN>	<HIGH>	<LOW>	<CLOSE>	<TICKVOL>	<VOL>	<SPREAD>
2026.03.01	00:00:00	100.00	101.00	99.00	100.00	10	0	20
```

Command:

```powershell
python tools\paf_bars_schema_normalizer.py `
  --raw-csv research\selftests\checkpoint_bh\paf_lookahead_bars_raw_mt5_style.csv `
  --output-csv research\selftests\checkpoint_bh\output\paf_lookahead_bars.csv `
  --results-root research\selftests\checkpoint_bh\output `
  --source-symbol GOLD# `
  --source-timeframe H1
```

Result:

- normalization verdict: `PASS`
- rows before: `4`
- rows after: `4`
- invalid rows: `0`
- delimiter detected: tab
- raw preserved copy created

## Validator Follow-Up

นำ normalized CSV ไปผ่าน validator เดิม:

```powershell
python tools\paf_lookahead_bars_validator.py `
  --bars-csv research\selftests\checkpoint_bh\output\paf_lookahead_bars.csv `
  --shadow-outcomes research\selftests\checkpoint_bh\paf_shadow_outcomes_fixture.csv `
  --results-root research\selftests\checkpoint_bh\output `
  --symbol GOLD# `
  --timeframe H1 `
  --horizon-bars 1
```

Result:

- validation verdict: `PASS`
- bar count: `4`
- event count: `2`
- matched events: `2`
- missing events: `0`
- gap count: `0`

## Limitations

- self-test ใช้ข้อมูลจำลอง ไม่ใช่ข้อมูลตลาดจริง
- tool ยังไม่พิสูจน์ว่า strategy ดีหรือไม่
- tool ยังไม่ทำ lookahead join
- tool ยังไม่อนุญาต order path
- ถ้า raw file จริงมี timezone หรือ symbol ไม่ชัด ต้องหยุดและทำ diagnosis ก่อน

## Decision

- `SCHEMA_NORMALIZER_TOOL_ADDED`
- `SCHEMA_NORMALIZER_SELFTEST_PASS`
- `NORMALIZED_OUTPUT_VALIDATOR_PASS_ON_SYNTHETIC_FIXTURE`
- `REAL_MARKET_LOOKAHEAD_CSV_STILL_MISSING`
- `JOINER_NOT_RUN_ON_REAL_DATA`
- `MT5_NOT_RUN`
- `ORDER_PATH_STILL_BLOCKED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`

## Progress Estimate

- Research infrastructure readiness: `73%`
- PAF diagnostic readiness: `70%`
- PAF shadow-outcome readiness: `61%`
- Order implementation readiness: `0%`
- Demo/live readiness: `0%`

ขั้นต่อไปที่ปลอดภัยคือรับไฟล์ raw/normalized CSV จริงจากผู้ใช้ แล้วรัน intake, normalization ถ้าจำเป็น, validator และค่อยพิจารณา offline join
