# บันทึกการ Implement Phase 2

## ไฟล์ที่สร้าง

- `mt5/Experts/ForexAiTrade.mq5`
- `mt5/Include/RiskManager.mqh`
- `mt5/Include/SymbolHelper.mqh`
- `mt5/Include/RegimeDetector.mqh`
- `mt5/Include/TradeLogger.mqh`
- `mt5/Include/Strategies/IStrategy.mqh`
- `mt5/Include/Strategies/TrendStrategy.mqh`
- `mt5/Include/Strategies/BreakoutStrategy.mqh`
- `mt5/Include/Strategies/MeanReversionStrategy.mqh`
- `mt5/Presets/EURUSD_H1_safe.set`
- `mt5/Presets/GBPUSD_H1_safe.set`
- `mt5/Presets/USDJPY#_H1_safe.set`
- `mt5/Presets/GOLDm#_H1_safe.set`
- `mt5/Presets/GOLDm#_H4_safe.set`
- `mt5/Presets/GOLD#_H1_safe.set`
- `tools/README.md`

## Inputs ที่เพิ่ม

- `InpLiveTradingEnabled=false`
- `InpDemoSafeMode=true`
- `InpMagicNumber`
- `InpRiskPerTradePercent=0.50`
- `InpMaxSpreadPoints`
- `InpMaxOpenPositionsPerSymbol=1`
- `InpMaxDailyLossPercent`
- `InpMaxWeeklyLossPercent`
- `InpMaxTotalDrawdownPercent`
- `InpMaxConsecutiveLosses`
- `InpTradeOnlyOnNewBar=true`
- `InpSignalTimeframe=PERIOD_H1`
- `InpAllowedSymbolsCsv`
- `InpCanonicalSymbolName`
- `InpBrokerSymbolSuffix`
- `InpBrokerGoldSymbolName=GOLDm#`
- `InpSanityStopLossPoints`

## Safety Checks

EA จะ block การเทรดเมื่อ:

- ยังไม่ได้เปิด `InpLiveTradingEnabled`
- เปิด demo-safe mode อยู่บนบัญชีจริง
- spread สูงกว่าค่าที่กำหนด
- จำนวน position ของ EA บน symbol นั้นถึง limit
- ขาดทุนรายวันถึง limit
- ขาดทุนรายสัปดาห์ถึง limit
- total drawdown ถึง limit
- consecutive losses ถึง limit
- `_Symbol` ปัจจุบันไม่ได้อยู่ใน `InpAllowedSymbolsCsv`
- broker symbol metadata ผิดปกติหรือหายไป
- Regime Detector คืนค่า `REGIME_UNSAFE`
- Strategy placeholder ไม่ส่งสัญญาณ

Phase 2 ไม่มี martingale, grid recovery หรือ lot multiplication แบบ uncontrolled

## Risk Manager

`RiskManager.mqh` คำนวณ lot จาก equity risk percent และระยะ stop loss เป็น points พร้อมตรวจ:

- Equity
- Risk percent
- Stop-loss distance
- Symbol point
- Tick size
- Tick value
- Contract size
- Minimum lot
- Maximum lot
- Lot step

ทุกกรณีที่ไม่ผ่านจะคืนเหตุผลชัดเจน ไม่ fail แบบเงียบๆ

## Broker Symbol Handling

EA ใช้ `_Symbol` เป็น actual runtime trading symbol เสมอ จึงรองรับชื่อแบบ XM เช่น `GOLDm#`, `GOLD#`, `USDJPY#` และ `US100Cash` โดยไม่ hardcode symbol เข้า strategy หรือ risk logic

`SymbolHelper.mqh` เก็บทั้ง:

- Actual broker symbol เช่น `GOLDm#`
- Canonical reporting symbol เช่น `XAUUSD`

ตอน `OnInit` EA จะพิมพ์ symbol diagnostics:

- Actual symbol
- Canonical symbol
- Digits
- Point
- Tick size
- Tick value
- Contract size
- Minimum lot
- Maximum lot
- Lot step
- Stops level
- Freeze level
- Spread

Risk calculation จะ query contract metadata จาก actual runtime symbol เสมอ

## วิธี Compile ใน MT5

1. คัดลอก `mt5/Experts/ForexAiTrade.mq5` ไปไว้ในโฟลเดอร์ `MQL5/Experts/` ของ MT5 หรือคงโครงสร้าง relative path เดิมไว้
2. คัดลอก `mt5/Include/*` ไปไว้ใน `MQL5/Include/` ถ้าไม่ได้ใช้ repo layout เดิม
3. เปิด `ForexAiTrade.mq5` ใน MetaEditor
4. กด `F7` หรือ Compile
5. Phase 2 ไม่ต้องใช้ external library

## No-Trade Sanity Test

1. Attach EA กับกราฟ demo เช่น EURUSD H1
2. คง `InpLiveTradingEnabled=false`
3. คง `InpDemoSafeMode=true`
4. ตรวจ Journal ว่ามี account state และ blocked reason
5. ยืนยันว่าไม่มี order ถูกเปิด
6. ถ้าทดสอบเพิ่มบน demo เท่านั้น สามารถตั้ง `InpLiveTradingEnabled=true` ได้ แต่ EA ยังควรปฏิเสธการเทรด เพราะ Regime Detector ตั้งใจคืนค่า `REGIME_UNSAFE`

บัญชีจริงจะเทรดไม่ได้ เว้นแต่ตั้ง `InpLiveTradingEnabled=true` และ `InpDemoSafeMode=false` อย่างตั้งใจพร้อมกัน ถึงอย่างนั้น Phase 2 ก็ยังไม่มี order execution อยู่ดี
