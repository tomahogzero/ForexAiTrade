# แผน Backtest

Backtest ควรใช้ข้อมูลย้อนหลังอย่างน้อย 5 ปี และควรใช้ 8-10 ปีถ้ามีข้อมูลคุณภาพดี

## คุณภาพข้อมูล

- ใช้ real tick หรือโหมด tick คุณภาพสูงถ้าเป็นไปได้
- ใส่สมมติฐาน spread ที่สมจริง
- ใส่สมมติฐาน slippage
- ทดสอบแต่ละ symbol แยกกันก่อนพิจารณาระดับ portfolio

## การแบ่งช่วงข้อมูล

- Train/Optimization: ค้นหา candidate parameter areas
- Validation: คัดทิ้งชุด parameter ที่เปราะบางหรือ overfit
- Out-of-sample: ประเมินผลในข้อมูลที่ระบบไม่เคยเห็น
- Demo forward test: ตรวจพฤติกรรมในตลาดปัจจุบัน

## Symbols ที่ต้องทดสอบ

- EURUSD H1
- GBPUSD H1
- USDJPY H1
- XAUUSD H1

## การตรวจขั้นต่ำ

Parameter set ที่ผ่านต้องมีกำไรสุทธิเป็นบวก drawdown อยู่ในเกณฑ์ จำนวน trade เพียงพอ losing streak ไม่ยาวเกินไป และผลลัพธ์คงที่ใน validation และ out-of-sample
