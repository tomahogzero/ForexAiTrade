# Checkpoint M: Price Action / Fibo Strategy Skeleton

เอกสารนี้สรุป Checkpoint M สำหรับ ForexAiTrade ซึ่งเพิ่มโครงสร้างโค้ดเริ่มต้นของกลยุทธ์ Price Action / Fibo เท่านั้น ยังไม่มีสัญญาณเข้าออเดอร์จริง และยังไม่อนุญาตให้ forward test บน demo/live

## สิ่งที่เพิ่ม

- เพิ่มไฟล์ `MQL5/Include/ForexAiTrade/Strategies/PriceActionFiboStrategy.mqh`
- เพิ่ม input กลุ่ม `Price Action / Fibo Skeleton`
- ผูก strategy skeleton เข้ากับ EA เพื่อให้ compile ได้
- เพิ่ม log placeholder เมื่อเปิด `InpEnablePriceActionFibo=true`
- เพิ่ม compile verification log สำหรับ Checkpoint M

## Input ที่เพิ่ม

- `InpEnablePriceActionFibo=false`
- `InpPriceActionFiboDiagnosticsOnly=true`
- `InpPAFEntryTimeframe=PERIOD_H1`
- `InpPAFHigherTimeframe=PERIOD_H1`
- `InpPAFUsePendingOrders=false`
- `InpPAFMaxPendingOrders=0`
- `InpPAFMaxOpenOrders=1`

ค่า default ทั้งหมดถูกตั้งแบบปลอดภัย: Price Action / Fibo ถูกปิดไว้ และ pending orders ถูกปิดไว้

## ไม่มีสัญญาณเทรดใน Checkpoint นี้

`CPriceActionFiboStrategy::Evaluate()` คืนค่า `SIGNAL_NONE` เสมอใน Checkpoint M

ข้อจำกัดที่ตั้งใจไว้:

- ไม่เปิด market order
- ไม่วาง pending order
- ไม่แก้ไข position
- ไม่สร้าง entry signal จริง
- ไม่เปลี่ยน baseline strategy behavior เมื่อ `InpEnablePriceActionFibo=false`

หากเปิด `InpEnablePriceActionFibo=true` EA จะ log ว่า module เป็น placeholder และไม่สร้าง trade signal

## ทำไม Pending Orders ยังปิดอยู่

Checkpoint L กำหนดไว้ว่ากลยุทธ์ Price Action / Fibo หรือ Fibo Zone Pending ต้องมี measurable rules, invalidation, expiry, max exposure, และ risk controls ก่อน การเปิด pending order ก่อน rule เหล่านี้ครบอาจทำให้ระบบกลายเป็น grid-like behavior ได้

ดังนั้น Checkpoint M จึงเพิ่มเฉพาะ skeleton และตั้ง `InpPAFUsePendingOrders=false`, `InpPAFMaxPendingOrders=0`

## ความสัมพันธ์กับ Checkpoint L

Checkpoint L เป็น specification-only สำหรับ Price Action / Fibo research

Checkpoint M เริ่มสร้างโครง code ตาม specification นั้น แต่ยังคงเป็น skeleton-only:

- มี TODO สำหรับ swing detection
- มี TODO สำหรับ support/resistance zone detection
- มี TODO สำหรับ Fibonacci zone calculation
- มี TODO สำหรับ breakout/retest detection
- มี TODO สำหรับ candle confirmation
- มี TODO สำหรับ invalidation rules
- มี TODO สำหรับ risk/R-multiple integration
- มี TODO สำหรับ diagnostics

## Symbol Profile Safety

- EURUSD H1 ยังเป็น baseline แรกสำหรับ research
- Other forex pairs เช่น USDJPY#, GBPUSD ต้อง validate แยกเอง
- GOLD# / GOLDm# ต้องถือเป็น broker-specific instrument class และต้องทำ risk-budget review แยก
- ห้าม reuse EURUSD parameters อัตโนมัติบน Gold หรือ symbol อื่น
- ห้าม force broker minimum lot ถ้าเกิน risk budget

## Checkpoint N ที่อาจทำในอนาคต

Checkpoint N อาจเพิ่มเฉพาะ diagnostic implementation เช่น swing/zone detection logging โดยยังไม่เปิด trade signal หากยังไม่มีข้อมูลเพียงพอ

สิ่งที่ควรรู้ก่อนเปิดสัญญาณจริง:

- swing/zone rules วัดได้ด้วยตัวเลข
- invalidation rules ชัดเจน
- pending order expiry/cancel rules ชัดเจน
- risk/R-multiple telemetry พร้อมตรวจสอบ
- train/validation/out-of-sample plan พร้อม

## ไม่ใช่ Optimization

Checkpoint M ไม่ได้ optimize parameter และไม่ได้เลือกค่าที่ทำกำไรย้อนหลัง

Input ที่เพิ่มเป็น safety/default placeholders เท่านั้น ไม่ใช่ parameter set ที่อนุมัติให้เทรด

## ไม่ใช่ Proof of Profitability

Checkpoint นี้ไม่ได้รัน MT5 backtest และไม่ได้พิสูจน์ว่ากลยุทธ์ Price Action / Fibo จะทำกำไรในอนาคต

ผลลัพธ์ของ checkpoint นี้คือ EA compile ได้พร้อม skeleton เท่านั้น

## ห้าม Demo/Live Forward Test

ยังไม่ควรเริ่ม demo/live forward test สำหรับ Price Action / Fibo เพราะยังไม่มี signal logic, pending order logic, diagnostics ที่ครบ, หรือผล train/validation/out-of-sample

ระบบยังต้องอยู่ในโหมด research-first และ capital-preservation-first
