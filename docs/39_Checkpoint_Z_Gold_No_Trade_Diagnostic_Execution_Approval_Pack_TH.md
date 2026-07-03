# Checkpoint Z: Gold No-Trade Diagnostic Execution Approval Pack

วันที่จัดทำ: 2026-07-04

## สถานะของ checkpoint นี้

Checkpoint Z เป็น approval pack เท่านั้น

Checkpoint นี้ยังไม่รัน MT5, ยังไม่รัน Strategy Tester, ยังไม่ spawn `terminal64.exe`, ไม่แก้ EA/source code, ไม่แก้ presets, ไม่ optimize, ไม่เพิ่ม lot/risk, ไม่ claim profitability และไม่อนุมัติ demo/live trading

## เป้าหมาย

Checkpoint Z ล็อกกรอบสำหรับ future Gold no-trade diagnostic execution หนึ่งรอบเท่านั้น เพื่อเตรียมความพร้อมก่อนที่ผู้ใช้จะอนุมัติการรันจริงใน checkpoint ถัดไป

เป้าหมายคือพิสูจน์ว่า:

- artifact path พร้อมและตรวจสอบได้
- terminal/config handoff ไม่หลุด
- Gold diagnostic path ไม่ส่ง order
- ไม่มี baseline fallback
- missing artifacts ต้องถือว่า inconclusive

## Current known state

- Checkpoint T เคยรัน EURUSD H1 no-trade diagnostic แล้วล้มเหลวเพราะไม่มี tester artifacts
- Checkpoint W เพิ่ม verified artifact path requirements
- Checkpoint X วาง Gold 2-5% monthly research framework แบบ aggressive research target
- Checkpoint Y กำหนด Gold diagnostic data requirements และ no-trade logging plan
- Checkpoint Z ยังไม่ execute อะไร

## Proposed future run scope

Future run ที่ checkpoint ถัดไปอาจอนุมัติได้ ต้องเป็น:

- exactly one run only
- Symbol: `GOLD#` preferred if this is the actual XM Market Watch symbol
- Alternate symbol: `GOLDm#` only if verified in Market Watch / MT5 tester
- Canonical symbol: `GOLD`
- Timeframe: H1 preferred for first diagnostic
- Date range: maximum 1 month
- Strategy Tester only
- No optimization
- No demo/live/forward test
- No market orders
- No pending orders
- No position modification
- No lot/risk increase
- No profitability interpretation

ถ้า actual symbol ไม่ใช่ `GOLD#` หรือ `GOLDm#` ต้องหยุดและทำ approval pack ใหม่

## Date range

Checkpoint Z ยังไม่กำหนดวันรันจริง

Future approval ต้องใส่ concrete date range ในรูปแบบ `YYYY-MM-DD to YYYY-MM-DD`

ข้อจำกัด:

- date range ต้องไม่เกิน 1 เดือน
- ถ้าเกิน 1 เดือน ห้ามรัน
- ถ้าต้องการรันมากกว่า 1 เดือน ต้องทำ checkpoint ใหม่

## Required future approval phrase

ห้ามรัน MT5 จนกว่าผู้ใช้จะพิมพ์ approval phrase แบบนี้:

`Approved to execute Checkpoint Z Gold no-trade diagnostic with symbol GOLD# timeframe H1 date range YYYY-MM-DD to YYYY-MM-DD using verified artifact paths.`

ถ้าใช้ `GOLDm#` ต้องเปลี่ยน symbol ใน phrase ให้ตรงกับ actual broker symbol

## Required source / preset drift guard

ก่อนรันจริงต้องบันทึก:

- exact source branch
- exact source commit
- exact `MQL5/` diff status
- exact `presets/` diff status
- generated tester config path
- effective config path

ถ้า execution commit ไม่ตรงกับ commit ที่ผ่าน review:

- ต้อง prove ว่า `MQL5/` และ `presets/` ไม่มี drift
- ถ้า prove ไม่ได้ ห้ามรัน
- ถ้า `MQL5/` หรือ `presets/` เปลี่ยน ต้องทำ GPT review และ approval checkpoint ใหม่

## Required artifact path preflight

ก่อนรันจริงต้องเก็บหลักฐาน:

- exact `terminal64.exe` path
- exact MT5 data folder path from `File > Open Data Folder`
- whether portable mode is used
- whether another MT5 instance is already running
- whether spawned MT5 uses same or isolated data folder
- absolute Strategy Tester report path
- pre-created unique report folder
- writable marker file in report folder
- expected terminal log folder
- expected tester log folder
- expected EA/mirror log folder
- stale artifact inventory
- no reuse of old artifacts as proof

ถ้าขาดข้อใดข้อหนึ่ง ห้ามรัน

## Required effective config assertions

Future run ต้องมี effective config snapshot ที่ยืนยัน:

- `InpRequireStrategyTester=true`
- `InpDemoSafeMode=true`
- `InpLiveTradingEnabled=true` allowed only inside Strategy Tester to pass internal gate
- `InpManageExistingPositions=false`
- `InpEnablePriceActionFibo=true` only if using Price Action/Fibo diagnostic path
- diagnostic-only mode enabled for any Gold experimental path
- pending orders disabled
- max pending orders = 0
- no position modification
- no optimization
- symbol allowlist includes actual Gold symbol only
- canonical symbol = `GOLD`
- file/mirror logging enabled if available
- no fallback to baseline strategy unless explicitly labeled as diagnostic observation

หมายเหตุ: `InpLiveTradingEnabled=true` ใน Strategy Tester ไม่ใช่การอนุมัติ demo/live trading

## Required Gold metadata preflight

ก่อนรันต้องพิสูจน์หรือเตรียม log:

- actual symbol
- canonical symbol
- digits
- point
- tick size
- tick value
- contract size
- min lot
- max lot
- lot step
- stops level
- freeze level
- spread
- account currency
- deposit assumption

ถ้า metadata ขาดหรือ invalid ต้องหยุด

## Explicit stop conditions

หยุดทันทีถ้า:

- terminal path unknown
- data folder unknown
- report folder not writable
- already-running MT5 may intercept `/config`
- `/config` handoff not controlled
- Gold symbol unavailable
- H1 history unavailable
- date range exceeds 1 month
- optimization enabled
- effective config mismatch
- source/preset drift unproven
- missing artifact path preflight
- market order attempt
- pending order attempt
- position modification attempt
- baseline strategy fallback
- log too noisy because new-bar throttle is not effective
- demo/live/forward environment detected

## Required future artifacts

หลัง future run ต้องมี:

- RunId
- source branch and commit
- actual symbol and canonical symbol
- date range
- Strategy Tester report path
- terminal log excerpt
- tester log excerpt
- EA/mirror diagnostic log
- generated tester config
- effective config snapshot
- process info for spawned terminal
- forbidden action scan
- symbol metadata summary
- diagnostic classification summary
- no-trade confirmation
- no baseline fallback confirmation

ถ้าขาด tester report/log หรือ EA mirror log ต้องจัดเป็น:

`FAILED_NO_TESTER_ARTIFACTS / INCONCLUSIVE`

## Forbidden marker scan

ต้องค้นหาอย่างน้อย:

- `OrderSend`
- `Buy`
- `Sell`
- `BuyLimit`
- `SellLimit`
- `BuyStop`
- `SellStop`
- `PositionModify`
- `SIGNAL_BUY`
- `SIGNAL_SELL`

ข้อความ diagnostic ที่พูดถึงคำเหล่านี้ต้องแยกจาก actual trade attempt ให้ชัด

ถ้าแยกไม่ได้ ห้ามให้ PASS

## What this checkpoint does not approve

Checkpoint Z ไม่อนุมัติ:

- MT5 execution
- Strategy Tester execution
- `terminal64.exe` spawn
- source code changes
- preset changes
- runner changes
- optimization
- demo/live/forward testing
- market orders
- pending orders
- position modification
- lot/risk increase
- profitability interpretation

## Next checkpoint

ถ้า Checkpoint Z ผ่าน GPT review และถูก merge แล้ว checkpoint ถัดไปควรเป็น:

`Checkpoint AA: Gold No-Trade Diagnostic One-Run Execution Approval`

Checkpoint AA ต้องให้ผู้ใช้ใส่ approval phrase ที่มี symbol, timeframe, date range และ verified artifact paths ครบก่อนรันจริง

