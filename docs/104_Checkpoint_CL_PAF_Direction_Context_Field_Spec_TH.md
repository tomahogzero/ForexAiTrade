# Checkpoint CL: PAF Direction Context Field Specification

Checkpoint CL เป็น specification เท่านั้น สำหรับ field ที่ควรมีในอนาคตเพื่อแก้ `DIRECTION_MISSING` ของ Price Action / Fibo diagnostics

รอบนี้:

- ไม่รัน MT5
- ไม่รัน Strategy Tester
- ไม่แก้ EA/source code
- ไม่แก้ presets
- ไม่เพิ่ม order logic
- ไม่เพิ่ม market order
- ไม่เพิ่ม pending order
- ไม่เพิ่ม position modification
- ไม่ optimize
- ไม่เพิ่ม lot/risk
- ไม่สรุป profitability
- ไม่อนุมัติ demo/live

## เหตุผล

Checkpoint CK พบว่า `DIRECTION_MISSING` มี `14` จาก `33` rows หรือ `42.42%`

Root cause:

- `FIBO_PULLBACK_EMA_DIRECTION_CONTEXT_MISSING`: `10` rows
- `ZONE_REJECTION_CANDLE_DIRECTION_CONTEXT_MISSING`: `4` rows

แปลว่า parser เห็น diagnostic event แล้ว แต่ context ยังไม่พอให้บอก buy/sell direction อย่างปลอดภัย

## Principle

Field เหล่านี้ต้องเป็น `diagnostics-only`

ห้ามใช้ field เหล่านี้เพื่อ:

- เปิด market order
- วาง pending order
- modify position
- เปลี่ยน entry/exit logic
- optimize parameter
- เพิ่ม lot/risk
- claim profitability

จนกว่าจะมี checkpoint แยกที่ review และอนุมัติอย่างชัดเจน

## Common Direction Fields

Field กลางที่ใช้ได้กับทุก PAF classification:

| Field | Type | Required | Allowed values / format | Purpose |
|---|---|---:|---|---|
| `paf_candidate_direction` | string | Yes | `BUY_CONTEXT`, `SELL_CONTEXT`, `DIRECTION_UNKNOWN` | direction ที่ diagnostic engine ประเมินได้ |
| `paf_direction_source` | string | Yes | `EMA_CONTEXT`, `CANDLE_REJECTION`, `BREAK_RETEST`, `MANUAL_UNKNOWN`, `NOT_AVAILABLE` | บอกว่าทิศทางมาจาก logic/context ไหน |
| `paf_direction_confidence` | string | Yes | `HIGH`, `MEDIUM`, `LOW`, `UNKNOWN` | ความมั่นใจเชิง diagnostic ไม่ใช่ signal confidence |
| `paf_direction_reason` | string | Yes | short reason code | อธิบายสาเหตุที่ได้/ไม่ได้ direction |
| `paf_direction_is_usable_for_first_touch` | bool/string | Yes | `true`, `false` | ใช้แยกว่า first-touch label ทำได้หรือไม่ |

Rule:

- ถ้า `paf_candidate_direction = DIRECTION_UNKNOWN` ต้องมี `paf_direction_reason`
- ถ้า `paf_direction_is_usable_for_first_touch = false` ห้ามนับเป็น relabel-ready row
- ห้าม infer direction จาก `classification` อย่างเดียว

## Fibo Pullback Fields

ใช้กับ `POSSIBLE_FIBO_PULLBACK`

| Field | Type | Required | Purpose |
|---|---|---:|---|
| `paf_ema_fast_value` | number | Recommended | EMA เร็ว ณ signal bar |
| `paf_ema_slow_value` | number | Recommended | EMA ช้า ณ signal bar |
| `paf_ema_fast_slope` | number/string | Recommended | slope หรือ direction ของ EMA เร็ว |
| `paf_ema_slow_slope` | number/string | Recommended | slope หรือ direction ของ EMA ช้า |
| `paf_trend_context` | string | Yes | `UPTREND`, `DOWNTREND`, `SIDEWAY`, `UNKNOWN` |
| `paf_pullback_side` | string | Yes | `PULLBACK_IN_UPTREND`, `PULLBACK_IN_DOWNTREND`, `UNKNOWN` |
| `paf_fibo_zone_level` | string/number | Recommended | zone/fibo level ที่เกี่ยวข้อง |

Direction mapping สำหรับ diagnostics เท่านั้น:

- `paf_trend_context = UPTREND` และ `paf_pullback_side = PULLBACK_IN_UPTREND` อาจ map เป็น `BUY_CONTEXT`
- `paf_trend_context = DOWNTREND` และ `paf_pullback_side = PULLBACK_IN_DOWNTREND` อาจ map เป็น `SELL_CONTEXT`
- ถ้า trend/pullback ขัดแย้งกัน ต้องเป็น `DIRECTION_UNKNOWN`

คำว่า "อาจ map" หมายถึง diagnostic classification เท่านั้น ไม่ใช่คำสั่งเทรด

## Zone Rejection Fields

ใช้กับ `POSSIBLE_ZONE_REJECTION`

| Field | Type | Required | Purpose |
|---|---|---:|---|
| `paf_zone_side` | string | Yes | `SUPPORT_ZONE`, `RESISTANCE_ZONE`, `UNKNOWN` |
| `paf_rejection_side` | string | Yes | `REJECT_UP_FROM_SUPPORT`, `REJECT_DOWN_FROM_RESISTANCE`, `UNKNOWN` |
| `paf_candle_body_direction` | string | Recommended | `BULLISH`, `BEARISH`, `DOJI`, `UNKNOWN` |
| `paf_wick_side` | string | Recommended | `LOWER_WICK`, `UPPER_WICK`, `BOTH`, `NONE`, `UNKNOWN` |
| `paf_rejection_strength` | string | Optional | `HIGH`, `MEDIUM`, `LOW`, `UNKNOWN` |

Direction mapping สำหรับ diagnostics เท่านั้น:

- `SUPPORT_ZONE` + `REJECT_UP_FROM_SUPPORT` อาจ map เป็น `BUY_CONTEXT`
- `RESISTANCE_ZONE` + `REJECT_DOWN_FROM_RESISTANCE` อาจ map เป็น `SELL_CONTEXT`
- ถ้า zone/rejection/candle ขัดแย้งกัน ต้องเป็น `DIRECTION_UNKNOWN`

## Break Retest Fields

ใช้กับ `POSSIBLE_BREAK_RETEST`

| Field | Type | Required | Purpose |
|---|---|---:|---|
| `paf_break_direction` | string | Yes | `BREAK_UP`, `BREAK_DOWN`, `UNKNOWN` |
| `paf_retest_side` | string | Recommended | `RETEST_FROM_ABOVE`, `RETEST_FROM_BELOW`, `UNKNOWN` |
| `paf_break_level` | number | Recommended | price level ที่ถูก break/retest |

Direction mapping สำหรับ diagnostics เท่านั้น:

- `BREAK_UP` อาจ map เป็น `BUY_CONTEXT`
- `BREAK_DOWN` อาจ map เป็น `SELL_CONTEXT`
- ถ้า break/retest ขัดแย้งกัน ต้องเป็น `DIRECTION_UNKNOWN`

## Validation Rules

ก่อนนับ row เป็น first-touch ready:

1. `paf_candidate_direction` ต้องเป็น `BUY_CONTEXT` หรือ `SELL_CONTEXT`
2. `paf_direction_is_usable_for_first_touch` ต้องเป็น `true`
3. ต้องมี `entry_reference_price`
4. ต้องมี TP/SL ที่คำนวณได้จาก ATR หรือ rule ที่ระบุชัด
5. ต้องมี source metadata เช่น `run_id`, `case_id`, `event_time`, `source_file`
6. ถ้า field ขัดแย้งกัน ต้อง mark เป็น `DIRECTION_CONFLICT`

## CSV / Parser Compatibility

Parser ในอนาคตควรรองรับทั้งชื่อ field ใหม่และชื่อเก่า:

- `direction` อาจ map จาก `paf_candidate_direction`
- `direction_reason` อาจ map จาก `paf_direction_reason`
- ถ้าไม่มี field ใหม่ ให้ใช้ behavior เดิมและรายงาน missing reason

ห้าม silently fill direction โดยไม่มี reason

## Required Output in Future Audit

เมื่อ implementation ถูกอนุมัติใน checkpoint ถัดไปแล้ว audit ต้องรายงาน:

- direction missing before/after
- direction conflict count
- usable-for-first-touch count
- classification breakdown
- sample count per field source
- examples of rows that remain unknown

## Acceptance Criteria Before Future EA/Source Change

ก่อนอนุญาตให้แตะ EA/source:

- spec นี้ต้องผ่าน review
- ต้องมี checkpoint approval แยกสำหรับ implementation
- implementation ต้องเป็น diagnostics-only
- ต้องมี effective output artifact เพื่อพิสูจน์ว่า field ถูก log จริง
- ต้องไม่มี order execution path ใหม่
- ต้องไม่มี pending order path ใหม่
- ต้องไม่มี position modification ใหม่

## Decision

`DIRECTION_FIELD_SPEC_DEFINED`

`IMPLEMENTATION_NOT_APPROVED`

`ORDER_LOGIC_NOT_APPROVED`

`NOT_READY_FOR_ORDER_LOGIC`

## Guardrail Confirmation

- `MT5_NOT_RUN`
- `STRATEGY_TESTER_NOT_RUN`
- `EA_SOURCE_NOT_CHANGED`
- `PRESETS_NOT_CHANGED`
- `ORDER_LOGIC_NOT_APPROVED`
- `OPTIMIZATION_NOT_PERFORMED`
- `LOT_RISK_NOT_INCREASED`
- `PROFITABILITY_NOT_CLAIMED`
- `DEMO_LIVE_NOT_APPROVED`

