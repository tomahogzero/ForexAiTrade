# Checkpoint G: Exit Telemetry และ R-Multiple Diagnostics

เอกสารนี้สรุป Checkpoint G ซึ่งเป็นงานวัดผลและบันทึกข้อมูล exit เท่านั้น ไม่ใช่การ optimize parameter และไม่ใช่หลักฐานว่าระบบจะทำกำไรในอนาคต

## เป้าหมาย

ก่อนแก้ exit logic เราต้องรู้ก่อนว่า order ปิดเพราะอะไรจริง ๆ โดยเฉพาะกรณีที่ MT5 report แสดง comment ว่า `sl` เพราะคำว่า SL ใน report อาจหมายถึงหลายแบบ:

- ชน stop loss แล้วขาดทุนจริง
- stop ถูกเลื่อนมาใกล้ breakeven แล้วปิดเกือบเท่าทุน
- trailing stop ถูกเลื่อนตามกำไรแล้วปิดด้วยกำไร

ถ้าอ่านเฉพาะ MT5 close comment ว่า `sl` จะสรุปผิดได้ง่ายว่า exit ทั้งหมดเป็น stop loss ที่แย่ ทั้งที่บางรายการเป็น trailing profit exit

## สิ่งที่เพิ่มใน Checkpoint G

- เพิ่ม `MQL5/Include/ForexAiTrade/ExitTelemetry.mqh`
- เพิ่ม input สำหรับ telemetry:
  - `InpEnableExitTelemetry`
  - `InpExitTelemetryFileName`
  - `InpLogPositionModifyEvents`
  - `InpLogRMultipleOnClose`
- บันทึก event:
  - `OPEN`
  - `MODIFY`
  - `CLOSE`
- เพิ่ม parser:
  - `tools/exit_telemetry_parser.py`
- รัน diagnostic-only เฉพาะ `EURUSD_H1_10000` ใน phase:
  - validation
  - out_of_sample

ไม่มีการเปลี่ยน entry logic และไม่มีการเปลี่ยน exit behavior เพื่อทำกำไร

## Realized R คำนวณอย่างไร

หลักคิด:

`realized R = profit ตอนปิด / initial risk money`

ตัวอย่างเชิงความหมาย:

- `realized R` ใกล้ `-1.0` หมายถึงขาดทุนประมาณ 1R
- `realized R` ใกล้ `0` หมายถึงใกล้ breakeven
- `realized R` มากกว่า `0` หมายถึงปิดด้วยกำไร

ค่า profit ที่ใช้มาจากผลปิด position ใน MT5 telemetry และ initial risk money ถูกบันทึกตั้งแต่ตอนเปิด trade

## Exit Classification

Telemetry แบ่ง close event เป็นกลุ่มหลัก:

| Classification | ความหมาย |
|---|---|
| INITIAL_SL_LOSS | ปิดด้วย SL และขาดทุนจริง |
| BREAKEVEN_SL | ปิดด้วย SL แต่ใกล้ breakeven |
| TRAILING_SL_PROFIT | ปิดด้วย SL comment แต่ปิดด้วยกำไร เพราะ SL ถูกเลื่อนขึ้น/ลงตามกำไร |
| TP_HIT | ปิดด้วย take profit |
| OTHER_CLOSE | ปิดด้วยเหตุผลอื่น |
| UNKNOWN | ข้อมูลไม่พอสำหรับจำแนก |

การจำแนกนี้เป็น diagnostic heuristic ไม่ใช่ logic เทรดใหม่

## ผลจาก RunId

RunId: `run_20260621_202843`

| Phase | Status | Trades | Net Profit | Profit Factor |
|---|---|---:|---:|---:|
| validation | PASS | 105 | 61.38 | 1.16 |
| out_of_sample | PASS | 62 | 41.03 | 1.18 |

รวม validation และ out-of-sample:

| Exit Type | Count |
|---|---:|
| INITIAL_SL_LOSS | 72 |
| BREAKEVEN_SL | 1 |
| TRAILING_SL_PROFIT | 66 |
| TP_HIT | 28 |
| OTHER_CLOSE | 0 |
| UNKNOWN | 0 |

ข้อสังเกตสำคัญ: SL comment จำนวนมากไม่ใช่ loss ทั้งหมด เพราะมี `TRAILING_SL_PROFIT` ถึง 66 รายการ

## ข้อจำกัด

- Checkpoint G ไม่ได้รัน train phase โดยตั้งใจ ดังนั้น case-level approval ยังไม่ครบ
- Telemetry ยังไม่ได้บันทึก MFE/MAE แบบละเอียด
- ยังไม่ควรสรุปว่า TP ไกลเกินไปหรือ SL แคบเกินไปจากข้อมูลชุดเดียว
- ยังต้องดู session, regime, spread/slippage และ drawdown concentration ประกอบ
- ผลนี้เป็น backtest diagnostic ไม่ใช่ forward test

## Recommendation

สถานะถัดไป: `NEEDS_EXIT_RESEARCH`

ความหมายคือควรวิจัย exit ต่อจากข้อมูล telemetry ก่อน ไม่ใช่เริ่ม optimize ทันที และยังไม่ควรเพิ่ม MicroTrend, Fibo Zone, Grid, Pending strategy หรือเริ่ม demo forward test

## ทำไมยังไม่ใช่ Optimization

Checkpoint นี้ไม่ได้ค้นหา parameter ที่กำไรมากที่สุด ไม่ได้ปรับ trailing/SL/TP และไม่ได้เลือกค่าที่ดีที่สุดจากหลายชุด งานนี้เพิ่มเฉพาะ telemetry เพื่อให้เข้าใจพฤติกรรมการปิด order ก่อนตัดสินใจเปลี่ยนระบบ
