# Checkpoint I2: Losing Streak และ Risk Gate Attribution

Checkpoint I2 วิเคราะห์ว่า EURUSD H1 baseline จาก `run_20260621_205032` ได้รับผลกระทบจาก risk gate โดยเฉพาะ losing streak gate มากแค่ไหน งานนี้เป็น diagnostic attribution เท่านั้น ไม่ใช่ optimization และไม่มีการเปลี่ยน strategy logic

## ทำไม Losing Streak Gate สำคัญ

losing streak gate เป็นกลไก survival-first เพื่อหยุดระบบเมื่อมีการขาดทุนต่อเนื่อง จุดประสงค์คือป้องกันไม่ให้ EA เทรดต่อในภาวะที่สัญญาณหรือ regime อาจไม่เหมาะสม

ในระบบเงินจริง แนวคิดนี้สำคัญมาก เพราะช่วยจำกัดความเสียหายเมื่อสภาพตลาดไม่เข้ากับกลยุทธ์

## ทำไม Risk Gate อาจทำให้การวิจัยตีความยาก

ถ้า gate หยุดระบบนานมาก ผล backtest phase นั้นจะกลายเป็น `risk-gated performance` ไม่ใช่ `raw strategy performance`

ตัวอย่างจาก Checkpoint I2:

| Phase | Trades | Losing Streak Blocks | First Block | Last Block | Accepted After First Block |
|---|---:|---:|---|---|---:|
| train | 22 | 1558 | 2023-01-30 13:00:00 | 2024-12-24 14:00:00 | 0 |
| validation | 105 | 467 | 2025-05-15 18:00:00 | 2025-12-29 10:00:00 | 0 |
| out_of_sample | 62 | 143 | 2026-03-31 17:00:00 | 2026-06-16 18:00:00 | 0 |

train phase มี trade ทั้งหมดแค่ 22 ครั้ง แล้วหลัง losing streak block แรกไม่มี accepted trade เพิ่มอีกเลย นี่หมายความว่า train weakness ถูกครอบด้วย lockout behavior อย่างมาก

## Losing Streak Logic ทำงานอย่างไร

จาก code review ใน `RiskManager.mqh`:

- ใช้ `HistorySelect(0, TimeCurrent())`
- ไล่ closed deals จากล่าสุดไปหาเก่าสุด
- กรองเฉพาะ `_Symbol` และ `InpMagicNumber`
- นับเฉพาะ `DEAL_ENTRY_OUT` และ `DEAL_ENTRY_OUT_BY`
- ถ้า closed profit ติดลบ จะเพิ่ม streak
- ถ้า closed profit เป็นบวก จะหยุดนับ เท่ากับ reset streak
- ถ้า streak มากกว่าหรือเท่ากับ `InpMaxLosingStreak` จะ block new entry

ข้อสำคัญ: ถ้า EA ถูก block จนเปิด trade ใหม่ไม่ได้ ก็จะไม่มี winning closed deal ใหม่มาล้าง streak ดังนั้น lockout อาจยาวมากหรือเหมือน permanent ภายใน backtest phase ได้

## นี่เป็น Bug หรือ Safety Design

พฤติกรรมนี้เป็น safety design ที่ตั้งใจปกป้องทุน แต่เป็น research limitation ด้วย เพราะมันทำให้เราไม่เห็นว่า strategy raw behavior หลังช่วง loss cluster จะเป็นอย่างไร

จึงไม่ควรสรุปว่า train แย่เพราะ entry/exit logic อย่างเดียว ต้องแยกว่า:

- raw strategy quality
- risk-gated strategy behavior
- losing streak lockout effect

## ทำไมยังไม่ควรเปลี่ยน Live/Demo Settings

แม้ lockout จะทำให้ research interpretation ยาก แต่ไม่ได้แปลว่าควรปิด losing streak gate ใน live/demo เพราะ gate นี้มีหน้าที่ปกป้องทุน

สิ่งที่ควรทำถัดไปคือ research แบบ tester-only เพื่อเปรียบเทียบ risk-gated vs raw/cooldown behavior โดยไม่เพิ่ม risk จริง

## Recommendation

Checkpoint I2 classification:

`NEEDS_LOSING_STREAK_COOLDOWN_RESEARCH`

ความหมาย:

- baseline ยังไม่ถูก reject
- ยังไม่อนุมัติ demo forward
- ยังไม่เปลี่ยน risk setting
- ควรวิจัย cooldown/risk-gate diagnostic แยกใน Strategy Tester

## ทำไมยังไม่ใช่ Optimization

Checkpoint นี้ไม่ได้ sweep parameter, ไม่ได้ปรับ losing streak limit, ไม่ได้เพิ่ม risk, ไม่ได้เปลี่ยน entry/exit logic และไม่ได้เลือกค่าจาก OOS เป็นเพียงการอ่าน attribution ของ risk gate จาก log ที่มีอยู่แล้ว
