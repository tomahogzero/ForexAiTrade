# Checkpoint BC: PAF Lookahead Bars Validator

วันที่จัดทำ: 2026-07-07

## สถานะ

Checkpoint BC เพิ่มเครื่องมือ offline สำหรับ validate `paf_lookahead_bars.csv` ก่อนนำไปใช้กับ `tools/paf_lookahead_joiner.py`

ไม่มีการรัน MT5, ไม่มีการรัน Strategy Tester, ไม่มีการแก้ EA/source code, ไม่มีการแก้ presets, ไม่มี optimization, ไม่มีการเพิ่ม lot/risk และไม่มี profitability claim

## เหตุผล

หลัง Checkpoint BA เรายังขาดวิธีตรวจว่า bar CSV ที่ผู้ใช้หรือระบบเตรียมมานั้น:

- มี schema ถูกต้องหรือไม่
- timestamp ตรงกับ diagnostic event หรือไม่
- coverage เพียงพอกับ lookahead horizon หรือไม่
- มี gap ที่เสี่ยงทำให้ผลผิดหรือไม่

Checkpoint BC จึงเพิ่ม validator เพื่อกันไม่ให้เอา bar CSV ที่ไม่พร้อมไป join แล้วสรุปผิด

## Files Added

- `tools/paf_lookahead_bars_validator.py`
- `docs/68_Checkpoint_BC_PAF_Lookahead_Bars_Validator_TH.md`
- `docs/ai/tasks/checkpoint-bc-paf-lookahead-bars-validator.md`
- `research/selftests/checkpoint_bc/output/paf_lookahead_bars_validation_summary.json`
- `research/selftests/checkpoint_bc/output/paf_lookahead_bars_validation_summary.md`

## วิธีใช้

```powershell
python tools\paf_lookahead_bars_validator.py `
  --bars-csv path\to\paf_lookahead_bars.csv `
  --shadow-outcomes research\results\paf_shadow_outcomes_all_cases.csv `
  --results-root research\results `
  --symbol GOLD# `
  --timeframe H1 `
  --horizon-bars 48
```

## ตรวจอะไรบ้าง

- required columns: `time`, `open`, `high`, `low`, `close`
- parse timestamp ได้หรือไม่
- parse OHLC เป็นตัวเลขได้หรือไม่
- exact timestamp match กับ `event_time` ใน shadow outcomes หรือไม่
- coverage ยาวพอถึง event ล่าสุด + horizon หรือไม่
- มี gap ระหว่าง bars ที่ใหญ่กว่า timeframe step หรือไม่

## Self-Test

ใช้ fixture จาก Checkpoint BB-Prep:

- `research/selftests/checkpoint_bb/paf_shadow_outcomes_fixture.csv`
- `research/selftests/checkpoint_bb/paf_lookahead_bars_fixture.csv`

Command:

```powershell
python tools\paf_lookahead_bars_validator.py `
  --bars-csv research\selftests\checkpoint_bb\paf_lookahead_bars_fixture.csv `
  --shadow-outcomes research\selftests\checkpoint_bb\paf_shadow_outcomes_fixture.csv `
  --results-root research\selftests\checkpoint_bc\output `
  --symbol GOLD# `
  --timeframe H1 `
  --horizon-bars 4
```

ผล self-test:

- verdict: `PASS`
- bar count: `20`
- event count: `4`
- matched events: `4`
- missing events: `0`
- gap count: `0`

## Guardrails

- validator ไม่รัน MT5
- validator ไม่รัน Strategy Tester
- validator ไม่เปิด market order
- validator ไม่เปิด pending order
- validator ไม่ modify position
- validator ไม่ optimize
- validator ไม่เพิ่ม lot/risk
- output ไม่ใช่ proof of profitability

## Decision

- `LOOKAHEAD_BARS_VALIDATOR_ADDED`
- `VALIDATOR_SELFTEST_PASS`
- `REAL_MARKET_LOOKAHEAD_CSV_STILL_MISSING`
- `MT5_STILL_BLOCKED`
- `ORDER_PATH_STILL_BLOCKED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`

## Next Safe Step

Checkpoint BB จริงยังต้องรอ `paf_lookahead_bars.csv` จากข้อมูลตลาดจริงที่ผ่าน validator แล้ว

ยังไม่ควร implement market orders หรือ pending orders
