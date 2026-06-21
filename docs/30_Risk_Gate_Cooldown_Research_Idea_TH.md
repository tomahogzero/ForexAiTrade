# Risk Gate Cooldown Research Idea

เอกสารนี้เป็นไอเดียวิจัยอนาคตเท่านั้น ยังไม่ใช่ approved change และยังไม่ควรใช้กับ demo/live

## เหตุผล

Checkpoint I2 พบว่า losing streak gate สามารถทำให้ backtest phase ถูก lockout ยาวมาก โดยเฉพาะ train phase ของ EURUSD H1 baseline ซึ่งมี trade เพียง 22 ครั้ง แล้วหลังจาก losing streak block แรกไม่มี accepted trade เพิ่มอีก

นี่ไม่ได้แปลว่า losing streak gate ผิด เพราะมันเป็นกลไก survival-first แต่แปลว่าควรมี diagnostic research เพื่อแยก raw strategy behavior ออกจาก risk-gated behavior

## ไอเดียที่อาจวิจัยในอนาคต

### 1. Fixed Cooldown After Losing Streak

หลังเกิด losing streak ให้หยุดเทรดตามจำนวน bar หรือชั่วโมงที่กำหนด แล้วอนุญาตให้ประเมินใหม่

ความเสี่ยง:

- cooldown สั้นเกินไปอาจกลับเข้า market ที่ยังแย่
- cooldown ยาวเกินไปอาจพลาด recovery regime

### 2. Pause Until Next Trading Day/Week

เมื่อถึง losing streak limit ให้หยุดจนถึงวันถัดไปหรือสัปดาห์ถัดไป

ความเสี่ยง:

- เป็น rule ที่เรียบง่ายแต่ยังอาจไม่สัมพันธ์กับ regime จริง

### 3. Reduce Risk After Losing Streak

ไม่ปิดระบบเต็มรูปแบบ แต่ลด risk percent ชั่วคราวหลัง losing streak

ความเสี่ยง:

- อาจทำให้ระบบยังเทรดใน regime แย่
- ต้องระวังไม่กลายเป็นการเพิ่มความซับซ้อนเพื่อไล่กำไร

### 4. Require Regime Reset Before Trading Again

หลัง losing streak ให้รอจน regime เปลี่ยนหรือ quality metric กลับมาดีขึ้นก่อนเทรด

ความเสี่ยง:

- ต้องนิยาม regime reset ให้ชัด
- ถ้า detector noisy อาจเกิด false reset

### 5. Diagnostic Raw-Strategy Run

รัน Strategy Tester แบบ diagnostic-only โดยปิดหรือผ่อน risk gate บางตัว เพื่อดู raw strategy behavior

ข้อกำหนด:

- ต้องใช้ `InpRequireStrategyTester=true`
- ห้ามใช้ preset นี้บน chart จริง
- ห้ามนำผลไป claim profitability
- ต้องแยก output จาก baseline ปกติชัดเจน

### 6. Compare Raw vs Risk-Gated Performance

เปรียบเทียบ:

- baseline risk-gated
- raw diagnostic
- cooldown variants

ดูทั้ง train, validation, out-of-sample และต้องแยกผลให้ชัดว่า variant ใดเป็น safety setting และ variant ใดเป็น diagnostic เท่านั้น

## สิ่งที่ยังไม่อนุมัติ

- ยังไม่อนุมัติให้ปิด losing streak gate
- ยังไม่อนุมัติให้เพิ่ม risk
- ยังไม่อนุมัติให้เริ่ม demo forward
- ยังไม่อนุมัติให้ใช้ raw diagnostic preset บน demo/live chart

สถานะ: `IDEA_ONLY_NOT_IMPLEMENTED`
