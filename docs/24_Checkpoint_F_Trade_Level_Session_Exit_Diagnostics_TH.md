# Checkpoint F: Trade-Level, Session, and Exit Diagnostics

Checkpoint นี้เพิ่ม diagnostics ระดับ trade, session, และ exit จากผล backtest เดิมเท่านั้น ไม่มีการรัน MT5 ใหม่ ไม่มีการ optimize parameter และไม่มีการแก้ strategy entry/exit logic

## ทำไมต้องดู trade-level ก่อนเพิ่ม strategy ใหม่

ถ้าดูแค่ net profit หรือ profit factor จะไม่รู้ว่ากำไร/ขาดทุนมาจากอะไร เช่น trade กระจุกตัวบาง session, loss มาจาก trade ไม่กี่ไม้, หรือ exit ทำให้โดน SL บ่อยเกินไป การเพิ่ม MicroTrend, Fibo Zone, Grid/Pending หรือ exit ใหม่ก่อนเข้าใจ trade distribution จะเพิ่มความเสี่ยง overfit

## สิ่งที่เพิ่ม

- `tools/trade_ledger_parser.py`
- `tools/session_diagnostics.py`
- per-case outputs:
  - `trade_ledger.csv`
  - `trade_ledger.json`
  - `trade_ledger_summary.md`
- aggregate outputs:
  - `research/results/trade_level_summary.md`
  - `research/results/session_diagnostics_summary.md`
  - `research/results/exit_diagnostics_summary.md`
  - `research/results/checkpoint_f_recommendation.md`

## ขอบเขตข้อมูล

Diagnostics ใช้เฉพาะ report/log ที่มีอยู่:

- `run_20260620_004501` สำหรับ `EURUSD_H1_10000`
- `run_20260621_173616` สำหรับ `EURUSD_H1_10000`
- `run_20260621_183001` สำหรับ `EURUSD_M30_10000`, `EURUSD_H1_10000`, `EURUSD_H4_10000`

ไม่มีการรัน MT5 ใหม่

## วิธีอ่าน trade-level diagnostics

`trade_ledger.csv` และ `trade_ledger.json` พยายามดึงข้อมูลต่อ trade:

- open time / close time
- symbol / timeframe
- direction
- volume
- open price / close price
- SL / TP ถ้า map จาก Orders table ได้
- profit / commission / swap
- holding duration
- exit reason จาก close deal comment เช่น `sl` หรือ `tp`

ข้อจำกัด: MT5 HTML report ไม่ได้มี magic number ที่เชื่อถือได้ และไม่เห็น trailing/breakeven modification โดยตรง

## วิธีอ่าน session diagnostics

Session bucket ใช้เวลา broker/server จาก MT5 report ก่อน ไม่แปลงเป็นเวลาไทย

- Asia
- London
- New York
- Overlap
- Other / Unknown

ใช้เพื่อดูว่า trade กระจุกหรืออ่อนในช่วงเวลาใด แต่ห้าม optimize session จาก sample เล็กโดยตรง

## วิธีอ่าน exit diagnostics

Exit diagnostics ดู:

- SL hits เทียบกับ TP hits
- average win / average loss
- win/loss ratio
- average holding time
- quick trades
- long-held trades
- largest loss concentration
- trailing/breakeven visibility

ผลปัจจุบันชี้ว่า EURUSD H1 มี exit ที่ควรวิจัยต่อ เพราะ SL-heavy และมี losing streak สูง แต่ยังไม่ควรแก้ exit logic จนกว่าจะมี logging ที่ชัดขึ้น

## ทำไมไม่ควร optimize จากจำนวน trade เล็ก

M30 และ H4 มีบางช่วงที่ trade count ต่ำมาก การปรับ parameter จาก sample เล็กอาจทำให้ได้ผลที่ดูดีเฉพาะอดีต แต่ไม่ robust ในอนาคต

## สถานะ EURUSD H1

EURUSD H1 ยังเป็น `RESEARCH_MORE` เท่านั้น ไม่ใช่ strong candidate และไม่ใช่ proof of profitability

Checkpoint F recommendation:

- `NEEDS_EXIT_RESEARCH`

ความหมายคือควรออกแบบ diagnostics/logging เพิ่มเพื่อเข้าใจ exit behavior ก่อน ไม่ใช่เริ่มแก้ strategy หรือ optimize ทันที

## ก่อนเพิ่ม MicroTrend หรือ Fibo Zone

ต้องรู้ให้ชัดก่อน:

- session weakness
- trade-level distribution
- exit behavior
- drawdown concentration
- spread/slippage sensitivity

## Guardrails

- ห้าม claim profitability
- ห้ามเริ่ม demo forward test
- ห้าม optimize parameter
- ห้ามเพิ่ม strategy ใหม่
- ห้ามแก้ entry/exit logic ใน checkpoint นี้
