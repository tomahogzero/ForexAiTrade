# Checkpoint J: Losing Streak Cooldown Diagnostic

วันที่จัดทำ: 2026-06-21

## เป้าหมาย

Checkpoint J มีเป้าหมายเพื่อทดสอบเชิงวินิจฉัยว่า losing-streak gate ทำให้ผลวิจัยบิดเบือนมากแค่ไหน และถ้าผ่อน gate ด้วย cooldown/reset จะช่วยให้ baseline EURUSD H1 ดีขึ้นหรือแย่ลง

งานนี้ไม่ใช่ optimization, ไม่ใช่การเลือก candidate, ไม่ใช่หลักฐานว่าระบบจะทำกำไรในอนาคต และยังไม่อนุญาตให้เริ่ม demo/live forward test

## สิ่งที่เปลี่ยนใน EA

เพิ่ม input:

- `InpRiskGateMode`
- `InpLosingStreakCooldownBars`

โหมดที่รองรับ:

- `NORMAL`: ใช้ losing-streak gate ตามปกติ
- `DIAGNOSTIC_NO_LOSING_STREAK_GATE`: ปิดเฉพาะ losing-streak gate เพื่อดูผลกระทบเชิงวินิจฉัย
- `DIAGNOSTIC_FIXED_COOLDOWN`: เมื่อชน losing streak ให้พักตามจำนวน bar ที่กำหนด แล้วอนุญาตให้ประเมินใหม่
- `DIAGNOSTIC_NEXT_DAY_RESET`: เมื่อชน losing streak ให้พักถึงวันถัดไปตามเวลา broker/server

โหมดที่ขึ้นต้นด้วย `DIAGNOSTIC_` ถูกบล็อกนอก Strategy Tester เพื่อป้องกันการนำ preset วิจัยไปใช้บนกราฟ demo/live โดยไม่ตั้งใจ

## ทำไม losing-streak gate ยังสำคัญ

Losing-streak gate เป็น risk gate เพื่อปกป้องทุน ไม่ใช่ตัวเพิ่มกำไร หน้าที่หลักคือหยุดระบบเมื่อพฤติกรรมตลาดหรือกลยุทธ์เริ่มผิดจังหวะติดต่อกัน

ข้อเสียคือ gate นี้อาจทำให้การวิจัยอ่านยาก เพราะบางช่วงระบบหยุดเทรดไปเลย ทำให้ไม่รู้ว่าถ้าอนุญาตให้เทรดต่อ ผลจะฟื้นหรือจะเสียหนักกว่าเดิม Checkpoint J จึงทดสอบแบบ diagnostic เท่านั้น

## Matrix ที่รัน

RunId: `run_20260621_214917`

Symbol/timeframe/deposit:

- EURUSD H1
- Deposit 10000

Variants:

- `normal`
- `no_losing_streak_gate`
- `fixed_cooldown_24bars`
- `next_day_reset`

Phases:

- train: 2023-01-01 ถึง 2024-12-31
- validation: 2025-01-01 ถึง 2025-12-31
- out_of_sample: 2026-01-01 ถึง 2026-06-18

## ผลลัพธ์หลัก

| Variant | Train Net | Validation Net | OOS Net | Classification |
|---|---:|---:|---:|---|
| normal | -40.96 | 61.38 | 41.03 | BASELINE_NORMAL |
| no_losing_streak_gate | -418.75 | -95.49 | -82.29 | RISKY_FOR_LIVE |
| fixed_cooldown_24bars | -426.33 | -168.67 | -61.97 | REJECT_FOR_NOW |
| next_day_reset | -447.57 | -129.69 | -61.97 | REJECT_FOR_NOW |

ผลนี้บอกว่าเมื่อปล่อยหรือผ่อน losing-streak gate จำนวน trade เพิ่มขึ้นมาก แต่ validation และ out-of-sample แย่ลง ไม่ใช่ดีขึ้น

## การตีความ

`NORMAL` ยังควรถูกเก็บเป็น baseline เพราะ validation และ out-of-sample เป็นบวก และ drawdown/max consecutive losses ต่ำกว่ากลุ่ม diagnostic

`no_losing_streak_gate` เป็นโหมดอันตรายสำหรับ live/demo เพราะถอด gate ป้องกันทุนออกโดยตรง แม้จะช่วยให้เห็นพฤติกรรมหลัง losing streak ได้ แต่ผล validation/OOS แย่กว่า normal

`fixed_cooldown_24bars` และ `next_day_reset` ยังไม่ผ่าน แม้จะเปิดให้ระบบกลับมาเทรดหลังพัก แต่ validation/OOS ยังติดลบและ max consecutive losses แย่กว่า normal

## ข้อจำกัด

- เป็นการทดสอบ diagnostic รอบเดียว ไม่ใช่ optimization
- ยังไม่ได้ทดสอบหลาย symbol หรือหลาย timeframe
- ยังไม่ควรปรับพารามิเตอร์เพื่อไล่กำไร
- OOS ใช้เป็น diagnostic check เท่านั้น ไม่ควรใช้ย้อนกลับมาเลือกค่าที่ดีที่สุด

## Output ที่เกี่ยวข้อง

- `research/results/risk_gate_variant_results.csv`
- `research/results/risk_gate_variant_scores.csv`
- `research/results/risk_gate_variant_summary.md`
- `research/results/checkpoint_j_risk_gate_recommendation.md`
- `research/runs/run_20260621_214917/`
- `docs/verification/compile_after_checkpoint_J.log`

## Recommendation

คำแนะนำปัจจุบัน:

`KEEP_NORMAL_GATE_AS_BASELINE`

ยังไม่ควรเริ่ม demo/live forward test และยังไม่ควรเพิ่ม strategy ใหม่ ก่อนสรุป baseline gate/session/exit/risk behavior ให้มั่นคงกว่านี้

Checkpoint นี้ไม่มีการ optimize parameter, ไม่มีการเพิ่ม strategy ใหม่, ไม่มีการเพิ่ม risk/lot และไม่มีการ claim profitability
