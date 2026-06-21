# Checkpoint L: Price Action / Fibo Zone Research Specification

วันที่จัดทำ: 2026-06-22

## เป้าหมาย

Checkpoint L เป็น specification-only สำหรับการวิจัย strategy branch ในอนาคตที่ใช้แนวคิด Price Action, Fibonacci zone, support/resistance, supply/demand และ pending order

Checkpoint นี้ยังไม่ implement strategy, ไม่เปลี่ยน baseline strategy logic, ไม่รัน MT5, ไม่ optimize parameter, ไม่เพิ่ม lot/risk และไม่ claim profitability

## Strategy Concept

แนวคิดหลักที่อนุญาตให้วิจัยในอนาคต:

- Price Action Break & Retest: รอราคา break โครงสร้างสำคัญ แล้วกลับมา retest ก่อนเข้า
- Fibo Zone Pullback: วัด swing ล่าสุด แล้วพิจารณา pullback ในโซน 38.2, 50, 61.8, 78.6
- Support/Resistance Zone: ใช้ swing high/low และ reaction area เพื่อสร้าง zone ที่วัดได้
- Supply/Demand Zone: ระบุ impulse move หลัง base area เพื่อใช้เป็นเขต reaction
- Optional Pending Order: วาง pending order เฉพาะเมื่อ setup ยัง valid และมี stop loss ชัดเจน

ทุกแนวคิดต้องแปลงเป็นกฎที่วัดได้ด้วยข้อมูลราคา ไม่ใช้การตีความด้วยสายตาแบบ subjective

## สิ่งที่อนุญาต

- จำกัดจำนวน pending orders สูงสุด
- จำกัดจำนวน open orders สูงสุด
- จำกัด total exposure สูงสุดต่อ symbol และต่อ EA
- ต้องมี hard stop loss ทุก order
- ใช้ risk per trade จาก `RiskManager` เดิม
- ใช้ Strategy Tester เท่านั้นในช่วง research
- ใช้ `_Symbol` และ broker metadata จริงเท่านั้น
- ใช้ spread filter, stops level, freeze level และ margin check เดิม
- ยกเลิก pending order เมื่อ setup invalidate
- ไม่ force min lot ถ้า risk budget ไม่พอ
- ไม่เพิ่ม lot หลังขาดทุน

## สิ่งที่ห้าม

- Martingale
- Unlimited grid
- Recovery lot multiplication
- No-stop-loss zone holding
- การเพิ่ม order ไปเรื่อย ๆ เมื่อราคาวิ่งสวนทาง
- การซ่อน floating loss ด้วยการปิดเฉพาะ order ที่กำไร
- การใช้ Price Action/Fibo เพื่อ bypass risk controls
- การเพิ่ม exposure เพื่อให้ backtest ดูดีขึ้น

## Code-Ready Rule Translation

### Swing High / Swing Low

Swing high ที่ index `i`:

- `High[i]` ต้องสูงกว่า high ของ `N` bars ซ้ายและ `N` bars ขวา
- ค่าเริ่มต้นสำหรับวิจัยในอนาคตควรเป็น parameter เช่น `SwingLookbackBars`
- ต้องใช้ closed bars เท่านั้น ห้ามใช้แท่งปัจจุบันที่ยังไม่ปิด

Swing low ที่ index `i`:

- `Low[i]` ต้องต่ำกว่า low ของ `N` bars ซ้ายและ `N` bars ขวา
- ใช้ closed bars เท่านั้น

### Support / Resistance Zone

Support zone:

- สร้างจาก swing low ล่าสุด หรือ cluster ของ swing lows ที่ราคาใกล้กัน
- Zone height ต้องวัดได้ เช่น `max(ATR * ZoneAtrMultiplier, MinZonePoints * Point)`
- Zone ต้องหมดอายุหลังจำนวน bars ที่กำหนด

Resistance zone:

- สร้างจาก swing high ล่าสุด หรือ cluster ของ swing highs ที่ราคาใกล้กัน
- ใช้ zone height และ expiry แบบเดียวกับ support

### Fibonacci Zone

Bullish pullback:

- ใช้ swing low เป็น anchor 0%
- ใช้ swing high เป็น anchor 100%
- Fibo retracement levels: 38.2, 50.0, 61.8, 78.6
- Valid pullback zone คือราคากลับเข้าช่วงที่กำหนด เช่น 50-61.8 หรือ 61.8-78.6

Bearish pullback:

- ใช้ swing high เป็น anchor 0%
- ใช้ swing low เป็น anchor 100%
- ใช้ retracement levels เดียวกันแต่ทิศทางกลับกัน

### Breakout Definition

Bullish breakout:

- Candle close ต้องปิดเหนือ resistance zone high
- ระยะปิดเหนือ zone อย่างน้อย `BreakoutBufferPoints`
- Volume/tick volume filter เป็น optional diagnostic เท่านั้น

Bearish breakout:

- Candle close ต้องปิดต่ำกว่า support zone low
- ระยะปิดต่ำกว่า zone อย่างน้อย `BreakoutBufferPoints`

### Retest Definition

Bullish retest:

- หลัง bullish breakout ราคา pullback กลับมาแตะ breakout zone หรือ fibo zone
- Low ของ candle ต้องเข้าถึง zone
- Close ต้องไม่ปิดต่ำกว่า invalidation level

Bearish retest:

- หลัง bearish breakout ราคา pullback กลับมาแตะ breakout zone หรือ fibo zone
- High ของ candle ต้องเข้าถึง zone
- Close ต้องไม่ปิดเหนือ invalidation level

### Rejection Candle Definition

Bullish rejection:

- Lower wick >= `WickToBodyRatio * BodySize`
- Close อยู่เหนือ candle midpoint
- Candle low อยู่ใน support/fibo zone

Bearish rejection:

- Upper wick >= `WickToBodyRatio * BodySize`
- Close อยู่ต่ำกว่า candle midpoint
- Candle high อยู่ใน resistance/fibo zone

### Engulfing Candle Definition

Bullish engulfing:

- Current candle close > open
- Previous candle close < open
- Current body high >= previous body high
- Current body low <= previous body low

Bearish engulfing:

- Current candle close < open
- Previous candle close > open
- Current body high >= previous body high
- Current body low <= previous body low

### Stop Loss Placement

Buy setup:

- SL ต้องอยู่ต่ำกว่า zone low หรือ swing low
- เพิ่ม buffer เช่น `StopBufferAtrMultiplier * ATR`
- SL distance ต้องผ่าน stops level/freeze level และ risk budget

Sell setup:

- SL ต้องอยู่เหนือ zone high หรือ swing high
- เพิ่ม buffer เช่น `StopBufferAtrMultiplier * ATR`

### Take Profit Placement

TP options สำหรับวิจัย:

- fixed reward:risk เช่น 1.5R หรือ 2.0R
- next opposing zone
- prior swing high/low

ต้อง pre-register ก่อน run research ห้ามเลือกย้อนหลังจากผล backtest

### Invalid Setup Condition

Setup ต้อง invalidate เมื่อ:

- ราคา close ทะลุ invalidation level
- zone หมดอายุ
- spread สูงกว่า limit
- regime เป็น unsafe
- risk budget ไม่พอสำหรับ min lot
- มี order/position เกิน limit
- pending order ยังไม่ fill ภายในจำนวน bars ที่กำหนด

## Future Module Design Only

ยังไม่สร้าง active strategy implementation ใน checkpoint นี้

ไฟล์ที่อาจสร้างใน checkpoint implementation อนาคต:

- `MQL5/Include/ForexAiTrade/Strategies/PriceActionFiboStrategy.mqh`
- `presets/research/price_action_fibo/`

Future module ควรมี responsibility:

- ตรวจ swing structure
- สร้าง support/resistance/fibo zones
- ตรวจ confirmation candle
- สร้าง signal หรือ pending order request
- ส่ง order request ผ่าน RiskManager และ execution safety gates เดิมเท่านั้น
- log setup, invalidation, pending fill/cancel reason

## Symbol Profile Separation

### EURUSD Baseline Profile

- EURUSD H1 remains the first research baseline.
- Future Price Action/Fibo implementation should start with EURUSD only.
- EURUSD results must be compared against the current EURUSD H1 baseline.
- EURUSD success does not imply success on other symbols.

### Other Forex Pairs Profile

- Other pairs such as USDJPY#, GBPUSD, or other broker-specific forex symbols must be validated separately.
- They may reuse the same conceptual Price Action/Fibo rules, but must not automatically reuse EURUSD parameters.
- Each symbol must have its own train, validation, and out-of-sample results.
- Each symbol must pass annual target and risk-adjusted viability checks independently.

### Gold Profile

- GOLD# / GOLDm# must be treated as a separate instrument class.
- Do not reuse EURUSD SL/TP, ATR, zone width, pending order spacing, or lot assumptions directly.
- Gold must use actual runtime broker metadata from `_Symbol`.
- Gold research must respect broker minimum lot and risk budget.
- Do not force broker minimum lot if it violates configured risk.
- Gold may require a larger research deposit assumption, but this is not a recommendation to trade that capital.
- Gold is not approved for demo/live forward testing until risk-budget issues are resolved.

## Required Diagnostics ก่อน Implementation

- zone source, zone age, zone height
- fibo anchors และ retracement level ที่ใช้
- confirmation type
- pending order fill rate
- pending cancel reason
- MAE/MFE หลังเข้า
- spread at setup และ spread at fill
- session/time bucket
- reason ที่ไม่เข้า trade

## Guardrail Summary

Price Action/Fibo strategy ในอนาคตต้องเป็น risk-controlled strategy ไม่ใช่ martingale/grid/recovery system

ห้ามใช้ zone หรือ pending order เพื่อสะสม position โดยไม่มี stop loss หรือเพื่อซ่อน floating loss

Checkpoint L เป็นเอกสาร specification เท่านั้น และไม่ใช่หลักฐานว่ากลยุทธ์นี้จะทำกำไรในอนาคต
