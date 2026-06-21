# Checkpoint I: Session, Regime, Spread และ Drawdown Attribution

Checkpoint I วิเคราะห์ EURUSD H1 baseline จาก RunId `run_20260621_205032` โดยใช้ baseline variant `EURUSD_H1_EXIT_BASELINE_10000` เท่านั้น งานนี้เป็น attribution analysis ไม่ใช่ optimization

## ทำไม Attribution ต้องมาก่อน Strategy ใหม่

ก่อนเพิ่ม MicroTrend, Price Action, Fibo Zone หรือ strategy branch ใหม่ ต้องรู้ก่อนว่า baseline แพ้หรือชนะเพราะอะไร เช่น session, direction, regime, spread, exit type หรือ loss concentration ถ้าเพิ่ม strategy ใหม่เร็วเกินไป จะทำให้ระบบซับซ้อนขึ้นแต่ยังไม่รู้ root cause

## ข้อมูลที่ใช้

ใช้ข้อมูลจาก:

- `trade_ledger.csv`
- `exit_telemetry.csv`
- `parsed_result.json`
- case metadata ของ train / validation / out_of_sample

ไม่ได้รัน MT5 ใหม่

## วิธีอ่าน Session Attribution

Session ถูกจัดกลุ่มจาก broker/server time:

- Asia
- London
- London/New York overlap
- New York
- Other/Unknown

การตีความต้องดู validation และ out-of-sample พร้อมกัน ห้ามตัดสินจาก OOS อย่างเดียว ถ้า session ใดดูแย่ใน validation แต่ไม่ได้แย่ใน OOS หรือจำนวน trade ต่ำ ยังไม่ควรสร้าง session filter

## วิธีอ่าน Direction Attribution

ผลแยก buy/sell ช่วยตอบว่า direction ใดอ่อนแอหรือไม่

จากผลรอบนี้:

- buy ดีใน validation แต่ติดลบใน OOS
- sell ติดลบใน validation แต่ดีใน OOS

ดังนั้นยังไม่มี direction ที่อ่อนแอแบบ consistent ข้าม validation และ OOS พอจะสร้าง filter

## วิธีอ่าน Regime Attribution

Telemetry มี regime/strategy ตอน entry จึงสามารถแยก trend/breakout ได้

จากผลรอบนี้:

- validation: breakout และ trend เป็นบวก
- OOS: breakout และ trend เป็นบวก
- train: trend ติดลบ แต่ train มี trade count ต่ำและเป็นช่วงที่ baseline เคยถูกจัดเป็น weak

ยังไม่ควรสรุปว่า regime ใดควรถูกปิดจากข้อมูลนี้

## วิธีอ่าน Spread Attribution

spread_at_entry มีใน telemetry และถูกจัดเป็น bucket เช่น `16-20`, `21-25`

ข้อมูลส่วนใหญ่อยู่ใน bucket `16-20` ส่วน bucket `21-25` มีจำนวน trade น้อย จึงยังไม่ควรสร้าง spread filter ใหม่จากรอบนี้ แม้ควรเฝ้าดูต่อ

## Drawdown Concentration

ผล monthly/drawdown ชี้ว่าการขาดทุนไม่ได้กระจายเท่ากันทุกเดือน:

- train กระจุกอยู่ใน 2023-01 เพราะมี trade น้อย
- validation มี drawdown แย่สุดช่วง 2025-02
- out_of_sample มี drawdown แย่สุดช่วง 2026-03

นี่เป็นเหตุผลที่ยังต้อง research ต่อ ไม่ใช่ปรับ parameter ทันที

## ทำไม Sample Size สำคัญ

บางกลุ่มมี trade น้อย เช่น session บางช่วง, spread bucket สูง, หรือ regime breakout ใน OOS ถ้า sample ต่ำ ผลอาจเกิดจาก trade ไม่กี่ไม้ จึงห้ามสรุปเป็น filter หรือ strategy rule ใหม่ทันที

## Recommendation

ผล Checkpoint I:

`KEEP_BASELINE_RESEARCH_MORE`

ความหมาย:

- EURUSD H1 baseline ยังเป็น reference ได้
- ยังไม่ควรเปลี่ยน live/demo settings
- ยังไม่ควรเพิ่ม strategy ใหม่
- ยังไม่ควรอนุมัติ demo forward
- ควรเก็บ attribution เพิ่มและตรวจซ้ำก่อน branch strategy

## ทำไมยังไม่ใช่ Optimization

Checkpoint นี้ไม่ได้ sweep parameter, ไม่ได้เลือกค่าที่ทำกำไรสูงสุด, ไม่ได้เปลี่ยน entry/exit logic และไม่ได้ใช้ OOS เพื่อปรับค่า เป็นการอธิบายผลลัพธ์ของ baseline เท่านั้น
