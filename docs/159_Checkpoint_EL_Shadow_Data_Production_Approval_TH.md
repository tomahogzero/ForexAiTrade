# Checkpoint EL: Shadow Data Production Approval Package

วันที่: 2026-07-11

## Preflight Findings

- DZ `ea_mirror.log` มี `entry_reference_price`, `atr`, event time, direction และ bar OHLC จริง
- entry/ATR สามารถ extract offline จากสาม DZ runs เดิมได้ ไม่ต้องรัน MT5
- future OHLC ยังไม่มี committed coverage สำหรับ DZ population
- เครื่องมือ `paf_bars_schema_normalizer.py`, `paf_lookahead_bars_validator.py`, `paf_lookahead_joiner.py` และ `paf_first_touch_relabel.py` มีอยู่แล้ว

## แยก Approval เป็นสองจุด

### EM: Offline Event Enrichment

Extract entry/ATR จาก `ea_mirror.log` เดิมสาม run และ join กับ EH eligible 1,600 rows ด้วย run/case/event time แบบ exact match

- ห้าม MT5/Strategy Tester
- ห้าม infer missing values
- ต้องได้ match `1600/1600` มิฉะนั้นหยุด

### EN: One-Time GOLD# H1 Bars Export

สร้าง raw GOLD# H1 OHLC จาก broker history ครอบคลุม `2023-01-01 00:00:00` ถึงอย่างน้อย `2025-12-31 23:59:59` แล้ว normalize/validate แบบ offline

- ใช้ runtime broker symbol `GOLD#`; ห้าม hardcode `XAUUSD`
- ห้าม Strategy Tester, optimization, EA/preset change หรือ order
- gaps ต้องถูก validator รายงาน ห้าม bypass
- MT5 process safety: ปิดได้เฉพาะ PID ที่ workflow เริ่มเอง

## Execution State

- EL package: `DEFINED`
- EM offline extraction: `BLOCKED_UNTIL_USER_APPROVAL`
- EN bars export: `BLOCKED_UNTIL_SEPARATE_USER_APPROVAL`
- shadow backtest: `NOT_RUN`
- order logic: `FAIL_NOT_APPROVED`
- profitability claim: `NOT_ALLOWED`

## Approval Phrases

จุดที่ 1:

`อนุมัติ Checkpoint EM ให้ extract และ exact-join entry/ATR จาก DZ logs เดิมแบบ offline เท่านั้น หาก match ไม่ครบ 1600/1600 ให้หยุด`

จุดที่ 2 จะขอภายหลังเมื่อ EM ผ่าน:

`อนุมัติ Checkpoint EN ให้ทำ one-time GOLD# H1 history bars export ช่วง 2023-01-01 ถึง 2025-12-31 โดยไม่รัน Strategy Tester ไม่ส่ง order และให้หยุดหาก validator ไม่ผ่าน`

## Progress

- Diagnostic candidate: `100%`
- Shadow backtest readiness: `30%`
- Order logic/demo-live: `0%`
