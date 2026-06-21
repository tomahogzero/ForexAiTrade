# เกณฑ์ Optimization

Optimization ต้องให้ความสำคัญกับ parameter ที่ทนทานและเสถียร มากกว่ากำไรย้อนหลังสูงสุด

## Primary Gates

- Profit factor อย่างน้อย 1.15
- Maximum drawdown ไม่เกิน 20%
- จำนวน trade อย่างน้อย 100 ครั้งในช่วงทดสอบ
- Maximum consecutive losses ไม่เกิน 8
- Net profit เป็นบวก

## Robustness Score

Python scoring pipeline ให้คะแนนเพิ่มจาก:

- Profit factor
- Sharpe ratio
- Net profit เป็นบวก
- จำนวน trade เพียงพอ

และหักคะแนนจาก:

- Drawdown สูง
- จำนวน trade ต่ำ
- Losing streak ยาว
- Profit factor ต่ำกว่า survival threshold
- Win rate ต่ำ

## Stability Checks

อย่ายอมรับ parameter set เพียงเพราะเป็นแถวที่ดีที่สุดใน optimization run เดียว ควรเลือกบริเวณ parameter ที่กว้างพอและค่าใกล้เคียงยังให้ผลรับได้

ใช้ `tools/stability_analysis.py` กับ optimizer exports หรือ ranked result CSV เพื่อหักคะแนนกลุ่ม parameter ที่ผลลัพธ์ดีที่สุดโดดออกจากค่าใกล้เคียงมากเกินไป จุด peak ที่แหลมและโดดเดี่ยวถือว่าเปราะบาง แม้ backtest แถวนั้นจะดูมีกำไร
