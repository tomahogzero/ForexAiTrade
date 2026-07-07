# Checkpoint BB-Prep: PAF Lookahead Joiner Self-Test

วันที่จัดทำ: 2026-07-07

## สถานะ

Checkpoint BB-Prep เป็น self-test สำหรับ `tools/paf_lookahead_joiner.py` ด้วยข้อมูลจำลองขนาดเล็ก

ไม่มีการรัน MT5, ไม่มีการรัน Strategy Tester, ไม่มีการแก้ EA/source code, ไม่มีการแก้ presets, ไม่มี optimization, ไม่มีการเพิ่ม lot/risk และไม่มี profitability claim

นี่ไม่ใช่ Checkpoint BB ที่ใช้ข้อมูลตลาดจริง และไม่ใช่ proof ว่า strategy ใช้ได้

## เหตุผล

Checkpoint AZ เพิ่ม offline joiner แล้ว แต่ยังไม่เคยทดสอบกับ CSV ที่มี OHLC ครบจริง ๆ

Checkpoint BA กำหนด checklist สำหรับ `paf_lookahead_bars.csv` แล้ว แต่ยังไม่มีไฟล์ตลาดจริงที่ verify ได้

BB-Prep จึงใช้ fixture จำลองเพื่อยืนยัน logic ของ tool ก่อน โดยไม่ใช้เป็นผลวิจัย

## Files Added

- `research/selftests/checkpoint_bb/paf_shadow_outcomes_fixture.csv`
- `research/selftests/checkpoint_bb/paf_lookahead_bars_fixture.csv`
- `research/selftests/checkpoint_bb/output/paf_shadow_outcomes_enriched.csv`
- `research/selftests/checkpoint_bb/output/paf_lookahead_join_summary.json`
- `research/selftests/checkpoint_bb/output/paf_lookahead_join_summary.md`
- `docs/67_Checkpoint_BB_Prep_PAF_Lookahead_Joiner_Selftest_TH.md`
- `docs/ai/tasks/checkpoint-bb-prep-paf-lookahead-joiner-selftest.md`

## Command Used

```powershell
python tools\paf_lookahead_joiner.py `
  --shadow-outcomes research\selftests\checkpoint_bb\paf_shadow_outcomes_fixture.csv `
  --bars-csv research\selftests\checkpoint_bb\paf_lookahead_bars_fixture.csv `
  --results-root research\selftests\checkpoint_bb\output `
  --horizons 4 `
  --tp-atr-multiple 1.5 `
  --sl-atr-multiple 1.0
```

## Expected Self-Test Cases

| Case | Expected |
|---|---|
| `BUY_TP_FIRST` | `TP_FIRST` |
| `SELL_SL_FIRST` | `SL_FIRST` |
| `BUY_AMBIGUOUS` | `AMBIGUOUS_SAME_BAR` |
| `DIRECTION_UNKNOWN` | `DIRECTION_MISSING` |

## Result

| Case | Join Status | Outcome |
|---|---|---|
| `BUY_TP_FIRST` | `JOINED` | `TP_FIRST` |
| `SELL_SL_FIRST` | `JOINED` | `SL_FIRST` |
| `BUY_AMBIGUOUS` | `JOINED` | `AMBIGUOUS_SAME_BAR` |
| `DIRECTION_UNKNOWN` | `DIRECTION_MISSING` | n/a |

Self-test result: `PASS`

## Guardrails

- ไม่รัน MT5
- ไม่รัน Strategy Tester
- ไม่เปิด market order
- ไม่เปิด pending order
- ไม่ modify position
- ไม่แก้ EA decision path
- ไม่ optimize
- ไม่เพิ่ม lot/risk
- ไม่ claim profitability
- fixture เป็นข้อมูลจำลอง ไม่ใช่ข้อมูลตลาดจริง

## Decision

- `LOOKAHEAD_JOINER_SELFTEST_PASS`
- `REAL_MARKET_LOOKAHEAD_CSV_STILL_MISSING`
- `MT5_STILL_BLOCKED`
- `ORDER_PATH_STILL_BLOCKED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`

## Next Safe Step

Checkpoint BB จริงควรเกิดหลังมี `paf_lookahead_bars.csv` จากข้อมูลตลาดจริงที่ผ่าน checklist ใน Checkpoint BA แล้วเท่านั้น

approval phrase ที่ยังต้องใช้:

`Approved to execute Checkpoint BB offline PAF lookahead join with bars CSV <absolute_path_to_csv> for RunId run_20260707_172236.`

การ approval นี้ยังคงอนุญาตเฉพาะ offline Python analysis เท่านั้น ไม่อนุญาต MT5, Strategy Tester, orders, optimization, หรือ risk changes
