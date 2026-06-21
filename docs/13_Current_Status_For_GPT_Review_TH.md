# ForexAiTrade Current Status for GPT Review

วันที่สรุป: 2026-06-19

เอกสารนี้สรุปสถานะล่าสุดของโปรเจกต์ ForexAiTrade เพื่อส่งต่อให้ GPT หรือผู้ช่วยอีกตัวช่วย review แนวทางต่อไป

## เป้าหมายโปรเจกต์

ForexAiTrade เป็น MT5 Expert Advisor และ research pipeline สำหรับ adaptive forex trading โดยเน้น:

- Capital preservation
- Risk control
- Robustness
- Demo-first workflow
- หลีกเลี่ยง martingale/grid recovery/uncontrolled lot multiplication
- ไม่ claim profitability ก่อนผ่าน backtest/validation/out-of-sample/demo forward test

## สถานะ Source และ Compile

EA source หลักอยู่ที่:

```text
MQL5/Experts/ForexAiTrade/ForexAiTrade.mq5
MQL5/Include/ForexAiTrade/
```

ติดตั้งเข้า XM MT5 Data Folder แล้ว:

```text
C:\Users\tomah\AppData\Roaming\MetaQuotes\Terminal\BB16F565FAAA6B23A20C26C49416FF05
```

Compile ล่าสุดผ่าน:

```text
docs/verification/compile_after_file_logging.log
```

ผล compile:

```text
0 errors, 0 warnings
```

## สิ่งที่ Implement แล้ว

### Safety Inputs

- `InpLiveTradingEnabled=false` default
- `InpDemoSafeMode=true` default
- `InpRequireStrategyTester=false` default
- `InpManageExistingPositions=false` default
- `InpTradeOnlyOnNewBar=true`
- `InpRiskPercentPerTrade`
- `InpMaxDailyLossPercent`
- `InpMaxWeeklyLossPercent`
- `InpMaxTotalDrawdownPercent`
- `InpMaxOpenOrders`
- `InpMaxSpreadPoints`
- `InpMaxLosingStreak`
- `InpEquityKillSwitchPercent`

### Tester Safety

- ถ้า `InpRequireStrategyTester=true` และไม่ได้รันใน Strategy Tester:
  - block new orders
  - block position modification
  - log เหตุผล `strategy tester required by preset`

### XM Symbol Safety

รองรับ broker-specific symbols เช่น:

- `GOLD#`
- `GOLDm#`
- `USDJPY#`
- `EURUSD#`

EA ใช้ `_Symbol` และ runtime symbol metadata ไม่ hardcode symbol ใน risk/trade logic

มี canonical mapping สำหรับ reporting:

- `GOLD#` / `GOLDm#` -> `GOLD`
- `USDJPY#` -> `USDJPY`
- `EURUSD#` -> `EURUSD`

### Risk Manager

RiskManager ทำงานจาก broker metadata จริง:

- `SYMBOL_TRADE_TICK_SIZE`
- `SYMBOL_TRADE_TICK_VALUE`
- `SYMBOL_POINT`
- `SYMBOL_VOLUME_MIN`
- `SYMBOL_VOLUME_MAX`
- `SYMBOL_VOLUME_STEP`
- `SYMBOL_TRADE_CONTRACT_SIZE`
- `SYMBOL_TRADE_STOPS_LEVEL`
- `SYMBOL_TRADE_FREEZE_LEVEL`

Lot sizing เป็นแบบ risk-safe:

- คำนวณ raw lot จาก equity risk percent และ SL distance
- ปัดลงตาม lot step
- ไม่ force lot ขึ้นไป broker minimum ถ้าเกิน risk budget
- ถ้า lot ต่ำกว่า broker minimum จะ reject ด้วยเหตุผล:

```text
broker minimum lot exceeds configured risk budget
```

### File Logging

เพิ่ม optional mirror log:

- `InpMirrorLogsToFile`
- `InpMirrorLogsUseCommonFolder`
- `InpMirrorLogFileName`

Smoke/sanity presets เปิด file log แล้ว

EA file logs อยู่ที่:

```text
C:\Users\tomah\AppData\Roaming\MetaQuotes\Terminal\Common\Files\
```

ตัวอย่าง:

```text
ForexAiTrade_EURUSD_H1_smoke.log
ForexAiTrade_USDJPY_H1_smoke.log
ForexAiTrade_GOLD_H4_smoke.log
```

มี script ดึง log กลับ workspace:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\collect_ea_file_logs.ps1
```

## Scripts ที่เพิ่มแล้ว

```text
scripts/install_to_mt5.ps1
scripts/collect_smoke_test_artifacts.ps1
scripts/collect_ea_file_logs.ps1
scripts/install_tester_profiles.ps1
scripts/run_mt5_smoke_test.ps1
scripts/run_mt5_research_batch.ps1
```

หมายเหตุ: `run_mt5_research_batch.ps1` ยังต้องปรับให้เสถียรกว่านี้ เพราะ MT5/Tester log มีพฤติกรรมเขียนทับ log ระหว่างรันหลายเคส ทำให้ batch wait logic ยังไม่นิ่ง

## Presets สำคัญ

Smoke test presets:

```text
presets/tester/GOLDm#_H1_smoke_test.set
presets/tester/GOLDm#_H4_smoke_test.set
presets/tester/EURUSD_H1_smoke_test.set
presets/tester/USDJPY#_H1_smoke_test.set
```

Sanity presets:

```text
presets/sanity/GOLDm#_H1_no_trade_sanity.set
presets/sanity/EURUSD_H1_no_trade_sanity.set
```

## Smoke Test Results ล่าสุด

### EURUSD H1

Path:

```text
smoke_test_artifacts/20260619-212411/EURUSD_H1_smoke_summary.md
smoke_test_artifacts/20260619-212411/logs/20260619.log
smoke_test_artifacts/20260619-212410/ea_file_logs/ForexAiTrade_EURUSD_H1_smoke.log
```

ผล:

- Symbol: `EURUSD`
- Timeframe: H1
- Period: 2026-03-19 ถึง 2026-06-18
- Deposit: 10000 USD
- Tester status: PASS
- Final balance: 9960.16 USD
- Net result: -39.84 USD
- Accepted signals: 6
- Deal log lines: 12
- Blocked signals: 156
- Max open order blocks: 13
- Losing streak blocks: 143
- Spread/unsafe spread blocks: 97

ข้อสรุป:

- EA ทำงานและ risk/safety guards ทำงาน
- ยังไม่ profitable ในช่วง smoke test นี้

### USDJPY# H1

Path:

```text
smoke_test_artifacts/research_batch_20260619-212906/USDJPY__H1/tester_excerpt.log
```

ผล:

- Symbol: `USDJPY#`
- Canonical: `USDJPY`
- Timeframe: H1
- Deposit: 10000 USD
- Tester status: PASS
- Final balance: 9900.02 USD
- Net result: -99.98 USD
- Accepted signals: 19
- Deal log lines: 39
- Blocked signals: 45

ข้อสรุป:

- Trade execution และ symbol normalization ทำงาน
- Risk lot ประมาณ 0.03 ถึง 0.11 lot
- Max open order block ทำงาน
- ยังไม่ profitable ในช่วง smoke test นี้

### GOLD# H4

จาก tester log ล่าสุด:

- Symbol: `GOLD#`
- Canonical: `GOLD`
- Timeframe: H4
- Deposit: 10000 USD
- Tester status: PASS
- Final balance: 10000.00 USD
- Net result: 0.00 USD

ข้อสังเกต:

- มีหลาย signal แต่ถูก block ด้วย:

```text
broker minimum lot exceeds configured risk budget
```

ข้อสรุป:

- Risk manager ทำงานถูกต้อง เพราะ GOLD# contract/SL distance ทำให้ risk budget ต่ำเกิน broker min lot
- ไม่ควร force lot ให้สูงขึ้นเพื่อเปิดเทรด เพราะจะละเมิด risk-first design

## สิ่งที่ผ่าน Acceptance / Safety Review

- EA compile ผ่าน 0 errors / 0 warnings
- EA attach/run ใน Strategy Tester ได้
- Tester-only preset gate ทำงาน
- Symbol diagnostics แสดง actual/canonical และ broker metadata
- ใช้ runtime symbol เช่น `GOLD#`, `USDJPY#`, `EURUSD`
- Risk manager ไม่ force lot ขึ้น
- Spread filter / unsafe regime block ทำงาน
- Max open order block ทำงาน
- Losing streak block ทำงาน
- ไม่มี martingale/grid recovery
- ไม่มี live trading enabled by default

## ปัญหา / ข้อจำกัดที่พบ

1. Strategy ปัจจุบันยังไม่มีกำไรใน smoke runs ที่ลอง

   - EURUSD H1: ขาดทุน
   - USDJPY# H1: ขาดทุน
   - GOLD# H4: ไม่เปิด order เพราะ risk budget ต่ำกว่า broker minimum

2. Batch runner ยังไม่เสถียร

   - MT5 Tester agent log อาจถูก overwrite ต่อเคส
   - command-line config บางครั้งไม่เริ่มเคสใหม่ตาม expected timing
   - ต้องปรับ script ให้ detect run completion จาก terminal log/tester log อย่าง robust กว่านี้

3. ยังไม่ควร optimize parameter

   - การไล่จนกำไรในช่วงเดียวเสี่ยง overfit
   - ต้องแยก train/validation/out-of-sample ก่อน

## คำถามที่อยากให้ GPT ช่วย Review

1. ควรปรับ research pipeline ยังไงให้ไม่ overfit แต่ยังหา candidate ที่มีกำไรได้?
2. Batch runner สำหรับ MT5 command-line Strategy Tester ควรออกแบบยังไงให้ reliable?
3. Strategy logic ปัจจุบันควรปรับจุดไหนก่อน ระหว่าง:
   - Regime detector thresholds
   - Entry filters
   - Exit/SL/TP logic
   - Trading session/time filters
   - Spread/volatility filters
4. สำหรับ GOLD# ที่ risk budget ต่ำกว่า broker minimum ควรใช้แนวทางไหน:
   - เพิ่ม deposit
   - ลด trade frequency
   - ใช้ wider validation และไม่ force lot
   - แยก preset เฉพาะ gold ด้วย higher account size assumption
5. ควรตั้ง robustness score ยังไงให้เน้น survival มากกว่า profit?

## Recommended Next Phase

Phase ต่อไปควรเป็น Controlled Research Pipeline ไม่ใช่ “test until profit”

แนะนำ:

1. ทำให้ batch runner เสถียรก่อน
2. สร้าง test matrix:
   - Symbols: EURUSD, USDJPY#, GOLD#
   - Timeframes: H1, H4
   - Periods: train, validation, out-of-sample
3. Export report ทุกเคส
4. Parse report ด้วย Python
5. คำนวณ robustness score:
   - Net profit
   - Max drawdown
   - Profit factor
   - Trade count
   - Max consecutive losses
   - Largest loss
   - Stability across periods
6. ห้ามใช้ผล train อย่างเดียวในการตัดสิน
7. Candidate ที่ผ่านต้อง forward test demo ก่อนเสมอ

## Important Disclaimer

ผลทั้งหมดข้างต้นเป็น smoke/backtest behavior check เท่านั้น ไม่ใช่หลักฐานว่าระบบ profitable และไม่ใช่คำแนะนำให้ใช้เงินจริง

โปรเจกต์นี้ยังอยู่ใน research phase และควรยึดหลัก capital preservation ก่อนเสมอ
