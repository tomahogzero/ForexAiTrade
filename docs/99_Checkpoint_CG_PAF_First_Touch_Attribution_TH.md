# Checkpoint CG: PAF First-Touch Attribution by Classification / Session / Spread / Regime

Checkpoint CG เพิ่ม offline attribution สำหรับผล first-touch จาก Checkpoint CE

รอบนี้ทำเฉพาะ diagnostic attribution:

- ไม่รัน MT5
- ไม่รัน Strategy Tester
- ไม่แก้ EA/source code
- ไม่แก้ presets
- ไม่เปิด market order
- ไม่สร้าง pending order
- ไม่แก้ position
- ไม่ rerun first-touch labels
- ไม่ optimize
- ไม่เพิ่ม lot/risk
- ไม่สรุป profitability

## สิ่งที่เพิ่ม

เพิ่มเครื่องมือ:

- `tools/paf_first_touch_attribution.py`

เครื่องมือนี้อ่าน:

- `research/results/checkpoint_ce_paf_first_touch_relabel/paf_shadow_outcomes_first_touch_relabel.csv`

แล้วสร้าง:

- `research/results/checkpoint_cg_first_touch_attribution/first_touch_attribution_by_dimension.csv`
- `research/results/checkpoint_cg_first_touch_attribution/first_touch_attribution_summary.json`
- `research/results/checkpoint_cg_first_touch_attribution/first_touch_attribution_summary.md`
- `research/results/checkpoint_cg_first_touch_attribution/first_touch_attribution_guardrail_summary.md`

## Attribution Dimensions

ใช้ dimensions ที่ Checkpoint CF แนะนำ:

- `classification`
- `session_bucket`
- `spread_bucket`
- `regime`

## Dry Run Result

ผล dry run:

- Status: `PASS_OFFLINE_FIRST_TOUCH_ATTRIBUTION`
- Rows read: `33`
- Relabel-ready rows: `17`
- Data-missing rows: `2`
- Direction-missing rows: `14`
- Classification: `NOT_READY_FOR_ORDER_LOGIC`

## Main Diagnostic Finding

ผล attribution ยังยืนยันคำเตือนจาก CF:

- `SL_FIRST` ยังมากกว่า `TP_FIRST` ในกลุ่มที่ประเมินได้
- direction missing ยังสูง
- sample ยังเล็กเกินไป
- ยังไม่ควรเพิ่ม order logic

รายละเอียดที่พบ:

- `POSSIBLE_FIBO_PULLBACK` เป็นกลุ่มหลัก: `25` rows, relabel-ready `15` rows
- `POSSIBLE_FIBO_PULLBACK` มี `SL_FIRST` มากกว่า `TP_FIRST` ในทุก horizon
- `POSSIBLE_ZONE_REJECTION` มี sample เล็กมาก: `6` rows, relabel-ready `2` rows จึงยังสรุปไม่ได้
- `ASIA` และ `OVERLAP` มี `SL_FIRST` dominant ใน sample ปัจจุบัน
- `LONDON` และ `NEW_YORK` ดูดีกว่าใน sample นี้ แต่จำนวน relabel-ready ยังน้อยเกินไปและห้ามใช้เป็น session filter ทันที
- `NORMAL_SPREAD` และ `trend` ครอบคลุมข้อมูลส่วนใหญ่ จึงยังแยกผลของ spread/regime ได้จำกัด

## Meaning

ผลนี้ช่วยบอกว่าควรตรวจต่อว่าปัญหา SL_FIRST กระจุกอยู่ที่ setup / session / spread / regime ใด

ผลนี้ยังไม่ใช่:

- ผลกำไร
- backtest performance
- strategy approval
- live/demo approval
- parameter optimization result

## Decision

- `OFFLINE_FIRST_TOUCH_ATTRIBUTION_TOOL_ADDED`
- `OFFLINE_FIRST_TOUCH_ATTRIBUTION_DRY_RUN_PASS`
- `CLASSIFICATION_SESSION_SPREAD_REGIME_ATTRIBUTION_CREATED`
- `ORDER_LOGIC_NOT_APPROVED`
- `OPTIMIZATION_NOT_APPROVED`
- `MT5_NOT_RUN`
- `STRATEGY_TESTER_NOT_RUN`
- `EA_SOURCE_NOT_CHANGED`
- `PRESETS_NOT_CHANGED`
- `NO_PROFITABILITY_CLAIM`

## Next Safe Step

Checkpoint CH ควรเป็น attribution interpretation package เท่านั้น เพื่ออ่านผล CG แล้วจัดลำดับ blocker/diagnostic questions ก่อนจะคิดเรื่องแก้ strategy หรือ logging เพิ่ม
