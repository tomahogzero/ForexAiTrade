# Strategy Branch Gate: Price Action / Fibo Zone

เอกสารนี้กำหนด gate ก่อนเพิ่ม strategy branch ใหม่ เช่น Price Action หรือ Fibo Zone เพื่อไม่ให้ระบบรีบเพิ่มความซับซ้อนก่อนเข้าใจ baseline

## ทำไม Price Action / Fibo Zone เป็นสาขาที่มีเหตุผล

Price Action / Fibo Zone เป็นแนวคิดที่ใช้บริบทของ swing, zone, retracement และ reaction ของราคา ซึ่งอาจช่วยตอบโจทย์บางช่วงที่ baseline trend/breakout/mean-reversion ยังไม่ดีพอ โดยเฉพาะถ้าพบว่า loss กระจุกตัวในบาง regime หรือบาง session

แต่การเพิ่ม strategy ใหม่เร็วเกินไปอาจทำให้:

- แยกไม่ออกว่ากำไร/ขาดทุนมาจาก baseline หรือ strategy ใหม่
- เกิด overfitting จาก backtest
- เพิ่มจำนวน parameter จนควบคุม robustness ยาก
- ทำให้ risk attribution ไม่ชัด

## ทำไมยังไม่ควรเพิ่มก่อน baseline attribution ชัดเจน

Checkpoint I ยังสรุปว่า EURUSD H1 baseline ควร `KEEP_BASELINE_RESEARCH_MORE` ไม่ใช่ reject และไม่ใช่ final candidate จุดอ่อนบางอย่าง เช่น session, direction, regime และ spread ยังมี sample size จำกัดหรือผลไม่ consistent ระหว่าง validation กับ out-of-sample

ดังนั้นถ้าเพิ่ม Price Action / Fibo ตอนนี้ เราจะไม่รู้ว่า:

- baseline แพ้เพราะ session หรือ exit
- แพ้เพราะ regime detector
- แพ้เพราะ direction bias
- แพ้เพราะ strategy logic จริง
- หรือข้อมูลยังน้อยเกินไป

## หลักฐานที่ต้องมีก่อนเปิด strategy branch ใหม่

ก่อนสร้าง Price Action / Fibo branch ควรมีอย่างน้อย:

- baseline attribution แยก session/direction/regime/spread แล้ว
- loss concentration ชัดเจนว่าเกิดในเงื่อนไขใด
- trade count เพียงพอใน validation และ out-of-sample
- evidence ไม่ได้มาจาก OOS อย่างเดียว
- มี logging ที่บอก regime/strategy/spread/exit classification ครบ
- มีเกณฑ์ reject/continue ที่ชัดก่อนเริ่มทดสอบ

## วิธีแยกวิจัย Price Action ในอนาคต

ถ้าจะทำ branch ใหม่ในอนาคต ให้แยกเป็น research branch โดย:

- ใช้ preset แยกจาก baseline
- ใช้ magic number แยก
- ใช้ output folder/run id แยก
- ไม่ผสมผลกับ baseline table
- เริ่มจาก diagnostic-only ก่อน ไม่ optimize
- รัน train/validation/out-of-sample เหมือน baseline
- ห้ามใช้ OOS เพื่อเลือก parameter

## สถานะปัจจุบัน

ยังไม่อนุญาตให้เพิ่ม Price Action / Fibo Zone ใน Checkpoint I

สถานะ: `WAIT_FOR_BASELINE_ATTRIBUTION_FOLLOWUP`

ไม่มีการอนุมัติ demo forward และไม่มีการ claim profitability
