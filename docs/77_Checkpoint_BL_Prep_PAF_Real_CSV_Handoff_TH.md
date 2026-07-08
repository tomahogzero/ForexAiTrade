# Checkpoint BL-Prep: PAF Real CSV Handoff Guide

วันที่จัดทำ: 2026-07-08

## สถานะ

Checkpoint BL-Prep เป็นเอกสาร handoff สำหรับเตรียมไฟล์ CSV จริงก่อนรัน offline PAF pipeline เท่านั้น

Checkpoint นี้ไม่รัน MT5, ไม่รัน Strategy Tester, ไม่รัน offline pipeline, ไม่แก้ EA/source code, ไม่แก้ presets, ไม่ optimize, ไม่เพิ่ม lot/risk และไม่ claim profitability

## ทำไมต้องมี BL-Prep

Checkpoint BJ ทำให้เรามี offline pipeline runner แล้ว

Checkpoint BK กำหนด approval package สำหรับรันกับ CSV จริงแล้ว

สิ่งที่ยังขาดคือไฟล์ `GOLD#` H1 bars CSV จริงจาก XM MT5 พร้อม path ที่ Codex อ่านได้ ดังนั้น BL-Prep จะบอกให้ชัดว่าไฟล์ควรหน้าตาแบบไหน วางไว้ที่ไหน และส่งข้อความอนุมัติอย่างไรในรอบถัดไป

## Target Context

- Diagnostic RunId: `run_20260707_172236`
- Symbol: `GOLD#`
- Timeframe: `H1`
- Diagnostic range: `2026-03-01` ถึง `2026-03-08`
- Required lookahead coverage: อย่างน้อยถึง `2026-03-10 23:59:59`
- Future execution checkpoint: `Checkpoint BL`

## สิ่งที่ผู้ใช้ต้องเตรียม

เตรียมไฟล์ CSV ของ `GOLD#` H1 จาก XM MT5 อย่างใดอย่างหนึ่ง:

1. Raw MT5-style CSV
   - มี column เช่น `<DATE>`, `<TIME>`, `<OPEN>`, `<HIGH>`, `<LOW>`, `<CLOSE>`
   - เหมาะกับ export จาก MT5 แล้วให้ Codex normalize ต่อ

2. Normalized CSV
   - มี column `time`, `open`, `high`, `low`, `close`
   - timestamp ควรเป็น `YYYY-MM-DD HH:MM:SS`

ไฟล์ควรครอบคลุมช่วงเวลาอย่างน้อย:

`2026-03-01 00:00:00` ถึง `2026-03-10 23:59:59`

## ที่วางไฟล์ที่แนะนำ

แนะนำให้วางไฟล์ไว้ใน workspace หรือโฟลเดอร์ artifact ที่ Codex อ่านได้ เช่น:

`G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\manual_exports\GOLD_HASH_H1_20260301_20260310_raw.csv`

หรือถ้าเป็น normalized:

`G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\manual_exports\GOLD_HASH_H1_20260301_20260310_normalized.csv`

ควรหลีกเลี่ยง path ที่อยู่ใน temp/downloads ที่อาจถูกลบหรือย้ายง่าย

## File Naming Recommendation

ใช้ชื่อไฟล์ที่บอก symbol, timeframe, range, และ format เช่น:

- `GOLD_HASH_H1_20260301_20260310_raw_mt5.csv`
- `GOLD_HASH_H1_20260301_20260310_normalized.csv`

เหตุผลที่ใช้ `GOLD_HASH` แทน `GOLD#` ในชื่อไฟล์ เพราะ `#` อาจสร้างปัญหาในบาง shell/tool หรือระบบ upload

## ก่อนส่งให้ Codex

ตรวจสอบเบื้องต้น:

- ไฟล์เป็น `GOLD#` ไม่ใช่ `GOLDm#`, `XAUUSD`, หรือ symbol อื่น
- timeframe เป็น H1
- ครอบคลุมวันที่ที่ต้องใช้
- ไม่แก้ราคา OHLC ด้วยมือ
- ไม่ตัดแถวช่วงกลางของไฟล์
- ถ้ามี timezone/source note ให้บอกมาด้วย
- ถ้าไม่แน่ใจว่าเป็น raw หรือ normalized ให้ส่ง path มาได้ แล้ว Codex จะตรวจแบบ offline ใน checkpoint ถัดไป

## ข้อความที่ต้องส่งเพื่ออนุมัติ Checkpoint BL

หลังเตรียมไฟล์แล้ว ให้ส่งข้อความนี้โดยแทน `<absolute_path_to_csv>` ด้วย path จริง:

`Approved to execute Checkpoint BL offline PAF pipeline on real GOLD# H1 bars CSV <absolute_path_to_csv> for RunId run_20260707_172236.`

ตัวอย่าง:

`Approved to execute Checkpoint BL offline PAF pipeline on real GOLD# H1 bars CSV G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\manual_exports\GOLD_HASH_H1_20260301_20260310_raw_mt5.csv for RunId run_20260707_172236.`

## สิ่งที่ Checkpoint BL จะทำได้

Checkpoint BL ในอนาคตจะทำได้เฉพาะ:

- ตรวจว่า path เป็น absolute path และไฟล์อ่านได้
- normalize ถ้าจำเป็น
- validate schema และ coverage
- join กับ shadow outcome rows
- สร้าง summary artifact

## สิ่งที่ Checkpoint BL ยังห้ามทำ

- ห้ามรัน MT5
- ห้ามรัน Strategy Tester
- ห้ามเปิด market order
- ห้ามเปิด pending order
- ห้าม modify position
- ห้ามแก้ EA/source code
- ห้ามแก้ presets
- ห้าม optimize
- ห้ามเพิ่ม lot/risk
- ห้ามสรุปว่า strategy ทำกำไรได้จริง

## Stop Conditions

Checkpoint BL ต้องหยุดถ้า:

- ไม่พบไฟล์
- path ไม่ใช่ absolute path
- ไฟล์อ่านไม่ได้
- symbol/timeframe ไม่ชัดเจน
- coverage ไม่พอ
- normalizer fail
- validator fail
- joiner fail
- มีคำขอให้ใช้ผลเป็น profitability proof
- มีคำขอให้เปิด order path หรือ demo/live

## Guardrails

- BL-Prep เป็นเอกสารเท่านั้น
- ยังไม่มีการประมวลผลข้อมูลจริง
- ยังไม่มีการรัน offline pipeline
- ยังไม่มีการรัน MT5/Strategy Tester
- order path ยังถูก block
- demo/live ยังถูก block

## Decision

- `REAL_CSV_HANDOFF_GUIDE_DEFINED`
- `REAL_CSV_PATH_STILL_REQUIRED`
- `OFFLINE_PIPELINE_NOT_RUN`
- `MT5_NOT_RUN`
- `STRATEGY_TESTER_NOT_RUN`
- `ORDER_PATH_STILL_BLOCKED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`

## Progress Estimate

- Research infrastructure readiness: `78%`
- PAF diagnostic readiness: `70%`
- PAF shadow-outcome readiness: `67%`
- Order implementation readiness: `0%`
- Demo/live readiness: `0%`

ขั้นตอนถัดไปคือให้ผู้ใช้วางไฟล์ CSV จริงและส่ง approval phrase สำหรับ Checkpoint BL
