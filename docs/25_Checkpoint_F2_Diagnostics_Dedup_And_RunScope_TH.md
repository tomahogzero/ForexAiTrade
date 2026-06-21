# Checkpoint F2: Diagnostics De-duplication and Selected-Run Scope

Checkpoint นี้แก้ปัญหา aggregation ของ diagnostics เท่านั้น ไม่มีการรัน MT5 ใหม่ ไม่มีการ optimize parameter และไม่มีการแก้ MQL5 strategy logic

## ปัญหาที่พบ

Checkpoint F รวม trade/session/exit diagnostics ของ `EURUSD_H1_10000` จากหลาย run พร้อมกัน:

- `run_20260620_004501`
- `run_20260621_173616`
- `run_20260621_183001`

run เหล่านี้มี EURUSD H1 train / validation / out-of-sample ซ้ำกัน ทำให้ตัวเลข aggregate ถูกนับซ้ำ เช่น:

- trades = 567
- SL = 480
- TP = 87
- net profit = 184.35

ตัวเลขเหล่านี้ไม่ควรใช้เป็น main diagnostics เพราะเป็นการรวมผลซ้ำจากหลาย run

## สิ่งที่แก้

- เพิ่ม selected-run support ให้ diagnostics tools
- default ใหม่คือใช้ latest successful run เท่านั้น
- รองรับ `--run-id <RunId>`
- รองรับ `--latest-run`
- สร้าง `research/results/duplicates_detected.json` เพื่อบันทึก run ซ้ำแยกจากตารางหลัก
- main diagnostics ไม่ merge historical/debug runs แล้ว

## Run ที่ใช้หลังแก้

Selected RunId:

`run_20260621_183001`

## Corrected EURUSD H1 Count

หลัง de-duplication:

- train = 22 trades
- validation = 105 trades
- out_of_sample = 62 trades
- total = 189 trades

ดังนั้น main diagnostics ต้องแสดง `EURUSD_H1_10000 = 189 trades` ไม่ใช่ 567

## ทำไมต้องใช้ selected-run diagnostics

ถ้า merge ทุก historical run โดย default จะเกิดปัญหา:

- trade count ถูก inflate
- SL/TP count ถูก inflate
- session distribution ถูก inflate
- exit diagnostics ถูกบิดเบือน
- recommendation อาจดูหนักหรือเบากว่าความจริง

Historical runs ยังมีประโยชน์สำหรับ debug แต่ต้องแยกไว้ใน debug/duplicate section ไม่ใช่ main diagnostics

## Recommendation หลัง F2

Recommendation ยังเป็น:

`NEEDS_EXIT_RESEARCH`

แต่ตอนนี้อ้างอิงจาก selected-run unique data เท่านั้น:

- EURUSD H1 trades = 189
- SL = 160
- TP = 29
- max consecutive losses = 7

ความหมายคือควรวิจัย exit/logging ต่อ แต่ยังไม่ควรแก้ exit logic หรือ optimize parameter

## Phase-Level H1 Diagnostics

F2 เพิ่ม section แยก phase สำหรับ EURUSD H1:

- train
- validation
- out_of_sample

สิ่งนี้สำคัญเพราะ train ยังอ่อน ขณะที่ validation และ out-of-sample เป็นบวก การดู aggregate รวมอย่างเดียวอาจซ่อนปัญหา regime/period sensitivity

## Guardrails

- ไม่มีการรัน MT5
- ไม่มีการ optimize parameter
- ไม่มีการเพิ่ม strategy ใหม่
- ไม่มีการแก้ strategy entry/exit logic
- ไม่มีการ claim profitability
