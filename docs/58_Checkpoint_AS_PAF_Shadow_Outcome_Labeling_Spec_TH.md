# Checkpoint AS: PAF Shadow Outcome Labeling Specification

วันที่จัดทำ: 2026-07-07

## สถานะ

Checkpoint AS เป็น specification-only checkpoint

ไม่ได้รัน MT5, ไม่ได้รัน Strategy Tester, ไม่ได้ spawn `terminal64.exe`, ไม่ได้แก้ EA/source code, ไม่ได้แก้ presets, ไม่ได้แก้ scripts/tools, ไม่ได้ optimize, ไม่ได้เพิ่ม lot/risk, ไม่ได้เปิด market order, ไม่ได้เปิด pending order, ไม่ได้ modify position และไม่ได้ claim profitability

## เป้าหมาย

ออกแบบวิธีวัดผลแบบ shadow outcome สำหรับ Price Action / Fibo diagnostic labels โดยไม่เปิด order จริง

เหตุผล: Checkpoint AQ/AR ยืนยันแล้วว่า PAF diagnostic workflow ปลอดภัยและมี labels กระจายหลายเดือน แต่ label presence ยังไม่ใช่ evidence ว่าถ้าเข้าเทรดจริงแล้วจะได้กำไรหรือควบคุม drawdown ได้

## สิ่งที่ Shadow Outcome ต้องตอบ

Shadow outcome ต้องตอบคำถามเหล่านี้โดยไม่ส่งคำสั่งเทรด:

- เมื่อเกิด `POSSIBLE_FIBO_PULLBACK` หลังจากนั้นราคาเคลื่อนไปทางที่คาดไหม
- เมื่อเกิด `POSSIBLE_ZONE_REJECTION` มี rejection follow-through จริงหรือไม่
- เมื่อเกิด `POSSIBLE_BREAK_RETEST` retest มี continuation จริงหรือหลอก
- ถ้าวัดด้วย SL/TP สมมติ outcome เป็น `TP_FIRST`, `SL_FIRST`, `NO_RESOLUTION`, หรือ `AMBIGUOUS`
- outcome เปลี่ยนไปตาม regime, spread bucket, session, volatility bucket หรือไม่
- label ใดมี noise สูงเกินไปจนไม่ควร implement

## หลักการสำคัญ

Shadow outcome เป็น research label เท่านั้น

ห้าม:

- ใช้ shadow outcome เป็น entry signal จริง
- เปิด market order
- เปิด pending order
- modify position
- optimize parameter
- เพิ่ม lot/risk
- claim profitability
- เริ่ม demo/live forward test

## Source Data

Input ที่อนุญาต:

- `ea_mirror.log`
- `paf_diagnostics.json`
- `paf_diagnostics_summary.md`
- `parsed_result.json`
- MT5 OHLC/tick data ที่ดึงจาก Strategy Tester artifact หรือ exported data ใน checkpoint ถัดไปเท่านั้น

Input ที่ยังไม่ควรใช้:

- demo/live fills
- order history จากเงินจริง
- manual discretionary labels
- parameter optimization output

## Required Diagnostic Fields

แต่ละ PAF diagnostic event ควรมี fields อย่างน้อย:

- `time`
- `actual_symbol`
- `canonical_symbol`
- `timeframe`
- `classification`
- `regime`
- `spread`
- `close_price` หรือ reference price
- `atr` ถ้ามี
- `ema_fast` / `ema_slow` ถ้ามี
- `bb_width` ถ้ามี
- `session` ถ้าคำนวณได้

ถ้าข้อมูลบาง field ไม่มี parser ต้องใส่ `null` และบันทึก limitation ห้ามเดาค่าจากอากาศ

## Shadow Entry Reference

การกำหนด entry reference ต้องเป็น deterministic และไม่ใช้ข้อมูลอนาคต

สำหรับ checkpoint แรกของ shadow labeling ให้ใช้แบบ conservative:

- Entry reference: close ของ bar ที่เกิด diagnostic label
- Direction: derived จาก label context ถ้ามี direction field
- ถ้าไม่มี direction field: classify เป็น `DIRECTION_UNKNOWN` และไม่ให้คำนวณ TP/SL directional outcome
- Entry price ต้องรวม spread assumption แยกในรายงาน ไม่บิดเพื่อให้ผลดีขึ้น

## Direction Handling

ถ้า diagnostic log มี direction:

- `BUY_CONTEXT`
- `SELL_CONTEXT`
- `DIRECTION_UNKNOWN`

ถ้าไม่มี direction ใน log:

- ห้าม infer direction จากผลอนาคต
- ห้ามใช้การมองย้อนหลังเลือก buy/sell
- ให้ outcome เป็น `DIRECTION_MISSING`
- ระบุว่า future diagnostic logging ต้องเพิ่ม direction ก่อนวัด outcome จริง

## Shadow Stop / Target Hypothesis

AS ยังไม่กำหนด parameter เพื่อ optimize

อนุญาตให้กำหนด hypothesis แบบ pre-registered เท่านั้น เช่น:

- SL hypothesis: ATR-based invalidation ระดับ conservative
- TP hypothesis: fixed R multiple เช่น 1R, 1.5R, 2R เพื่อวัด distribution
- Lookahead: จำนวน bars คงที่ เช่น 12, 24, 48 bars

Checkpoint ถัดไปต้องระบุค่าก่อนรัน parser และห้ามเลือกค่าหลังเห็นผล

## Outcome Labels

Outcome labels ที่ควรใช้:

- `TP_FIRST`: ราคาถึง hypothetical target ก่อน stop
- `SL_FIRST`: ราคาถึง hypothetical stop ก่อน target
- `BOTH_SAME_BAR`: ทั้ง stop และ target อยู่ใน bar เดียวกัน
- `NO_RESOLUTION`: ไม่ถึง stop หรือ target ภายใน lookahead
- `DIRECTION_MISSING`: ไม่มี direction เพียงพอสำหรับคำนวณ
- `DATA_MISSING`: OHLC/tick data ไม่พอ
- `SPREAD_FILTERED`: spread สูงเกินเงื่อนไขก่อนคำนวณ outcome
- `REGIME_FILTERED`: regime ไม่อยู่ในกลุ่มที่ต้องการวัด

สำหรับ `BOTH_SAME_BAR` ต้องใช้ conservative assumption:

- หากไม่มี tick path ให้ถือเป็น ambiguous หรือ stop-first ใน sensitivity table
- ห้ามเลือก TP-first เพื่อทำให้ผลดูดีขึ้น

## Buckets ที่ต้องแยกวิเคราะห์

ผล shadow outcome ต้องแยกอย่างน้อย:

- classification
- regime
- spread bucket
- volatility bucket
- session bucket
- month/window
- direction

Spread bucket เบื้องต้น:

- `LOW_SPREAD`
- `NORMAL_SPREAD`
- `HIGH_SPREAD`
- `EXTREME_SPREAD`

ค่าขอบเขต bucket ต้องกำหนดล่วงหน้าใน checkpoint ถัดไป ห้ามเลือกจากผลลัพธ์ย้อนหลัง

## Metrics

Metrics ที่ควรรายงาน:

- event count
- eligible event count
- missing direction count
- TP_FIRST count
- SL_FIRST count
- BOTH_SAME_BAR count
- NO_RESOLUTION count
- DATA_MISSING count
- simple win/loss ratio ของ shadow labels
- average favorable excursion
- average adverse excursion
- median bars to resolution
- spread distribution per outcome
- regime distribution per outcome

Metrics เหล่านี้ยังไม่ใช่เงินจริง และยังไม่ใช่ proof of profitability

## Minimum Evidence Gate

ก่อนคิดเรื่อง implementation spec ของ order path ต้องมีอย่างน้อย:

- eligible directional events เพียงพอใน validation-style windows
- event distribution ไม่กระจุกเดือนเดียว
- outcome ไม่ได้ดีเพราะ spread bucket เดียว
- label ที่สนใจยังดีใน high-spread sensitivity หรือถูก filter อย่างชัดเจน
- `NO_RESOLUTION` ไม่สูงจนไม่มี edge ที่วัดได้
- ไม่มีการเลือก parameter จากผลย้อนหลังแบบ overfit

## Gold-Specific Risk Guardrails

Gold ต้องเป็น instrument class แยกจาก EURUSD/forex pairs

สำหรับ Gold:

- ใช้ actual symbol `_Symbol` / `GOLD#`
- ห้าม reuse EURUSD SL/TP/ATR/zone width โดยตรง
- ต้องเคารพ broker min lot และ risk budget
- ห้าม force broker minimum lot หากเกิน risk budget
- เงิน deposit assumption สำหรับ research ไม่ใช่คำแนะนำให้เทรดเงินจริง

## Required Outputs สำหรับ Checkpoint ถัดไป

ถ้าจะทำ Checkpoint AT ต่อ ควรเป็น parser/spec implementation แบบ no-order:

- `tools/paf_shadow_outcome_labeler.py` หรือชื่อที่เทียบเท่า
- `research/results/paf_shadow_outcomes_all_cases.csv`
- `research/results/paf_shadow_outcome_summary.md`
- per-window outcome summary
- missing-data limitations
- sensitivity table สำหรับ ambiguous bars

แต่ Checkpoint AS ยังไม่ implement tool

## Decision

ผล Checkpoint AS:

```text
SHADOW_OUTCOME_SPEC_DEFINED
NO_ORDER_IMPLEMENTATION_APPROVED
NO_OPTIMIZATION_APPROVED
```

## Recommended Next Checkpoint

Checkpoint AT ควรเป็น:

```text
PAF Shadow Outcome Parser Prototype
```

เงื่อนไข:

- no MT5 run เว้นแต่ user approve แยก
- no order
- no pending order
- no position modification
- ใช้ AQ artifacts เป็น input ก่อน
- ถ้าข้อมูล direction/OHLC ไม่พอ ต้อง report limitation ไม่ใช่เดา

## Progress ประเมินหลัง Checkpoint AS

- EA / safety / risk guardrails: `90%`
- MT5 runner + artifact pipeline: `88%`
- PAF no-trade diagnostic workflow: `78%`
- Gold-specific diagnostic evidence: `60%`
- PAF implementation readiness: `42%`
- Demo/live readiness: `0%`
- Profitability proof: `0%`

ภาพรวมถ้าวัดถึง "ระบบวิจัยที่พร้อมทดลอง strategy อย่างควบคุมได้": ประมาณ `56%`

ถ้าวัดถึง "บอทพร้อมเงินจริง": ยังประมาณ `10-15%`

เหตุผล: AS เพิ่มกรอบวัด outcome ที่จำเป็นก่อน implementation แต่ยังไม่ได้สร้าง outcome data และยังไม่อนุมัติ order logic
