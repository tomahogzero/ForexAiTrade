# Checkpoint CE: PAF Offline First-Touch Relabel Tool and Dry Run

Checkpoint CE เพิ่มเครื่องมือ offline เพื่อ relabel first-touch outcome โดยใช้ `offline_atr_14` จาก Checkpoint CC

รอบนี้ทำเฉพาะ offline relabel:

- ไม่รัน MT5
- ไม่รัน Strategy Tester
- ไม่แก้ EA/source code
- ไม่แก้ presets
- ไม่แก้ production validator
- ไม่เปิด market order
- ไม่สร้าง pending order
- ไม่แก้ position
- ไม่ optimize
- ไม่เพิ่ม lot/risk
- ไม่สรุป profitability

## สิ่งที่เพิ่ม

เพิ่มเครื่องมือ:

- `tools/paf_first_touch_relabel.py`

เครื่องมือนี้อ่าน:

- `research/results/checkpoint_cc_offline_atr_enrichment/paf_shadow_outcomes_atr_enriched.csv`
- `research/results/checkpoint_bz_offline_joiner_run/paf_lookahead_bars.csv`

แล้วสร้าง:

- `research/results/checkpoint_ce_paf_first_touch_relabel/paf_shadow_outcomes_first_touch_relabel.csv`
- `research/results/checkpoint_ce_paf_first_touch_relabel/first_touch_relabel_summary.json`
- `research/results/checkpoint_ce_paf_first_touch_relabel/first_touch_relabel_summary.md`
- `research/results/checkpoint_ce_paf_first_touch_relabel/first_touch_relabel_by_horizon.csv`
- `research/results/checkpoint_ce_paf_first_touch_relabel/first_touch_relabel_guardrail_summary.md`

## Relabel Method

ใช้ค่าที่ Checkpoint CD อนุมัติไว้เท่านั้น:

- ATR column: `offline_atr_14`
- TP ATR multiple: `1.5`
- SL ATR multiple: `1.0`
- Horizons: `6,12,24,48`

rows ที่ `ATR_MISSING` หรือ `DIRECTION_MISSING` จะไม่ถูกเดา outcome และยังคงถูก block

## Dry Run Result

ผล dry run จากไฟล์ CC/BZ:

- Rows read: `33`
- Relabel-ready rows: `17`
- Data-missing rows: `2`
- Direction-missing rows: `14`

สถานะ:

`PASS_OFFLINE_FIRST_TOUCH_RELABEL`

## Outcome Label Distribution

ผลนี้เป็นจำนวน label ของ shadow diagnostic เท่านั้น:

| Horizon | TP_FIRST | SL_FIRST | NO_RESOLUTION | AMBIGUOUS_SAME_BAR | DATA_MISSING | DIRECTION_MISSING |
|---:|---:|---:|---:|---:|---:|---:|
| 6 | 5 | 9 | 2 | 1 | 2 | 14 |
| 12 | 6 | 10 | 0 | 1 | 2 | 14 |
| 24 | 6 | 10 | 0 | 1 | 2 | 14 |
| 48 | 6 | 10 | 0 | 1 | 2 | 14 |

ตัวเลขนี้ยังไม่ใช่ผลกำไรและยังไม่ใช่สัญญาณให้เปิด order

## ความหมายของผลลัพธ์

ผลนี้เป็น shadow diagnostic เท่านั้น ไม่ใช่ trade result จริง

ใช้เพื่อดูว่า ถ้า PAF diagnostic event นั้นมี entry reference และ ATR แล้ว ภายใน horizon หลัง event มี hypothetical TP หรือ SL ถูกแตะก่อนหรือไม่

สิ่งที่ยังห้ามทำ:

- ห้ามตีความเป็นกำไร
- ห้ามเลือก strategy candidate
- ห้ามเพิ่ม order logic
- ห้ามเพิ่ม pending order
- ห้ามเพิ่ม lot/risk
- ห้ามเริ่ม demo/live

## Limitation

OHLC H1 bars ไม่รู้ลำดับ tick ภายในแท่งเดียวกัน ถ้า TP และ SL ถูกแตะในแท่งเดียวกัน ต้อง label เป็น `AMBIGUOUS_SAME_BAR`

## Decision

- `OFFLINE_FIRST_TOUCH_RELABEL_TOOL_ADDED`
- `OFFLINE_FIRST_TOUCH_RELABEL_DRY_RUN_PASS`
- `OFFLINE_ATR_14_USED_ONLY`
- `TP_SL_MULTIPLES_FIXED`
- `DIRECTION_MISSING_STAYS_BLOCKED`
- `ATR_MISSING_STAYS_DATA_MISSING`
- `SAME_BAR_AMBIGUITY_HANDLED`
- `MT5_NOT_RUN`
- `STRATEGY_TESTER_NOT_RUN`
- `EA_SOURCE_NOT_CHANGED`
- `PRESETS_NOT_CHANGED`
- `NO_OPTIMIZATION`
- `NO_PROFITABILITY_CLAIM`

## Next Safe Step

Checkpoint CF ควรเป็น diagnostic interpretation package เท่านั้น เพื่อสรุป distribution ของ labels โดยไม่สรุปกำไร ไม่ optimize และไม่เพิ่ม order logic
