# Checkpoint E2: Report Consistency Fix

Checkpoint นี้แก้เฉพาะความสอดคล้องของรายงานและ recommendation เท่านั้น ไม่มีการรัน MT5 ใหม่ ไม่มีการ optimize parameter และไม่มีการแก้ strategy entry/exit logic

## ปัญหาที่พบ

หลัง Checkpoint E พบว่า `research/results/diagnostics_summary.md` และ `research/results/next_research_recommendation.md` สรุป EURUSD M30/H4 ผิด โดยจัดเป็น `RESEARCH_MORE` และใช้ข้อความในเชิงว่า validation/OOS pass ทั้งที่ผลจริงไม่ผ่าน

## สิ่งที่แก้

- ปรับ `tools/research_diagnostics.py` ให้ recommendation ระดับ case อ่านผล train / validation / out-of-sample จริงก่อนตัดสิน
- ห้ามใช้คำว่า validation/OOS pass ถ้า validation หรือ out-of-sample ติดลบ หรือ trade count ต่ำเกินไป
- เพิ่ม rule ให้ validation trades ต่ำมาก เช่นน้อยกว่า 30 เป็น `REJECT_FOR_NOW`
- คง GOLD# risk-budget cases เป็น `NEEDS_RISK_BUDGET_REVIEW` เมื่อติด broker minimum lot / risk budget
- เพิ่ม alias `drawdown_relative` ใน `parsed_result.json` ให้ตรงกับ `relative_drawdown`
- เพิ่ม warning เรื่อง trade activity uneven และ monthly trade concentration ใน baseline summary

## Recommendation ที่ถูกต้องหลังแก้

| Case | Recommendation | เหตุผล |
|---|---|---|
| EURUSD_H1_10000 | RESEARCH_MORE | validation และ out-of-sample เป็นบวก แต่ train ติดลบและ train มีเพียง 22 trades ใน 2 ปี |
| EURUSD_M30_10000 | REJECT_FOR_NOW | out-of-sample เป็นบวก แต่ validation ติดลบ และ validation มีเพียง 5 trades |
| EURUSD_H4_10000 | REJECT_FOR_NOW | validation และ out-of-sample ติดลบ และ trade count ต่ำ |

## ทำไม M30 ถูก reject

M30 มี out-of-sample เป็นบวก แต่ validation ติดลบและ validation trade count ต่ำมาก จึงไม่ควรใช้ positive OOS เพียงอย่างเดียวเพื่อสรุปว่า timeframe นี้ดี

## ทำไม H4 ถูก reject

H4 มี validation และ out-of-sample ติดลบ พร้อม trade count ต่ำ จึงไม่มีหลักฐานพอสำหรับ baseline หรือ strategy work ต่อในตอนนี้

## ทำไม H1 ยังเป็นเพียง RESEARCH_MORE

H1 น่าสนใจที่สุดในสาม timeframe เพราะ validation และ out-of-sample เป็นบวก แต่ train ติดลบและ train มี trade น้อยมาก ผลบวกใน OOS ยังไม่พอสำหรับ forward/live readiness

ข้อความ warning ที่ต้องถือเป็นเงื่อนไขสำคัญ:

> Trade activity is uneven across periods. Positive OOS is not enough for forward/live readiness.

## ทำไมต้องแก้ reporting ก่อน strategy work

ถ้ารายงาน classification ไม่ตรงกับผลจริง การเพิ่ม strategy ใหม่หรือการปรับ parameter จะทำให้ตัดสินผิดทางได้ง่าย โดยเฉพาะกับ case ที่ OOS ดีแต่ validation แย่ หรือ case ที่ trade count ต่ำมาก

ดังนั้นหลัง E2 ยังไม่ควร:

- เริ่ม optimization
- เพิ่ม MicroTrend
- เพิ่ม Fibo/Grid/Pending strategy
- เริ่ม demo forward test
- claim profitability

## ไฟล์ที่ regenerate

- `research/results/diagnostics_summary.md`
- `research/results/next_research_recommendation.md`
- `research/results/timeframe_review_summary.md`
- `research/results/timeframe_review_scores.csv`
- `research/results/baseline_stability_summary.md`
- `parsed_result.json` จาก report เดิมใน `research/runs/`

ทั้งหมดนี้เป็นการแก้รายงานจาก artifact เดิม ไม่ใช่การรัน MT5 ใหม่
