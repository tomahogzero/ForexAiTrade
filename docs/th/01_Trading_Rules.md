# กฎการเทรด

ForexAiTrade จะเทรดเฉพาะเมื่อสภาพตลาดเหมาะสมและ Risk Manager อนุญาตเท่านั้น

## การเลือกกลยุทธ์ตามสภาพตลาด

- Trend regime: ใช้กลยุทธ์ trend following
- Breakout regime: ใช้กลยุทธ์ breakout
- Sideway regime: ใช้กลยุทธ์ mean reversion
- Unsafe หรือ mixed regime: ไม่เทรด

## Trend Following

กลยุทธ์ trend following ต้องการให้ fast EMA และ slow EMA สอดคล้องกับทิศทางแนวโน้ม มี EMA slope ชัดเจน และเกิด pullback เข้าหา pullback EMA ระยะ stop loss และ take profit ใช้ ATR เป็นฐาน

## Breakout

กลยุทธ์ breakout ต้องการให้ราคาปิดทะลุกรอบราคาย้อนหลัง พร้อม buffer จาก ATR เพื่อลดสัญญาณหลอก ระยะ stop loss และ take profit ใช้ ATR เป็นฐาน

## Mean Reversion

กลยุทธ์ mean reversion ใช้เฉพาะตลาด sideway โดยมองหาราคาที่ชนขอบ Bollinger Band และยืนยันด้วย RSI ระยะ stop loss และ take profit ใช้ ATR เป็นฐาน

## กฎการส่งคำสั่ง

- ค่าเริ่มต้นคือเทรดเฉพาะเมื่อเกิดแท่งใหม่ของ timeframe สัญญาณ
- ค่าเริ่มต้นคือเปิดได้เพียง 1 position ต่อ symbol ต่อ EA
- หยุดเทรดเมื่อ spread สูงกว่าค่าที่กำหนด
- ไม่เทรดบัญชีจริงเมื่อ demo-safe mode ยังเปิดอยู่
