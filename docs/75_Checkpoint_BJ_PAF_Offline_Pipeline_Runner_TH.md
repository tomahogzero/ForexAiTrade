# Checkpoint BJ: PAF Offline Pipeline Runner

วันที่จัดทำ: 2026-07-08

## สถานะ

Checkpoint BJ เพิ่ม runner แบบ offline เพื่อรัน pipeline ทั้งเส้นด้วยคำสั่งเดียว:

raw bars CSV หรือ normalized bars CSV -> normalize ถ้าจำเป็น -> validate -> join

ไม่มีการรัน MT5, ไม่มีการรัน Strategy Tester, ไม่มีการแก้ EA/source code, ไม่มีการแก้ presets, ไม่มีข้อมูลตลาดจริง, ไม่มี optimization, ไม่มีการเพิ่ม lot/risk และไม่มี profitability claim

## Files Added

- `tools/paf_offline_pipeline_runner.py`
- `research/selftests/checkpoint_bj/output/paf_bars_schema_normalization_summary.json`
- `research/selftests/checkpoint_bj/output/paf_bars_schema_normalization_summary.md`
- `research/selftests/checkpoint_bj/output/paf_lookahead_bars.csv`
- `research/selftests/checkpoint_bj/output/paf_lookahead_bars_raw.csv`
- `research/selftests/checkpoint_bj/output/paf_lookahead_bars_validation_summary.json`
- `research/selftests/checkpoint_bj/output/paf_lookahead_bars_validation_summary.md`
- `research/selftests/checkpoint_bj/output/paf_lookahead_join_summary.json`
- `research/selftests/checkpoint_bj/output/paf_lookahead_join_summary.md`
- `research/selftests/checkpoint_bj/output/paf_offline_pipeline_runner_summary.json`
- `research/selftests/checkpoint_bj/output/paf_offline_pipeline_runner_summary.md`
- `research/selftests/checkpoint_bj/output/paf_shadow_outcomes_enriched.csv`
- `docs/75_Checkpoint_BJ_PAF_Offline_Pipeline_Runner_TH.md`
- `docs/ai/tasks/checkpoint-bj-paf-offline-pipeline-runner.md`

## เหตุผล

หลัง Checkpoint BI pipeline offline ทำงานครบแล้ว แต่ยังต้องรันหลายคำสั่งแยกกัน

Checkpoint BJ จึงเพิ่ม runner เพื่อให้ขั้นตอนในอนาคตกับไฟล์จริงปลอดภัยขึ้น:

1. ถ้ามี raw CSV ให้ normalize ก่อน
2. รัน validator เสมอ
3. ถ้า validator fail ให้หยุด
4. รัน joiner เฉพาะเมื่อ validator ผ่าน
5. สรุป stage results ในไฟล์เดียว

## Tool

`tools/paf_offline_pipeline_runner.py`

รองรับ input อย่างใดอย่างหนึ่ง:

- `--raw-csv` สำหรับไฟล์ raw MT5-style export
- `--bars-csv` สำหรับไฟล์ normalized `time,open,high,low,close`

## Self-Test Command

```powershell
python -m py_compile `
  tools\paf_offline_pipeline_runner.py `
  tools\paf_bars_schema_normalizer.py `
  tools\paf_lookahead_bars_validator.py `
  tools\paf_lookahead_joiner.py

python tools\paf_offline_pipeline_runner.py `
  --raw-csv research\selftests\checkpoint_bi\paf_lookahead_bars_raw_mt5_style.csv `
  --shadow-outcomes research\selftests\checkpoint_bi\paf_shadow_outcomes_fixture.csv `
  --results-root research\selftests\checkpoint_bj\output `
  --symbol GOLD# `
  --timeframe H1 `
  --horizon-bars 1 `
  --join-horizons 1,2 `
  --tp-atr-multiple 1.5 `
  --sl-atr-multiple 1.0
```

## Self-Test Result

- syntax check: `PASS`
- runner verdict: `PASS`
- normalize stage: `PASS`
- validate stage: `PASS`
- join stage: `PASS`
- join status: `JOINED=2`
- horizon 1 outcomes: `TP_FIRST=1`, `SL_FIRST=1`
- horizon 2 outcomes: `TP_FIRST=1`, `SL_FIRST=1`

## Stop Gate

runner ต้องหยุดทันทีถ้า:

- normalization fail
- validation fail
- joiner fail

ถ้า validation fail runner จะไม่รัน joiner

## Guardrails

- ไม่รัน MT5
- ไม่รัน Strategy Tester
- ไม่เปิด market order
- ไม่เปิด pending order
- ไม่ modify position
- ไม่แก้ EA/source code
- ไม่แก้ presets
- ไม่ใช้ข้อมูลตลาดจริงใน self-test นี้
- ไม่ใช้ lookahead data ใน EA decision path
- ไม่ optimize
- ไม่เพิ่ม lot/risk
- ไม่ claim profitability

## Limitations

- self-test ใช้ synthetic fixture เท่านั้น
- ยังไม่มีไฟล์ `GOLD#` H1 จริงจาก XM MT5
- runner ไม่พิสูจน์ว่า strategy ดี
- runner ไม่อนุญาต order path
- OHLC bars ยังไม่พิสูจน์ลำดับ tick ภายในแท่งเดียวกัน

## Decision

- `OFFLINE_PIPELINE_RUNNER_ADDED`
- `OFFLINE_PIPELINE_RUNNER_SELFTEST_PASS`
- `NORMALIZE_VALIDATE_JOIN_CHAIN_PASS_ON_SYNTHETIC_FIXTURE`
- `REAL_MARKET_LOOKAHEAD_CSV_STILL_MISSING`
- `JOINER_NOT_RUN_ON_REAL_DATA`
- `MT5_NOT_RUN`
- `ORDER_PATH_STILL_BLOCKED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`

## Progress Estimate

- Research infrastructure readiness: `76%`
- PAF diagnostic readiness: `70%`
- PAF shadow-outcome readiness: `65%`
- Order implementation readiness: `0%`
- Demo/live readiness: `0%`

ขั้นต่อไปที่ปลอดภัยคือใช้ runner นี้กับไฟล์ `GOLD#` H1 จริงหลังผู้ใช้ส่ง path หรืออนุมัติการ export ข้อมูล bars แยกต่างหาก
