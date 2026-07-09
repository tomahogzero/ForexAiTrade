# Checkpoint CS: PAF Direction Explainability Implementation Approval

วันที่จัดทำ: 2026-07-09

## สถานะ

Checkpoint CS เป็นเอกสารอนุมัติขอบเขตการ implementation เท่านั้น

ไม่ได้รัน MT5 ไม่ได้รัน Strategy Tester ไม่ได้แก้ EA/source code ไม่ได้แก้ preset ไม่ได้ optimize ไม่ได้เพิ่ม lot/risk และไม่ได้สรุปว่า strategy ทำกำไร

## เหตุผลที่ต้องมี approval package

Checkpoint CQ พบว่า `DIRECTION_UNKNOWN=78` ไม่ใช่ failure ทั้งหมด เพราะ `64` แถวเป็น `NO_SETUP_DIRECTION_NOT_REQUIRED`

ช่องว่างจริงที่ต้องอธิบายเพิ่มเหลือ `14` possible-setup rows:

- `FIBO_PULLBACK_EMA_DIRECTION_CONTEXT_MISSING`: `10`
- `ZONE_REJECTION_CANDLE_DIRECTION_CONTEXT_MISSING`: `4`

Checkpoint CR ออกแบบ field และ reason สำหรับอธิบายช่องว่างนี้แล้ว แต่ยังไม่ได้แก้ source code

Checkpoint CS จึงล็อกขอบเขตอย่างเป็นทางการก่อน checkpoint implementation ถัดไป เพื่อไม่ให้ diagnostics work เผลอกลายเป็น trading logic

## ขอบเขตที่อนุมัติสำหรับ Checkpoint CT

Checkpoint CT สามารถทำได้เฉพาะ:

1. เพิ่ม diagnostics-only fields ใน PAF log output
2. เพิ่ม parser support แบบ backward-compatible
3. เพิ่ม summary/report output สำหรับ direction gap reasons
4. compile EA ถ้ามี MQL5 changes
5. เพิ่ม compile log ใน `docs/verification/`

ห้ามรัน MT5 / Strategy Tester ใน CT เว้นแต่มี approval แยกหลังจาก implementation merge แล้ว

## ไฟล์ที่อนุญาตให้แก้ใน CT

อนุญาตเฉพาะไฟล์ที่เกี่ยวกับ diagnostics:

- `MQL5/Include/ForexAiTrade/Strategies/PriceActionFiboStrategy.mqh`
- `tools/paf_diagnostic_parser.py`
- `docs/`
- `docs/ai/`
- `research/results/` เฉพาะ output จาก parser self-test หรือ static validation

ไม่ควรแก้:

- preset files
- risk manager
- trade execution code
- strategy entry/exit signal behavior
- MT5 runner behavior
- lot/risk defaults

## Required Implementation Guardrails

ถ้า Checkpoint CT แก้ MQL5 ต้องยืนยัน:

- `Evaluate()` ยังเป็น diagnostics-only
- PAF path ยังไม่ส่ง `SIGNAL_BUY`
- PAF path ยังไม่ส่ง `SIGNAL_SELL`
- ไม่มี market order
- ไม่มี pending order
- ไม่มี position modification
- ไม่มี baseline fallback
- ไม่มี optimization
- ไม่มี lot/risk increase
- ไม่มี broker minimum lot override
- ไม่มี lookahead

## Required New Diagnostic Fields

Checkpoint CT ควร implement field ตาม CR แบบระมัดระวัง

### Fibo Pullback Fields

- `paf_fibo_ema_fast_value`
- `paf_fibo_ema_slow_value`
- `paf_fibo_ema_gap_points`
- `paf_fibo_ema_slope_state`
- `paf_fibo_price_vs_ema_state`
- `paf_fibo_trend_alignment_state`
- `paf_fibo_pullback_side`
- `paf_fibo_direction_gap_reason`

### Zone Rejection Fields

- `paf_zone_side`
- `paf_zone_touch_state`
- `paf_rejection_candle_direction`
- `paf_rejection_wick_side`
- `paf_rejection_body_ratio`
- `paf_rejection_wick_ratio`
- `paf_zone_direction_gap_reason`

## Required Reason Values

### Fibo Pullback

- `EMA_VALUES_MISSING`
- `EMA_GAP_TOO_SMALL`
- `EMA_SLOPE_FLAT`
- `PRICE_BETWEEN_EMAS`
- `TREND_ALIGNMENT_CONFLICT`
- `PULLBACK_SIDE_UNKNOWN`
- `FIBO_ZONE_SIDE_CONFLICT`
- `INSUFFICIENT_BAR_CONTEXT`
- `NONE`

### Zone Rejection

- `ZONE_SIDE_UNKNOWN`
- `ZONE_TOUCH_MISSING`
- `TOUCHED_BOTH_SIDES`
- `REJECTION_CANDLE_DOJI`
- `WICK_TOO_SMALL`
- `BODY_DIRECTION_CONFLICT`
- `WICK_SIDE_CONFLICT`
- `INSUFFICIENT_BAR_CONTEXT`
- `NONE`

## Parser Requirements

`tools/paf_diagnostic_parser.py` ต้อง:

- parse legacy logs ได้เหมือนเดิม
- parse new fields ได้ถ้ามี
- map missing fields เป็น `null` หรือ `UNKNOWN`
- ไม่ crash เมื่อ field บางตัวไม่มี
- แยก `NO_SETUP_DIRECTION_NOT_REQUIRED` ออกจาก possible-setup gaps
- สรุป gap count เฉพาะ possible-setup rows

## Required Checks After CT Implementation

Checkpoint CT ต้องทำอย่างน้อย:

1. Python syntax check สำหรับ parser ที่แก้
2. Compile EA ถ้าแก้ MQL5
3. Guardrail grep/check summary
4. Artifact audit

Guardrail grep ต้องค้นหาอย่างน้อย:

- `SIGNAL_BUY`
- `SIGNAL_SELL`
- `OrderSend`
- `.Buy(`
- `.Sell(`
- `BuyLimit`
- `SellLimit`
- `BuyStop`
- `SellStop`
- `PositionModify`

ถ้าพบคำเหล่านี้ในส่วน PAF implementation ใหม่ ต้องอธิบายหรือหยุด

## Compile Requirement

ถ้า CT แก้ MQL5:

- compile active EA
- สร้าง `docs/verification/compile_after_checkpoint_CT.log`
- ต้องได้ `0 errors, 0 warnings`

## MT5 Execution Block

Checkpoint CT ยังห้ามรัน MT5 / Strategy Tester

หลัง CT merge แล้ว ถ้าต้อง validation จริง ต้องมี checkpoint approval ใหม่ เช่น Checkpoint CU:

- one run only
- Strategy Tester only
- `GOLD#` H1 หรือ symbol/timeframe ที่อนุมัติชัดเจน
- date range สั้น
- no market orders
- no pending orders
- no position modification
- no optimization
- no profitability interpretation

## Stop Conditions

หยุด CT ทันทีถ้า:

- implementation ต้องแก้ order logic
- implementation ต้องแก้ preset
- implementation ต้องเพิ่ม risk/lot
- parser ต้องอ่านค่าด้วยการเดาสุ่ม
- compile มี warning/error ที่แก้ไม่ได้โดยไม่เปลี่ยน behavior
- พบว่าต้องรัน MT5 เพื่อพิสูจน์ implementation

## Decision

Checkpoint CS อนุมัติให้ checkpoint ถัดไปทำ diagnostics-only implementation ของ direction explainability fields ได้ แต่ยังไม่อนุมัติ Strategy Tester run และยังไม่อนุมัติ order logic

PAF ยังอยู่สถานะ:

- `NOT_READY_FOR_ORDER_LOGIC`
- `NOT_READY_FOR_DEMO`
- `NOT_READY_FOR_LIVE`

## Approval Phrase For Future CT

ถ้าจะให้เริ่ม CT implementation ให้ใช้ข้อความ:

`Approved to implement Checkpoint CT diagnostics-only PAF direction explainability fields with compile verification and no MT5 run.`
