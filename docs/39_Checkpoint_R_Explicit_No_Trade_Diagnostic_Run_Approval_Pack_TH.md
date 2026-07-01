# Checkpoint R: ชุดเอกสารขออนุมัติการรัน Diagnostic แบบห้ามเทรด

วันที่สร้าง: 2026-07-02

## เป้าหมาย

Checkpoint R เป็นเอกสารขออนุมัติเท่านั้น สำหรับการรัน Strategy Tester แบบ diagnostic-only ในอนาคตของ Price Action / Fibo

Checkpoint นี้ยังไม่รัน MT5, ยังไม่รัน Strategy Tester, ไม่แก้ source code, ไม่แก้ preset, ไม่ optimize และไม่อนุมัติ demo/live trading

## ขอบเขตที่แคบมากของการรันในอนาคต

ถ้ามีการอนุมัติแยกใน checkpoint ถัดไป การรันต้องจำกัดเฉพาะ:

- Symbol: EURUSD
- Timeframe: H1
- ช่วงเวลาสั้นเพื่อดู diagnostic เท่านั้น
- Strategy Tester เท่านั้น
- ห้าม optimization
- ห้าม demo/live/forward test
- ห้าม market order
- ห้าม pending order
- ห้ามแก้ position
- ห้ามเพิ่ม lot/risk
- ห้ามอ้างว่าได้กำไรหรือพิสูจน์ profitability

## ค่าที่ต้องตรวจสอบก่อนรัน

ก่อนรันจริงในอนาคต ต้องบันทึก effective config และตรวจให้ครบ:

- `InpEnablePriceActionFibo=true`
- `InpPriceActionFiboDiagnosticsOnly=true`
- `InpPAFUsePendingOrders=false`
- `InpPAFMaxPendingOrders=0`
- `InpManageExistingPositions=false`
- `InpRequireStrategyTester=true`
- `InpPAFLogOnlyOnNewBar=true`
- ไม่มี existing/open position ใน tester context
- ต้องเป็น Strategy Tester เท่านั้น

ถ้าข้อใดไม่ตรง ห้ามเริ่มรัน

## เงื่อนไขหยุดทันที

ต้องหยุดและถือว่า fail หากพบ:

- config ไม่ตรง
- มีการพยายามส่ง market order
- มีการพยายามส่ง pending order
- มีการพยายามแก้ position
- baseline strategy ทำงานแทน diagnostic path
- log ถี่เกินไปเพราะ `InpPAFLogOnlyOnNewBar` ไม่ทำงาน
- optimization ถูกเปิด
- ตรวจพบ demo/live environment

## Artifact ที่ต้องเก็บถ้ามีการรันในอนาคต

- path ของ Strategy Tester report/log
- RunId
- effective config snapshot
- grep/check summary สำหรับคำสั่งเทรดต้องห้าม
- diagnostic classification summary
- no-trade confirmation

## หมายเหตุสำคัญ

`InpLiveTradingEnabled=true` หากใช้ใน Strategy Tester เป็นเพียงการผ่าน internal tester gate ของ EA เท่านั้น ไม่ใช่การอนุมัติ demo/live trading

classification จาก Price Action / Fibo เป็น label เพื่อสังเกตการณ์เท่านั้น ไม่ใช่สัญญาณเข้าออเดอร์

## สถานะ

MT5 / Strategy Tester ยังคงถูก block จนกว่าจะมีคำอนุมัติแยกอย่างชัดเจนหลังจาก review Checkpoint R
