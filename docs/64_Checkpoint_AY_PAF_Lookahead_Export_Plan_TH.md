# Checkpoint AY: PAF OHLC/Tick Lookahead Export Plan

วันที่จัดทำ: 2026-07-07

## สถานะ

Checkpoint AY เป็น documentation / research-plan-only checkpoint

ไม่มีการแก้ EA/source code, ไม่มีการแก้ presets, ไม่มีการรัน MT5, ไม่มีการรัน Strategy Tester, ไม่มี optimization, ไม่มีการเพิ่ม lot/risk, ไม่มี profitability claim และไม่มี approval สำหรับ demo/live trading

## เหตุผล

Checkpoint AX ยืนยันแล้วว่า Price Action / Fibo diagnostic fields ถูกเขียนลง `ea_mirror.log` ได้ครบ:

- `direction_context`
- `direction_reason`
- `entry_reference_price`
- bar OHLC
- `atr`
- `ema_fast`
- `ema_slow`
- `bb_width_percent`

แต่ shadow outcome parser ยังสรุปผลไม่ได้ เพราะไม่มีข้อมูลราคาหลังจุด diagnostic:

- AX possible setup rows: `33`
- `DATA_MISSING`: `19`
- `DIRECTION_MISSING`: `14`
- readiness: `BLOCKED_BY_MISSING_LOOKAHEAD_DATA`

ดังนั้นก่อนคิดเรื่อง order path ต้องมีแผน export OHLC/tick lookahead แบบ diagnostic-only เพื่อวัดว่า setup ที่ถูก label ไว้มีพฤติกรรมหลังจากนั้นอย่างไร โดยไม่เปิด order จริง

## เป้าหมายของ AY

สร้างแผนที่ปลอดภัยสำหรับ checkpoint ถัดไป เพื่อให้ระบบสามารถ export หรือสร้าง artifact ข้อมูลราคาแบบ lookahead สำหรับ offline shadow outcome labeling

เป้าหมายคือวัดพฤติกรรมหลัง diagnostic event เช่น:

- หลังเกิด `POSSIBLE_FIBO_PULLBACK` ราคาไปทาง expected direction หรือไม่
- หลังเกิด `POSSIBLE_ZONE_REJECTION` มี adverse move มากแค่ไหน
- หลังเกิด `POSSIBLE_BREAK_RETEST` ราคามี follow-through หรือ fail breakout
- spread / regime / session ส่งผลต่อ outcome อย่างไร

นี่เป็นการวิเคราะห์ diagnostic เท่านั้น ไม่ใช่ entry signal และไม่ใช่ profitability proof

## ข้อห้าม

Checkpoint ถัดไปที่ implement/export lookahead data ต้องห้าม:

- ห้ามเปิด market order
- ห้ามเปิด pending order
- ห้าม modify position
- ห้ามใช้ lookahead data ใน trading runtime
- ห้าม optimize parameter
- ห้ามเพิ่ม lot/risk
- ห้าม force broker minimum lot
- ห้าม claim profitability
- ห้าม demo/live forward test
- ห้ามใช้ข้อมูลอนาคตใน EA decision path

lookahead data ต้องใช้หลังรันจบแล้วเท่านั้น สำหรับ offline research / parser analysis

## Artifact ที่ต้องการในอนาคต

สำหรับแต่ละ diagnostic event ที่เป็น possible setup ควรมี output อย่างน้อย:

- `run_id`
- `case_id`
- `phase`
- `actual_symbol`
- `canonical_symbol`
- `timeframe`
- `event_time`
- `classification`
- `direction_context`
- `direction_reason`
- `entry_reference_price`
- `spread_points`
- `regime`
- `session_bucket`
- `bar_open`
- `bar_high`
- `bar_low`
- `bar_close`
- `atr`
- `ema_fast`
- `ema_slow`
- `bb_width_percent`

และข้อมูลหลัง event:

- lookahead bar count
- future high by horizon
- future low by horizon
- future close by horizon
- maximum favorable excursion หรือ MFE
- maximum adverse excursion หรือ MAE
- first touch side หากกำหนด hypothetical TP/SL
- same-bar ambiguity flag
- missing data flag

## Horizon ที่ควร pre-register

เพื่อกันการ optimize ย้อนหลัง ควรกำหนด horizon ล่วงหน้า เช่น:

- 6 bars
- 12 bars
- 24 bars
- 48 bars

สำหรับ H1 หมายถึงประมาณ 6, 12, 24, และ 48 ชั่วโมงหลัง diagnostic event

ห้ามเลือก horizon หลังเห็นผลเพื่อทำให้ดูดีขึ้น

## Hypothetical TP/SL สำหรับ shadow labeling

ถ้าจะใช้ hypothetical TP/SL ใน parser ต้อง pre-register ก่อน เช่น:

- ATR-based TP/SL
- structure-based invalidation
- fixed R multiple for analysis only

กติกานี้ต้องเป็น offline label เท่านั้น ไม่ใช่ order placement rule

ถ้า same-bar ทั้ง TP และ SL ถูกแตะใน bar เดียวกัน ให้ใช้กติกา conservative:

- mark เป็น `AMBIGUOUS_SAME_BAR`
- หรือถือว่า adverse side เกิดก่อน
- ห้ามเลือกด้านที่ทำให้ผลดูดี

## แนวทาง implementation ใน checkpoint ถัดไป

Checkpoint ถัดไปควรเลือกหนึ่งในสองแนวทาง:

### Option A: Export bar series artifact

ให้ runner หรือ parser export OHLC bar series รอบช่วง diagnostic run แล้ว parser จับคู่กับ event_time ภายหลัง

ข้อดี:

- ไม่ต้องให้ EA ใช้ข้อมูลอนาคต
- ลดความเสี่ยง future leak ใน trading decision path
- เหมาะกับ offline research

ข้อควรระวัง:

- ต้องพิสูจน์ว่า timestamp และ timezone ตรงกับ EA diagnostic log
- ต้องจัดการ missing bars / weekend / symbol session

### Option B: EA diagnostic file adds post-run-safe bar snapshot

ให้ EA เขียน diagnostic event และ bar context เพิ่ม แต่ห้ามคำนวณผลอนาคตเพื่อ decision ใน EA

ข้อดี:

- timestamp และ symbol context มาจาก EA โดยตรง

ข้อควรระวัง:

- ต้องแยกชัดเจนว่าเป็น logging-only
- ห้ามให้ future data กลับไปส่งผลต่อ `Evaluate()`
- ต้อง compile และ review source ก่อนรัน

AY แนะนำ Option A ก่อน เพราะปลอดภัยกว่าและลดความเสี่ยง future leak

## Acceptance Criteria สำหรับ checkpoint ถัดไป

Checkpoint ถัดไปต้องผ่าน:

- ไม่มี MQL5 order path change
- ไม่มี pending order implementation
- ไม่มี position modification
- ไม่มี optimization
- ไม่มี lot/risk increase
- มี artifact ที่จับคู่ diagnostic events กับ OHLC lookahead ได้
- timestamp alignment ถูกตรวจแล้ว
- parser แยก `DATA_MISSING`, `DIRECTION_MISSING`, `AMBIGUOUS_SAME_BAR`, และ valid shadow outcome
- output เป็น diagnostic summary เท่านั้น
- no profitability claim

## Output ที่ควรได้ในอนาคต

ไฟล์ที่คาดหวัง:

- `paf_lookahead_bars.csv`
- `paf_shadow_outcomes_enriched.csv`
- `paf_shadow_outcome_by_classification.md`
- `paf_shadow_outcome_by_session.md`
- `paf_shadow_outcome_by_spread_bucket.md`
- `paf_shadow_outcome_by_regime.md`
- `checkpoint_ay_or_next_recommendation.md`

## ความเสี่ยง

- future leak หาก EA ใช้ข้อมูลอนาคตใน decision path
- timestamp mismatch ระหว่าง EA log กับ exported bar series
- spread/tick behavior ของ Gold อาจต่างจาก bar OHLC
- low sample size ทำให้สรุปผิด
- การเลือก horizon หรือ TP/SL หลังเห็นผลอาจกลายเป็น optimization แฝง

## Decision

- `LOOKAHEAD_EXPORT_PLAN_DEFINED`
- `ORDER_PATH_STILL_BLOCKED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`
- `NEXT_CHECKPOINT_REQUIRES_EXPLICIT_SCOPE`

## Next Safe Step

Checkpoint AZ ควรเป็น implementation หรือ approval package ที่แคบมากสำหรับ Option A:

- export OHLC bar series artifact เท่านั้น
- parse กับ existing diagnostic events เท่านั้น
- ไม่รัน MT5 เว้นแต่ได้รับ approval ชัดเจน
- ไม่เปิด order
- ไม่แก้ entry/exit behavior
- ไม่ optimize
