# Strategy Idea Backlog

เอกสารนี้เป็นรายการแนวคิดสำหรับการวิจัยในอนาคตเท่านั้น ยังไม่ควร implement ก่อนที่ baseline stability จะชัดเจนกว่าเดิม

## MicroTrend Intraday M15/M30

- Hypothesis: ใช้ trend ขนาดเล็กใน M15/M30 อาจเพิ่มจำนวน trade และจับ momentum ช่วงสั้นได้มากกว่า H1
- Risk: จำนวน trade มากขึ้นอาจเพิ่ม spread/slippage sensitivity และเกิด overtrading ได้ง่าย
- Required diagnostics: win/loss แยกตาม session, spread at signal, MA slope quality, losing streak, trade duration, max open block
- Reason not now: EURUSD baseline ยังเป็น `RESEARCH_MORE` และ M30 validation ยังอ่อนมาก จึงยังไม่ควรเพิ่ม logic ใหม่

## Fibo Zone Pending Order Strategy

- Hypothesis: pending order ตาม retracement zone อาจช่วยให้ entry ได้ราคาดีกว่า market entry
- Risk: pending order เพิ่มความซับซ้อนด้าน expiration, false retracement, slippage, และการจัดการ order ค้าง
- Required diagnostics: fill rate, cancel reason, zone touch count, adverse excursion, risk before/after fill
- Reason not now: ยังไม่มี baseline ที่มั่นคงพอ และยังไม่ได้ออกแบบ safety สำหรับ pending order โดยเฉพาะ

## Supply/Demand Zone Pending Strategy

- Hypothesis: zone-based entry อาจช่วยกรอง trade ที่อยู่ใกล้บริเวณ liquidity หรือ reaction area
- Risk: zone detection มี subjectivity สูงและอาจ overfit ง่ายมาก
- Required diagnostics: zone age, number of retests, distance to zone, reaction strength, invalidation reason
- Reason not now: ต้องมี logging/diagnostics เพิ่มก่อน ไม่ควรใส่ zone logic ก่อนเข้าใจ baseline

## Session Filter Research

- Hypothesis: การจำกัดช่วง London/New York อาจลดช่วง spread แย่หรือ liquidity ต่ำ
- Risk: อาจลด trade count มากเกินไป และทำให้ผลขึ้นกับช่วงเวลามากเกินควร
- Required diagnostics: trade outcome by hour/session, spread by session, rejected signals by session
- Reason not now: ควรใช้เป็น diagnostic filter หลังจากเห็น monthly/session behavior ชัดกว่าเดิม

## Exit/Trailing Stop Research

- Hypothesis: exit หรือ trailing stop ที่ยืดหยุ่นขึ้นอาจลด drawdown หรือเก็บ trend ได้ดีขึ้น
- Risk: exit tuning เป็นจุดที่ overfit ได้ง่าย และอาจทำให้ backtest ดูดีโดยไม่ robust
- Required diagnostics: MFE/MAE, trade duration, exit reason, partial profit behavior, stop movement frequency
- Reason not now: ยังต้องยืนยันว่า entry/regime baseline มีความเสถียรพอ ก่อนแก้ exit logic

## Rule

ทุกแนวคิดด้านบนต้องผ่าน diagnostics ก่อน ไม่ควรเริ่ม optimization หรือ live/demo forward test จาก backlog นี้โดยตรง
