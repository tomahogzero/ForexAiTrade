# Checkpoint E: Baseline Stability and Timeframe Review

Checkpoint นี้มีเป้าหมายเพื่อดูว่า EURUSD H1 baseline เสถียรพอสำหรับการวิจัยต่อหรือไม่ โดยยังไม่เปลี่ยน strategy logic และยังไม่ optimize parameter

## สิ่งที่ทำ

- เพิ่ม `tools/baseline_stability_analysis.py`
- วิเคราะห์ `EURUSD_H1_10000` จาก run `run_20260621_173616`
- รัน controlled timeframe review สำหรับ EURUSD M30/H1/H4 ใน train, validation, out-of-sample
- สร้างผลลัพธ์ใน `research/results/`
- สร้าง note สำหรับ GOLD# risk-budget
- เพิ่ม backlog แนวคิด strategy สำหรับอนาคต แต่ยังไม่ implement

## ทำไมต้องดู baseline ก่อนเพิ่ม strategy ใหม่

ถ้า baseline ยังไม่ชัด การเพิ่ม MicroTrend, Fibo, Grid, Pending, หรือ exit ใหม่จะทำให้แยกไม่ออกว่า performance เปลี่ยนเพราะ edge จริง หรือเพราะ noise/overfit การดู baseline ก่อนช่วยให้รู้ว่าปัญหาอยู่ที่ trade count, regime filter, spread, risk budget, หรือ entry/exit quality

## EURUSD H1 สถานะปัจจุบัน

EURUSD H1 ยังเป็น `RESEARCH_MORE` ไม่ใช่ strong candidate

- train ติดลบ และมี trade count ต่ำ
- validation และ out-of-sample เป็นบวก
- validation + out-of-sample น่าสนใจกว่า train แต่ยังไม่ใช่ proof
- risk gates เช่น losing streak block, spread block, unsafe regime block มีผลต่อผลลัพธ์มาก

ข้อสรุป: ใช้ EURUSD H1 เป็น baseline สำหรับ diagnostics ต่อได้ แต่ยังไม่ควรเริ่ม demo forward test

## USDJPY สถานะปัจจุบัน

USDJPY# ถูกจัดเป็น `REJECT_FOR_NOW`

เหตุผลหลักคือผลรวมยังไม่เสถียรพอ และไม่ควร optimize แบบสุ่มเพื่อไล่กำไร เพราะมีความเสี่ยงสูงต่อ overfitting

## GOLD# สถานะปัจจุบัน

GOLD# ต้องเป็น `NEEDS_RISK_BUDGET_REVIEW`

ปัญหา validation/out-of-sample ไม่ได้แปลว่า strategy แพ้เสมอไป แต่เกิดจาก minimum lot ของ broker เมื่อเทียบกับ risk budget และ stop distance ทำให้ทุน 30000 ยังไม่พอในบางช่วง

ห้าม force min lot และห้ามเพิ่ม risk อัตโนมัติ

## Timeframe Review

ผลจาก run `run_20260621_183001`:

- M30: out-of-sample เป็นบวก แต่ validation ติดลบและมี trade ต่ำมาก
- H1: validation และ out-of-sample เป็นบวก แต่ train ติดลบ/ต่ำ
- H4: trade ต่ำและผล validation/out-of-sample ไม่ดี

ข้อสรุปปัจจุบัน: EURUSD H1 ยังเป็น baseline ที่เหมาะสุดสำหรับการวิจัยต่อ แต่ยังไม่ใช่ candidate ที่พร้อมใช้งาน

## วิธีอ่านผล

- `PASS` ใน execution หมายถึง MT5 run สำเร็จและ report parse ได้ ไม่ได้แปลว่ากลยุทธ์ดี
- `RESEARCH_MORE` หมายถึงน่าสนใจพอสำหรับ diagnostics ต่อ แต่ยังไม่พอสำหรับ forward/live
- phase ที่ trade ต่ำควรถูกระวัง เพราะ sample size อาจไม่พอ
- validation และ out-of-sample สำคัญกว่า train profit แต่ถ้า train แย่ ต้องถือเป็น warning

## ทำไมยังไม่ใช่ optimization

Checkpoint นี้รัน timeframe เปรียบเทียบด้วย logic และ conservative settings เดิม ไม่มีการไล่ parameter เพื่อหากำไรสูงสุด และไม่มีการปรับ strategy entry/exit เพื่อให้ผลดีขึ้น

## สิ่งที่ยังไม่ควรทำ

- ยังไม่ควรเริ่ม demo forward test
- ยังไม่ควรเพิ่ม MicroTrend
- ยังไม่ควรเพิ่ม Fibo/Grid/Pending strategy
- ยังไม่ควรปรับ exit/trailing stop เพื่อไล่ผลกำไร
- ยังไม่ควร claim profitability

## ไฟล์ผลลัพธ์

- `research/results/baseline_stability_summary.md`
- `research/results/baseline_stability_by_phase.csv`
- `research/results/baseline_stability_by_year_or_month.csv`
- `research/results/timeframe_review_summary.md`
- `research/results/timeframe_review_scores.csv`
- `research/results/gold_risk_budget_review.md`
