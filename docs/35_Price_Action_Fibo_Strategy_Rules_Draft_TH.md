# Price Action / Fibo Strategy Rules Draft

เอกสารนี้เป็น draft rulebook สำหรับ strategy implementation ในอนาคต ยังไม่ใช่โค้ด EA และยังไม่อนุญาตให้รัน demo/live

## Operating Mode

- Research mode เท่านั้น
- ต้องใช้ `InpRequireStrategyTester=true` ใน preset วิจัย
- ต้องใช้ `InpLiveTradingEnabled=true` ได้เฉพาะใน Strategy Tester ตาม safety gate
- ต้องใช้ `InpDemoSafeMode=true`
- ต้องใช้ RiskManager เดิมสำหรับ lot sizing

## Market Context Rules

ระบบต้องประเมิน context ก่อนหา setup:

- Symbol ต้องผ่าน allowed symbol check
- Spread ต้องไม่เกิน limit
- Regime ต้องไม่เป็น unsafe
- Broker metadata ต้อง valid
- มี position/pending order ไม่เกิน limit

## Swing Detection

ใช้ closed bars เท่านั้น

Parameter draft:

- `SwingLeftBars`
- `SwingRightBars`
- `MinSwingDistancePoints`
- `MaxSwingAgeBars`

Swing high valid เมื่อ:

- high ของ candidate bar มากกว่า high ของ bars ซ้าย/ขวาตาม parameter
- ระยะจาก swing ก่อนหน้ามากกว่า `MinSwingDistancePoints`
- swing ยังไม่หมดอายุ

Swing low valid เมื่อ:

- low ของ candidate bar ต่ำกว่า low ของ bars ซ้าย/ขวาตาม parameter
- ระยะจาก swing ก่อนหน้ามากกว่า `MinSwingDistancePoints`
- swing ยังไม่หมดอายุ

## Zone Construction

Support zone:

- ใช้ swing low valid ล่าสุด
- zone low = swing low
- zone high = swing low + zone height

Resistance zone:

- zone high = swing high
- zone low = swing high - zone height

Zone height:

- `max(ATR * ZoneAtrMultiplier, MinZonePoints * Point)`
- ต้องไม่เกิน `MaxZoneDepthPoints`

Supply/Demand zone draft:

- Base zone ต้องมี candle range เฉลี่ยต่ำกว่า ATR threshold
- Impulse candle หลัง base ต้องมี range >= `ImpulseAtrMultiplier * ATR`
- Zone ใช้ high/low ของ base area

## Fibo Pullback Rules

Bullish fibo setup:

- ต้องมี swing low ก่อน swing high
- swing high ต้องเกิดหลัง swing low
- trend/context ต้องไม่ขัดกับ buy
- pullback ต้องแตะ selected fibo band

Bearish fibo setup:

- ต้องมี swing high ก่อน swing low
- swing low ต้องเกิดหลัง swing high
- trend/context ต้องไม่ขัดกับ sell
- pullback ต้องแตะ selected fibo band

Allowed fibo bands for research:

- 38.2-50.0
- 50.0-61.8
- 61.8-78.6

ต้องเลือก band ล่วงหน้าใน preset/matrix ห้ามเลือกย้อนหลังจากผล test

## Break & Retest Rules

Bullish break:

- close เหนือ resistance zone high + buffer
- breakout candle ต้องเป็น closed candle
- breakout ต้องไม่เกิดตอน spread สูง

Bullish retest:

- low ของ candle หลัง breakout แตะ zone
- close ไม่หลุด invalidation level
- มี rejection หรือ engulfing confirmation

Bearish break:

- close ต่ำกว่า support zone low - buffer

Bearish retest:

- high ของ candle หลัง breakout แตะ zone
- close ไม่ทะลุ invalidation level
- มี rejection หรือ engulfing confirmation

## Confirmation Rules

Confirmation types:

- rejection candle
- engulfing candle
- close back inside direction after zone touch

ใช้ได้เฉพาะ confirmation ที่คำนวณได้จาก OHLC เท่านั้น

ห้ามใช้คำว่า strong, clean, obvious, beautiful, หรือ perfect โดยไม่มี numeric rule

## Entry Rules

Market entry:

- เข้าเมื่อ confirmation candle ปิดแล้ว
- entry price ใช้ bid/ask runtime symbol

Pending entry:

- buy limit ใน bullish pullback zone
- sell limit ใน bearish pullback zone
- pending order ต้องมี expiration
- pending order ต้องถูก cancel เมื่อ setup invalidate

ห้ามวาง pending order หลายชั้นแบบ grid ถ้าไม่ได้กำหนดจำนวนสูงสุดและ total exposure ล่วงหน้า

## Stop Loss Rules

Buy:

- SL ต่ำกว่า zone low หรือ swing low
- ใช้ buffer ที่วัดได้จาก ATR/points

Sell:

- SL สูงกว่า zone high หรือ swing high
- ใช้ buffer ที่วัดได้จาก ATR/points

ทุก order ต้องมี SL ตั้งแต่เปิดหรือวาง pending order

## Take Profit Rules

Draft TP options:

- Fixed R multiple
- Opposing support/resistance zone
- Prior swing high/low

TP mode ต้อง pre-register ใน research matrix

## Invalid Setup Rules

Setup invalid เมื่อ:

- close ทะลุ invalidation level
- zone expired
- fibo anchors เปลี่ยน
- spread สูงเกิน limit
- regime unsafe
- pending order หมดอายุ
- risk budget ไม่พอ
- stops/freeze level ไม่ผ่าน
- max order/exposure reached

## Logging Requirements

Future implementation ต้อง log:

- setup id
- zone type
- zone high/low
- fibo anchors
- fibo level/band
- confirmation type
- entry type: market/pending
- SL/TP
- risk money
- normalized lot
- reject/cancel reason
- setup outcome

## Research Approval Rules

Strategy branch ในอนาคตต้องผ่าน:

- train, validation, out_of_sample
- validation และ OOS ต้อง positive
- annual target framework จาก Checkpoint K
- drawdown, Calmar, PF, annualized return, trade count
- artifact audit

Train positive อย่างเดียวไม่พอ

Checkpoint นี้เป็น draft rules เท่านั้น ไม่มี trading implementation
