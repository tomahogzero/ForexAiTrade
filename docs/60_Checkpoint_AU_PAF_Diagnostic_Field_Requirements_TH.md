# Checkpoint AU: PAF Diagnostic Field Requirements

วันที่จัดทำ: 2026-07-07

## สถานะ

Checkpoint AU เป็น documentation / research-plan only checkpoint

ไม่ได้รัน MT5, ไม่ได้รัน Strategy Tester, ไม่ได้ spawn `terminal64.exe`, ไม่ได้แก้ EA/source code, ไม่ได้แก้ presets, ไม่ได้แก้ scripts/tools, ไม่ได้ optimize, ไม่ได้เพิ่ม lot/risk, ไม่ได้เปิด market order, ไม่ได้เปิด pending order, ไม่ได้ modify position และไม่ได้ claim profitability

## เหตุผล

Checkpoint AT สร้าง parser สำหรับอ่าน Price Action / Fibo diagnostic artifacts จาก Checkpoint AQ แล้วพบว่า:

- มี diagnostic events ทั้งหมด `954`
- มี possible setup rows `267`
- possible setup rows ทั้งหมดถูก label เป็น `DIRECTION_MISSING`

ผลนี้แปลว่า diagnostic workflow เริ่มมีข้อมูล setup เพียงพอให้ศึกษา แต่ยังไม่พอสำหรับ shadow TP/SL outcome เพราะ event ไม่มี direction context และไม่มี OHLC/tick lookahead ที่ใช้วัด outcome ได้แบบ deterministic

Checkpoint AU จึงกำหนด field ที่ต้องมีในอนาคตก่อนทำ shadow outcome รอบถัดไป

## หลักการสำคัญ

ห้ามเดาทิศทางย้อนหลัง

ถ้า diagnostic event ไม่มี direction ที่เกิดจาก rule ณ เวลานั้น ต้องถือว่า `DIRECTION_MISSING` และห้ามคำนวณ TP/SL outcome

ห้ามใช้กราฟหลัง event เพื่อเลือกว่าควรเป็น buy หรือ sell เพราะจะทำให้เกิด hindsight bias และ overfit

## Required Diagnostic Fields

ทุก Price Action / Fibo diagnostic event ที่เป็น possible setup ควร log fields เหล่านี้:

| Field | Required | เหตุผล |
|---|---|---|
| `event_time` | yes | เวลา server/broker ของ bar ที่เกิด diagnostic |
| `actual_symbol` | yes | ใช้ symbol จริงของ broker เช่น `GOLD#` |
| `canonical_symbol` | yes | ใช้เพื่อ reporting เช่น `GOLD` |
| `timeframe` | yes | timeframe ที่สร้าง diagnostic เช่น `PERIOD_H1` |
| `classification` | yes | `NO_SETUP`, `POSSIBLE_FIBO_PULLBACK`, `POSSIBLE_ZONE_REJECTION`, `POSSIBLE_BREAK_RETEST` |
| `regime` | yes | regime ณ เวลานั้น เช่น trend/breakout/sideway/unsafe |
| `spread` | yes | spread ณ เวลา diagnostic |
| `direction_context` | yes | `BUY_CONTEXT`, `SELL_CONTEXT`, หรือ `DIRECTION_UNKNOWN` |
| `direction_reason` | yes | เหตุผล deterministic ที่เลือก direction context |
| `entry_reference_price` | yes | ราคาอ้างอิงสำหรับ shadow entry เช่น close ของ diagnostic bar |
| `bar_open` | yes | OHLC ของ diagnostic bar |
| `bar_high` | yes | OHLC ของ diagnostic bar |
| `bar_low` | yes | OHLC ของ diagnostic bar |
| `bar_close` | yes | OHLC ของ diagnostic bar |
| `atr` | yes | volatility context สำหรับ hypothesis ในอนาคต |
| `ema_fast` | recommended | trend context |
| `ema_slow` | recommended | trend context |
| `bb_width` | recommended | volatility/range context |
| `swing_high` | recommended | structure context |
| `swing_low` | recommended | structure context |
| `support_zone` | recommended | zone context |
| `resistance_zone` | recommended | zone context |
| `fibo_zone` | recommended | Fibo context |
| `breakout` | recommended | setup component |
| `retest` | recommended | setup component |
| `rejection_candle` | recommended | setup component |
| `engulfing_candle` | recommended | setup component |

## Direction Context Rules

`direction_context` ต้องเกิดจาก rule ที่ deterministic ณ เวลา diagnostic เท่านั้น

Allowed values:

- `BUY_CONTEXT`
- `SELL_CONTEXT`
- `DIRECTION_UNKNOWN`

ตัวอย่าง rule ที่อนุญาตในอนาคต:

- ถ้า zone ที่เกี่ยวข้องเป็น support zone และ rejection เป็น bullish ให้เป็น `BUY_CONTEXT`
- ถ้า zone ที่เกี่ยวข้องเป็น resistance zone และ rejection เป็น bearish ให้เป็น `SELL_CONTEXT`
- ถ้า break/retest อยู่เหนือ resistance เดิมและ context เป็น continuation ขึ้น ให้เป็น `BUY_CONTEXT`
- ถ้า break/retest อยู่ใต้ support เดิมและ context เป็น continuation ลง ให้เป็น `SELL_CONTEXT`
- ถ้าข้อมูลขัดแย้งหรือไม่ครบ ให้เป็น `DIRECTION_UNKNOWN`

ห้าม:

- เลือก direction จากผลลัพธ์หลัง event
- เลือก direction จากว่าราคาไปทางไหนในอนาคต
- เปลี่ยน direction rule หลังเห็น shadow outcome

## Entry Reference Rules

entry reference สำหรับ shadow outcome ต้องถูกกำหนดก่อนรัน parser

ค่าเริ่มต้นที่แนะนำสำหรับ checkpoint ถัดไป:

- `entry_reference_price = bar_close` ของ diagnostic bar
- ไม่มี spread advantage
- spread ต้องรายงานแยก ไม่ซ่อนในผลลัพธ์

ห้ามใช้ราคาที่ดีที่สุดย้อนหลัง เช่น wick low สำหรับ buy หรือ wick high สำหรับ sell ถ้าไม่ได้กำหนดไว้ล่วงหน้า

## OHLC / Lookahead Data Requirement

การวัด shadow outcome ต้องมี OHLC หรือ tick context หลัง diagnostic event

อย่างน้อยควรมี:

- diagnostic bar OHLC
- lookahead OHLC 12 bars
- lookahead OHLC 24 bars
- lookahead OHLC 48 bars

ถ้าไม่มี tick path และใน bar เดียวกันแตะทั้ง SL และ TP ต้องถือเป็น `BOTH_SAME_BAR` หรือใช้ conservative stop-first sensitivity เท่านั้น

ห้ามเลือก TP-first เพื่อให้ผลดูดีขึ้น

## Future Shadow Hypothesis Requirements

ก่อนวัด shadow outcome ต้อง pre-register:

- allowed classifications
- allowed regimes
- spread bucket thresholds
- lookahead bars
- stop hypothesis
- target hypothesis
- ambiguous bar rule
- session bucket mapping

ห้ามเลือกค่าหลังจากเห็นผลลัพธ์

## Gold-Specific Requirements

สำหรับ `GOLD#` / `GOLDm#`:

- ใช้ actual broker symbol จาก `_Symbol`
- ห้าม reuse EURUSD SL/TP/ATR/zone width โดยตรง
- ห้าม force broker minimum lot ถ้าเกิน risk budget
- ต้องแยก instrument class จาก EURUSD และ forex pairs อื่น
- deposit assumption สำหรับ research ไม่ใช่คำแนะนำให้เทรดด้วยเงินจริง

## Future Checkpoint Gate

Checkpoint AU ไม่อนุมัติให้แก้ EA หรือ implement order path

Checkpoint ถัดไปที่ปลอดภัยควรเป็น Checkpoint AV:

- ขออนุมัติแก้เฉพาะ diagnostic logging fields
- ยังต้อง diagnostics-only
- ยังต้อง no market order
- ยังต้อง no pending order
- ยังต้อง no position modification
- ยังต้อง Strategy Tester only เมื่อมีการรัน

## Decision

```text
PAF_DIAGNOSTIC_FIELD_REQUIREMENTS_DEFINED
ORDER_PATH_STILL_BLOCKED
NO_OPTIMIZATION_APPROVED
NO_PROFITABILITY_CLAIM
```

## Progress Estimate

- Research system readiness: ประมาณ `58%`
- PAF diagnostic readiness: ประมาณ `47%`
- PAF order implementation readiness: ยังไม่พร้อม
- Demo/live readiness: `0%`
- Profit proof: `0%`

