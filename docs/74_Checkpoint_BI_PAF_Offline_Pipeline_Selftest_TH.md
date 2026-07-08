# Checkpoint BI: PAF Offline Pipeline Self-Test

วันที่จัดทำ: 2026-07-08

## สถานะ

Checkpoint BI รัน self-test แบบ offline ทั้ง pipeline ด้วยข้อมูลจำลองเท่านั้น:

raw MT5-style bars CSV -> schema normalizer -> bars validator -> lookahead joiner

ไม่มีการรัน MT5, ไม่มีการรัน Strategy Tester, ไม่มีการแก้ EA/source code, ไม่มีการแก้ presets, ไม่มีข้อมูลตลาดจริง, ไม่มี optimization, ไม่มีการเพิ่ม lot/risk และไม่มี profitability claim

## Files Added

- `research/selftests/checkpoint_bi/paf_lookahead_bars_raw_mt5_style.csv`
- `research/selftests/checkpoint_bi/paf_shadow_outcomes_fixture.csv`
- `research/selftests/checkpoint_bi/output/paf_lookahead_bars.csv`
- `research/selftests/checkpoint_bi/output/paf_lookahead_bars_raw.csv`
- `research/selftests/checkpoint_bi/output/paf_bars_schema_normalization_summary.json`
- `research/selftests/checkpoint_bi/output/paf_bars_schema_normalization_summary.md`
- `research/selftests/checkpoint_bi/output/paf_lookahead_bars_validation_summary.json`
- `research/selftests/checkpoint_bi/output/paf_lookahead_bars_validation_summary.md`
- `research/selftests/checkpoint_bi/output/paf_shadow_outcomes_enriched.csv`
- `research/selftests/checkpoint_bi/output/paf_lookahead_join_summary.json`
- `research/selftests/checkpoint_bi/output/paf_lookahead_join_summary.md`
- `docs/74_Checkpoint_BI_PAF_Offline_Pipeline_Selftest_TH.md`
- `docs/ai/tasks/checkpoint-bi-paf-offline-pipeline-selftest.md`

## เหตุผล

Checkpoint BH เพิ่ม schema normalizer แล้ว แต่ยังทดสอบแยกแค่ normalize และ validate

Checkpoint BI จึงทดสอบ pipeline เต็มแบบ offline:

1. raw MT5-style CSV
2. normalized CSV
3. validator
4. lookahead joiner
5. enriched shadow outcome rows

เพื่อยืนยันว่า tool chain ต่อกันได้ก่อนใช้กับไฟล์ `GOLD#` H1 จริง

## Commands Run

### Syntax Check

```powershell
python -m py_compile `
  tools\paf_bars_schema_normalizer.py `
  tools\paf_lookahead_bars_validator.py `
  tools\paf_lookahead_joiner.py
```

ผล: `PASS`

### Normalize

```powershell
python tools\paf_bars_schema_normalizer.py `
  --raw-csv research\selftests\checkpoint_bi\paf_lookahead_bars_raw_mt5_style.csv `
  --output-csv research\selftests\checkpoint_bi\output\paf_lookahead_bars.csv `
  --results-root research\selftests\checkpoint_bi\output `
  --source-symbol GOLD# `
  --source-timeframe H1
```

ผล:

- normalization verdict: `PASS`
- rows before: `4`
- rows after: `4`
- invalid rows: `0`

### Validate

```powershell
python tools\paf_lookahead_bars_validator.py `
  --bars-csv research\selftests\checkpoint_bi\output\paf_lookahead_bars.csv `
  --shadow-outcomes research\selftests\checkpoint_bi\paf_shadow_outcomes_fixture.csv `
  --results-root research\selftests\checkpoint_bi\output `
  --symbol GOLD# `
  --timeframe H1 `
  --horizon-bars 1
```

ผล:

- validation verdict: `PASS`
- bar count: `4`
- event count: `2`
- matched events: `2`
- missing events: `0`
- gap count: `0`

### Join

```powershell
python tools\paf_lookahead_joiner.py `
  --shadow-outcomes research\selftests\checkpoint_bi\paf_shadow_outcomes_fixture.csv `
  --bars-csv research\selftests\checkpoint_bi\output\paf_lookahead_bars.csv `
  --results-root research\selftests\checkpoint_bi\output `
  --horizons 1,2 `
  --tp-atr-multiple 1.5 `
  --sl-atr-multiple 1.0
```

ผล:

- join status: `JOINED` = `2`
- horizon 1: `TP_FIRST` = `1`, `SL_FIRST` = `1`
- horizon 2: `TP_FIRST` = `1`, `SL_FIRST` = `1`

## Guardrails

- ใช้ synthetic fixture เท่านั้น
- ไม่รัน MT5
- ไม่รัน Strategy Tester
- ไม่เปิด market order
- ไม่เปิด pending order
- ไม่ modify position
- ไม่แก้ EA/source code
- ไม่แก้ presets
- ไม่ใช้ข้อมูล lookahead ใน EA decision path
- ไม่ optimize
- ไม่เพิ่ม lot/risk
- ไม่ claim profitability

## Limitations

- self-test นี้ไม่ใช่ข้อมูลตลาดจริง
- ยังไม่มี `GOLD#` H1 bars CSV จริงจาก XM MT5
- OHLC bar ไม่สามารถพิสูจน์ลำดับ tick ภายในแท่งเดียวกันได้
- same-bar ambiguity ยังต้องตีความแบบ conservative
- ผล `TP_FIRST` หรือ `SL_FIRST` ใน fixture เป็นการทดสอบ logic ไม่ใช่ strategy performance

## Decision

- `OFFLINE_PIPELINE_SELFTEST_PASS`
- `NORMALIZER_VALIDATOR_JOINER_CHAIN_PASS_ON_SYNTHETIC_FIXTURE`
- `REAL_MARKET_LOOKAHEAD_CSV_STILL_MISSING`
- `JOINER_NOT_RUN_ON_REAL_DATA`
- `MT5_NOT_RUN`
- `ORDER_PATH_STILL_BLOCKED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`

## Progress Estimate

- Research infrastructure readiness: `74%`
- PAF diagnostic readiness: `70%`
- PAF shadow-outcome readiness: `63%`
- Order implementation readiness: `0%`
- Demo/live readiness: `0%`

ขั้นต่อไปที่ปลอดภัยคือรับไฟล์ `GOLD#` H1 raw/normalized CSV จริงจากผู้ใช้ แล้วรัน offline intake/normalization/validation ก่อน join จริง
