# Checkpoint D: Research Diagnostics Before Strategy Changes

วันที่: 2026-06-21

Checkpoint D เป็นเฟสวิเคราะห์ diagnostic ก่อนเปลี่ยนกลยุทธ์ จุดประสงค์คือเข้าใจว่าแต่ละ case แพ้ ชนะ หรือไม่เข้าเทรดเพราะอะไร โดยยังไม่ optimize และยังไม่แก้ entry/exit logic

## ข้อจำกัดของ Checkpoint นี้

- ไม่ optimize parameters
- ไม่เพิ่ม MicroTrend
- ไม่เปลี่ยน strategy entry/exit logic เพื่อไล่กำไร
- ไม่ claim profitability
- ไม่เริ่ม demo forward test
- ไม่ force minimum lot
- ไม่เพิ่ม risk อัตโนมัติ

## ทำไม diagnosis ต้องมาก่อน optimization

ถ้า optimize ก่อน diagnosis เราอาจแก้ปัญหาผิดจุด เช่น:

- ปรับ parameter เพื่อปิดบัง entry quality ที่ไม่ดี
- เพิ่ม risk ทั้งที่ปัญหาจริงคือ broker minimum lot
- ไล่กำไรจากช่วง validation/OOS โดยไม่เห็นว่า train อ่อน
- เลือก symbol ที่ trade count ต่ำเกินไป

Diagnostics ช่วยแยกว่า problem มาจาก:

- strategy signal quality
- exit behavior
- market regime filter
- spread
- low trade count
- losing streak/risk gate
- broker contract and minimum lot

## วิธีอ่าน diagnostics

ไฟล์หลัก:

```text
research/results/diagnostics_summary.md
research/results/diagnostics_all_cases.csv
research/results/next_research_recommendation.md
```

ในแต่ละ case folder:

```text
diagnostics.json
diagnostics_summary.md
```

ควรอ่านตามลำดับ:

1. `diagnostics_summary.md` เพื่อเห็นภาพรวม
2. `next_research_recommendation.md` เพื่อดู action เบื้องต้น
3. `diagnostics.json` ของแต่ละ case เพื่อดูตัวเลขละเอียด

## วิธีตัดสิน Reject / Keep / Research More

แนวคิดเบื้องต้น:

- `KEEP_FOR_BASELINE`: ใช้เป็น baseline เพื่อเปรียบเทียบต่อ ไม่ใช่ live-ready
- `RESEARCH_MORE`: น่าสนใจแต่ยังต้องวิเคราะห์เพิ่ม
- `REJECT_FOR_NOW`: ยังไม่ควร optimize หรือพัฒนาต่อในตอนนี้
- `NEEDS_RISK_BUDGET_REVIEW`: ต้องแก้โจทย์ risk/deposit/min lot ก่อนวิเคราะห์ strategy
- `NEEDS_TIMEFRAME_REVIEW`: timeframe ปัจจุบันอาจ trade ต่ำหรือไม่เหมาะ

## ทำไม low trade count อันตราย

Trade count ต่ำทำให้ผล backtest ไม่น่าเชื่อถือ เพราะ:

- ชนะ/แพ้ไม่กี่ครั้งเปลี่ยนผลรวมได้มาก
- profit factor อาจหลอกตา
- drawdown ยังไม่ได้สะท้อนสภาวะตลาดหลายแบบ
- validation/OOS อาจดูดีเพราะ sample น้อย

ดังนั้น case ที่ trade count ต่ำไม่ควรถูก optimize ทันที

## ทำไม GOLD# no-risk-budget ไม่ใช่ strategy failure อัตโนมัติ

GOLD# validation และ OOS มีสัญญาณ แต่หลายสัญญาณถูก block เพราะ:

```text
broker minimum lot exceeds configured risk budget
```

นี่แปลว่า lot ที่คำนวณจาก risk budget ต่ำกว่า broker minimum lot ไม่ได้แปลว่า entry logic แย่ทันที

สำหรับ run ล่าสุด `GOLD_HASH_H4_30000`:

- risk percent: `0.05`
- broker min lot: `0.01`
- deposit: `30000`
- validation estimated minimum deposit: ประมาณ `71428.57`
- out_of_sample estimated minimum deposit: ประมาณ `130434.78`

ดังนั้น 30000 ยังไม่พอสำหรับบางช่วง ถ้าจะวิจัย GOLD# ต่อ ควรทำ risk-budget review แยกก่อน อาจใช้ deposit assumption เช่น 100000 เพื่อ research เท่านั้น แต่ยังไม่ควรเพิ่ม risk หรือ force min lot อัตโนมัติ

## ทำไม USDJPY ไม่ควรถูก optimize แบบสุ่ม

USDJPY# H1 ใน run ล่าสุด:

- train ติดลบ
- validation ติดลบ
- out_of_sample ติดลบ
- train/OOS trade count ต่ำ
- rejected/blocked signals สูง

การ optimize ทันทีมีโอกาสสูงที่จะ overfit จึงควร reject for now หรือทบทวน timeframe/symbol fit ก่อน

## สรุปผลล่าสุดจาก Checkpoint D

Run:

```text
run_20260621_173616
```

Diagnosis:

- `EURUSD_H1_10000`: `RESEARCH_MORE`
- `USDJPY_HASH_H1_10000`: `REJECT_FOR_NOW`
- `GOLD_HASH_H4_30000`: `NEEDS_RISK_BUDGET_REVIEW`

ผลทั้งหมดเป็น research diagnostics เท่านั้น ไม่ใช่ proof of future profitability

