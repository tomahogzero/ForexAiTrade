# Checkpoint N: Price Action / Fibo Detection Diagnostics

Checkpoint N เพิ่ม diagnostic-only detection สำหรับแนวคิด Price Action / Fibo ใน ForexAiTrade โดยยังไม่เปิดสัญญาณเทรดจริง

## สิ่งที่เพิ่ม

- swing high / swing low detection
- support/resistance zone detection
- Fibonacci pullback zone calculation
- breakout detection
- retest detection
- rejection candle detection
- engulfing candle detection
- diagnostic summary logging

ทั้งหมดนี้ใช้เพื่อสังเกตพฤติกรรมและเก็บเหตุผลเชิง diagnostic เท่านั้น ไม่ใช่ trade signal

## ไม่มีสัญญาณเทรด

`CPriceActionFiboStrategy::Evaluate()` ยังคืน `SIGNAL_NONE` เสมอ

ข้อห้ามที่ยังคงอยู่:

- ไม่เปิด market order จาก Price Action / Fibo
- ไม่วาง pending order จาก Price Action / Fibo
- ไม่แก้ไข position จาก Price Action / Fibo
- ไม่ fallback ไปใช้ baseline strategy เมื่อ `InpEnablePriceActionFibo=true`
- ไม่เปลี่ยน behavior เดิมเมื่อ `InpEnablePriceActionFibo=false`

## Inputs สำหรับ Diagnostics

เพิ่ม input ภายใต้กลุ่ม `Price Action / Fibo Skeleton`:

- `InpPAFDiagnosticsEnabled=true`
- `InpPAFSwingLookbackBars=20`
- `InpPAFMinSwingDistancePoints=100`
- `InpPAFZoneAtrMultiplier=0.50`
- `InpPAFFiboLevelsCsv="38.2,50.0,61.8,78.6"`
- `InpPAFBreakoutCloseBufferAtr=0.20`
- `InpPAFRetestMaxDistanceAtr=0.50`
- `InpPAFRejectionWickBodyRatio=2.0`
- `InpPAFEngulfingMinBodyRatio=1.0`
- `InpPAFLogOnlyOnNewBar=true`

ค่าเหล่านี้ควบคุม diagnostic logging เท่านั้น ไม่ได้อนุมัติให้เทรดหรือ optimize

## Measurable Rule Definitions

### Swing High / Swing Low

- ใช้ closed bars เริ่มจาก shift 2
- ตรวจย้อนหลัง `InpPAFSwingLookbackBars`
- swing high คือ high สูงสุดในช่วง lookback
- swing low คือ low ต่ำสุดในช่วง lookback
- ถ้าข้อมูล bar ไม่พอ จะจัดเป็น `INSUFFICIENT_DATA`

### Support / Resistance Zone

- ต้องมี swing high และ swing low ก่อน
- swing distance ต้องมากกว่าหรือเท่ากับ `InpPAFMinSwingDistancePoints`
- zone width = ATR x `InpPAFZoneAtrMultiplier`
- support zone อยู่รอบ swing low
- resistance zone อยู่รอบ swing high

### Fibonacci Zone

- ใช้ range ระหว่าง swing high และ swing low
- อ่านระดับจาก `InpPAFFiboLevelsCsv`
- default levels: 38.2, 50.0, 61.8, 78.6
- คำนวณเป็น pullback จาก swing high ลงมาตามเปอร์เซ็นต์ของ range
- ถ้าไม่มี level ที่ valid ระหว่าง 0 และ 100 จะไม่สร้าง fibo zone

### Breakout

- bullish breakout: close ของ bar ล่าสุดปิดเหนือ swing high + ATR buffer
- bearish breakout: close ของ bar ล่าสุดปิดใต้ swing low - ATR buffer
- ATR buffer = ATR x `InpPAFBreakoutCloseBufferAtr`

### Retest

- bullish retest: close อยู่เหนือ swing high และ low เข้าใกล้ swing high ภายใน ATR distance
- bearish retest: close อยู่ใต้ swing low และ high เข้าใกล้ swing low ภายใน ATR distance
- ATR distance = ATR x `InpPAFRetestMaxDistanceAtr`

### Rejection Candle

- วัด wick/body ratio ของ closed bar ล่าสุด
- rejection เกิดเมื่อ upper wick หรือ lower wick >= body x `InpPAFRejectionWickBodyRatio`
- body ใช้ค่าขั้นต่ำเป็น point เพื่อกันหารด้วยศูนย์

### Engulfing Candle

- ใช้ body ของ closed bar ล่าสุดเทียบกับ body ของ bar ก่อนหน้า
- body ล่าสุดต้องใหญ่กว่า body ก่อนหน้าอย่างน้อย `InpPAFEngulfingMinBodyRatio`
- bullish engulfing และ bearish engulfing ต้องมี body overlap ตามนิยาม numeric

## Diagnostic Classifications

ผลลัพธ์ diagnostic มี classification:

- `NO_SETUP`
- `POSSIBLE_BREAK_RETEST`
- `POSSIBLE_FIBO_PULLBACK`
- `POSSIBLE_ZONE_REJECTION`
- `INSUFFICIENT_DATA`

classification เหล่านี้เป็น diagnostic-only และห้ามนำไปเปิด order ใน Checkpoint N

## Logging

เมื่อ `InpEnablePriceActionFibo=true` และ `InpPriceActionFiboDiagnosticsOnly=true` EA จะ log:

- actual symbol
- canonical symbol
- timeframe
- regime
- swing high / swing low state
- support/resistance zone
- fibo levels และ fibo zone
- breakout/retest/candle confirmation flags
- final diagnostic classification
- reason

ค่า default `InpPAFLogOnlyOnNewBar=true` เพื่อหลีกเลี่ยง log ทุก tick

## Limitations

- ยังไม่มี setup quality score
- ยังไม่มี R-multiple integration
- ยังไม่มี pending order invalidation/expiry
- ยังไม่มี train/validation/out-of-sample telemetry สำหรับ Price Action / Fibo
- ยังไม่มีการแยก symbol profile ในผล backtest เพราะยังไม่ได้รัน MT5

## ไม่ใช่ Optimization

Checkpoint N ไม่ได้ปรับ parameter เพื่อหากำไรย้อนหลัง และไม่ได้เลือกค่าเพื่อให้ผล OOS ดีขึ้น

## ไม่ใช่ Proof of Profitability

ไม่มีการรัน MT5 Strategy Tester ใน checkpoint นี้ และไม่มีการอ้างว่ากลยุทธ์นี้ทำกำไรได้

## ห้าม Demo/Live Forward Test

Price Action / Fibo ยังไม่ผ่าน research pipeline, ยังไม่มี active signal และยังไม่มี validation/OOS result จึงไม่ควรเริ่ม demo/live forward test
