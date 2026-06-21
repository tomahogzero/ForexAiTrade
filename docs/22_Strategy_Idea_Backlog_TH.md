# Strategy Idea Backlog

เอกสารนี้เป็น backlog สำหรับแนวคิดวิจัยในอนาคตเท่านั้น ยังไม่ใช่คำสั่งให้ implement strategy

ทุก idea ต้องผ่าน specification, safety checklist, diagnostics และ research comparison plan ก่อนเริ่ม implementation

## MicroTrend Intraday M15/M30

- Hypothesis: trend ขนาดเล็กใน M15/M30 อาจเพิ่มจำนวน trade และจับ momentum ระยะสั้นได้มากกว่า H1
- Risk: trade count สูงขึ้นทำให้ spread/slippage sensitivity และ overtrading เพิ่มขึ้น
- Required diagnostics: session outcome, spread at signal, MA slope quality, losing streak, trade duration
- Reason not now: baseline EURUSD H1 ยังเป็น `RESEARCH_MORE` และ M30 เคยถูก reject for now

## Price Action Break & Retest

- Hypothesis: รอ break structure แล้ว retest zone อาจช่วยกรอง false breakout และเข้าใกล้จุด invalidation
- Risk: rule อาจ subjective ถ้าไม่กำหนด swing/zone/retest แบบ numeric
- Required diagnostics: breakout quality, retest depth, confirmation type, invalidation reason, MAE/MFE
- Reason not now: ต้องเริ่มจาก specification branch และ safety checklist ก่อน implementation

## Fibo Zone Pending Order

- Hypothesis: pending order ใน fibo pullback zone อาจช่วยให้ entry ดีขึ้นกว่าการ market entry หลังสัญญาณ
- Risk: pending order อาจกลายเป็น grid ถ้าไม่มี max order, expiry, invalidation และ exposure limit
- Required diagnostics: fill rate, cancel reason, zone touch count, adverse excursion, risk before/after fill
- Reason not now: ต้องพิสูจน์ว่าไม่ใช่ martingale/grid และต้องใช้ RiskManager เดิมเท่านั้น

## Supply/Demand Pending Order

- Hypothesis: zone ที่เกิดจาก base + impulse อาจระบุ reaction area ได้ดีขึ้น
- Risk: supply/demand zone มี subjectivity สูงและ overfit ง่าย
- Required diagnostics: zone age, retest count, impulse strength, distance to zone, invalidation reason
- Reason not now: ต้องกำหนด zone construction แบบ measurable ก่อน

## Session Filter Research

- Hypothesis: จำกัดช่วง London/New York หรือหลีกเลี่ยง rollover อาจลด spread/liquidity risk
- Risk: trade count อาจลดลงจน annualized metric misleading
- Required diagnostics: trades by hour/session, spread by session, rejected signals by session
- Reason not now: ควรใช้เป็น diagnostic ก่อน ไม่ใช่ filter เพื่อ overfit

## Exit Variant Follow-Up

- Hypothesis: exit/trailing stop ที่เหมาะสมกว่าอาจลด drawdown หรือเพิ่ม realized R
- Risk: exit tuning overfit ง่ายและอาจทำให้ OOS misleading
- Required diagnostics: exit classification, realized R, MFE/MAE, trade duration, trailing modify frequency
- Reason not now: ต้องใช้ pre-registered variants เท่านั้น ไม่เลือกค่าจาก OOS ย้อนหลัง

## Risk Gate Cooldown Follow-Up

- Hypothesis: cooldown หลัง losing streak อาจลด lockout distortion บางช่วง
- Risk: Checkpoint J พบว่าการผ่อน gate เพิ่ม trade count แต่ทำให้ validation/OOS แย่ลง
- Required diagnostics: accepted trades after first block, drawdown after cooldown, max consecutive losses
- Reason not now: normal losing-streak gate ยังเป็น baseline และ cooldown variants ถูก reject/research-only

## Rule

ห้ามเริ่ม optimization หรือ demo/live forward test จาก backlog โดยตรง

ทุก strategy idea ต้องมี:

- specification
- safety checklist
- research plan
- train/validation/out-of-sample comparison
- annual target assessment
- artifact audit
- explicit no-profitability-claim statement
