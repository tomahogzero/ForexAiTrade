# Checkpoint AV: PAF Diagnostic Logging Fields

วันที่จัดทำ: 2026-07-07

## สถานะ

Checkpoint AV เป็น diagnostic-logging-only implementation checkpoint

มีการแก้ MQL5 source เฉพาะส่วน Price Action / Fibo diagnostic log และแก้ parser ให้รองรับ field ใหม่

ไม่ได้รัน MT5, ไม่ได้รัน Strategy Tester, ไม่ได้ spawn `terminal64.exe`, ไม่ได้แก้ presets, ไม่ได้ optimize, ไม่ได้เพิ่ม lot/risk, ไม่ได้เปิด market order, ไม่ได้เปิด pending order, ไม่ได้ modify position และไม่ได้ claim profitability

## เหตุผล

Checkpoint AT พบว่า AQ artifacts มี possible setup rows `267` จุด แต่ทั้งหมดติด `DIRECTION_MISSING`

Checkpoint AU จึงกำหนด field ที่ต้องเพิ่มใน diagnostic log ก่อนวัด shadow outcome จริง

Checkpoint AV เพิ่ม field เหล่านั้นแบบ logging-only เพื่อให้ checkpoint ถัดไปสามารถรัน no-trade diagnostics แล้ว parser อ่าน direction / entry reference / bar context ได้

## ไฟล์ที่แก้

- `MQL5/Include/ForexAiTrade/Strategies/PriceActionFiboStrategy.mqh`
- `tools/paf_shadow_outcome_labeler.py`
- `docs/verification/compile_after_checkpoint_AV.log`
- `docs/61_Checkpoint_AV_PAF_Diagnostic_Logging_Fields_TH.md`
- `docs/ai/tasks/checkpoint-av-paf-diagnostic-logging-fields.md`
- `docs/ai/current-status.md`

## MQL5 Diagnostic Fields ที่เพิ่ม

Price Action / Fibo diagnostic log เพิ่ม fields:

- `direction_context`
- `direction_reason`
- `entry_reference_price`
- `bar_open`
- `bar_high`
- `bar_low`
- `bar_close`
- `atr`
- `ema_fast`
- `ema_slow`
- `bb_width_percent`

## Direction Context

ค่าที่อนุญาต:

- `BUY_CONTEXT`
- `SELL_CONTEXT`
- `DIRECTION_UNKNOWN`

กติกาเป็น diagnostic-only และ deterministic จากข้อมูล ณ เวลานั้น:

- break/retest เหนือ swing high = `BUY_CONTEXT`
- break/retest ใต้ swing low = `SELL_CONTEXT`
- rejection จาก support พร้อม candle bullish = `BUY_CONTEXT`
- rejection จาก resistance พร้อม candle bearish = `SELL_CONTEXT`
- fibo pullback ใช้ EMA context เพื่อบอก direction แบบ diagnostic-only
- ถ้าไม่ชัดเจน = `DIRECTION_UNKNOWN`

กติกานี้ไม่ใช่ entry signal และไม่ถูกใช้เปิดออเดอร์

## Parser Update

`tools/paf_shadow_outcome_labeler.py` ถูกปรับให้รองรับ:

- `direction_context`
- `direction_reason`

ถ้า `direction_context=DIRECTION_UNKNOWN` parser ยังถือเป็น `DIRECTION_MISSING`

ถ้ามี direction แล้วแต่ยังไม่มี OHLC/tick lookahead parser ต้องถือเป็น `DATA_MISSING` จนกว่า checkpoint ถัดไปจะมี artifact เพียงพอ

## Compile Result

Compile active EA:

```text
Result: 0 errors, 0 warnings
```

Compile log:

- `docs/verification/compile_after_checkpoint_AV.log`

## Guardrails

ยืนยัน:

- ไม่เปิด market order
- ไม่เปิด pending order
- ไม่ modify position
- `Evaluate()` ของ Price Action / Fibo ยังคืน `SIGNAL_NONE`
- ไม่เพิ่ม lot/risk
- ไม่ optimize
- ไม่ claim profitability
- ไม่อนุมัติ demo/live trading

## สิ่งที่ยังไม่ได้พิสูจน์

Checkpoint AV ยังไม่ได้รัน MT5 ดังนั้นยังไม่ได้พิสูจน์ว่า log ใหม่เกิดจริงใน Strategy Tester

ยังไม่ได้พิสูจน์ shadow outcome, TP/SL, R-multiple หรือกำไร

## Next Safe Step

Checkpoint AW ควรเป็น approval package สำหรับรัน no-trade Strategy Tester diagnostic window สั้น ๆ เพื่อยืนยันว่า field ใหม่ออกใน `ea_mirror.log` จริง

เงื่อนไขยังต้องเหมือนเดิม:

- Strategy Tester only
- one run หรือ small controlled windows เท่านั้น
- diagnostics-only
- no market order
- no pending order
- no position modification
- no optimization
- no lot/risk increase
- no profitability claim

## Progress Estimate

- Research system readiness: ประมาณ `59%`
- PAF diagnostic readiness: ประมาณ `52%`
- PAF shadow outcome readiness: ยังต้องรัน no-trade diagnostic ใหม่ก่อน
- PAF order implementation readiness: ยังไม่พร้อม
- Demo/live readiness: `0%`
- Profit proof: `0%`

