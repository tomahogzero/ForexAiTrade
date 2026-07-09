# Checkpoint CT: PAF Direction Explainability Fields

วันที่จัดทำ: 2026-07-09

## สถานะ

Checkpoint CT implement เฉพาะ diagnostics-only fields และ parser support ตาม approval phrase:

`Approved to implement Checkpoint CT diagnostics-only PAF direction explainability fields with compile verification and no MT5 run.`

ไม่ได้รัน MT5 ไม่ได้รัน Strategy Tester ไม่ได้แก้ preset ไม่ได้ optimize ไม่ได้เพิ่ม lot/risk และไม่ได้สรุปว่า strategy ทำกำไร

## ไฟล์ที่แก้

- `MQL5/Include/ForexAiTrade/Strategies/PriceActionFiboStrategy.mqh`
- `tools/paf_diagnostic_parser.py`
- `docs/verification/compile_after_checkpoint_CT.log`
- `docs/112_Checkpoint_CT_PAF_Direction_Explainability_Fields_TH.md`
- `docs/ai/current-status.md`
- `docs/ai/tasks/checkpoint-ct-paf-direction-explainability-fields.md`
- `docs/ai/gpt-requests/checkpoint-ct-review-paf-direction-explainability-fields.md`

## สิ่งที่เพิ่มใน MQL5

เพิ่ม field เชิงวินิจฉัยเพื่ออธิบาย possible-setup direction gap โดยไม่เปลี่ยน signal behavior:

### Fibo Pullback

- `paf_fibo_ema_fast_value`
- `paf_fibo_ema_slow_value`
- `paf_fibo_ema_gap_points`
- `paf_fibo_ema_slope_state`
- `paf_fibo_price_vs_ema_state`
- `paf_fibo_trend_alignment_state`
- `paf_fibo_pullback_side`
- `paf_fibo_direction_gap_reason`

### Zone Rejection

- `paf_zone_touch_state`
- `paf_rejection_candle_direction`
- `paf_rejection_wick_side`
- `paf_rejection_body_ratio`
- `paf_rejection_wick_ratio`
- `paf_zone_direction_gap_reason`

หมายเหตุ: `paf_zone_side` มีอยู่แล้วจาก checkpoint ก่อนหน้า จึงคง field เดิมไว้และเพิ่ม `paf_zone_touch_state` เพื่ออธิบายการแตะ zone ให้ชัดขึ้น

## Reason Values

### Fibo Pullback Gap Reasons

- `EMA_VALUES_MISSING`
- `EMA_GAP_TOO_SMALL`
- `EMA_SLOPE_FLAT`
- `PRICE_BETWEEN_EMAS`
- `TREND_ALIGNMENT_CONFLICT`
- `PULLBACK_SIDE_UNKNOWN`
- `FIBO_ZONE_SIDE_CONFLICT`
- `INSUFFICIENT_BAR_CONTEXT`
- `NONE`

### Zone Rejection Gap Reasons

- `ZONE_SIDE_UNKNOWN`
- `ZONE_TOUCH_MISSING`
- `TOUCHED_BOTH_SIDES`
- `REJECTION_CANDLE_DOJI`
- `WICK_TOO_SMALL`
- `BODY_DIRECTION_CONFLICT`
- `WICK_SIDE_CONFLICT`
- `INSUFFICIENT_BAR_CONTEXT`
- `NONE`

## Parser Update

`tools/paf_diagnostic_parser.py` ถูก update ให้:

- parse field ใหม่ได้
- รองรับ legacy logs ต่อไป
- เพิ่ม `paf_direction_gap_bucket_counts`
- เพิ่ม `paf_fibo_direction_gap_reason_counts`
- เพิ่ม `paf_zone_direction_gap_reason_counts`
- เพิ่ม summary section สำหรับ direction gap explainability

## Verification

### Python Syntax Check

ผ่าน:

`python -m py_compile tools/paf_diagnostic_parser.py`

หลัง syntax check ได้ลบ `tools/__pycache__` ออกจาก worktree แล้ว

### MQL5 Compile

Compile active EA:

- File: `MQL5/Experts/ForexAiTrade/ForexAiTrade.mq5`
- Log: `docs/verification/compile_after_checkpoint_CT.log`
- Result: `0 errors, 0 warnings`

## Guardrail Scan

ตรวจใน `PriceActionFiboStrategy.mqh` แล้วไม่พบ marker ต่อไปนี้:

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

## สิ่งที่ไม่ได้ทำ

- ไม่ได้รัน MT5
- ไม่ได้รัน Strategy Tester
- ไม่ได้เปิด market order
- ไม่ได้เปิด pending order
- ไม่ได้แก้ position
- ไม่ได้ fallback ไป baseline strategy
- ไม่ได้แก้ preset
- ไม่ได้แก้ RiskManager
- ไม่ได้ optimize
- ไม่ได้เพิ่ม lot/risk
- ไม่ได้ claim profitability

## Decision

Checkpoint CT ผ่าน compile และเพิ่ม diagnostics-only explainability fields แล้ว

PAF ยังอยู่สถานะ:

- `NOT_READY_FOR_ORDER_LOGIC`
- `NOT_READY_FOR_DEMO`
- `NOT_READY_FOR_LIVE`

## Next Safe Step

Checkpoint CU ควรเป็น approval package สำหรับ one-run Strategy Tester diagnostic validation ของ CT fields เท่านั้น

ยังห้ามรัน MT5 จนกว่าจะมี approval แยกชัดเจน
