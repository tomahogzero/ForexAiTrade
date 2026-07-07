# Checkpoint AW: PAF Diagnostic Field Verification Approval

วันที่จัดทำ: 2026-07-07

## สถานะ

Checkpoint AW เป็น approval-package-only checkpoint

ไม่ได้รัน MT5, ไม่ได้รัน Strategy Tester, ไม่ได้ spawn `terminal64.exe`, ไม่ได้แก้ EA/source code เพิ่มจาก Checkpoint AV, ไม่ได้แก้ presets, ไม่ได้ optimize, ไม่ได้เพิ่ม lot/risk, ไม่ได้เปิด market order, ไม่ได้เปิด pending order, ไม่ได้ modify position และไม่ได้ claim profitability

## เหตุผล

Checkpoint AV เพิ่ม diagnostic fields ใหม่ใน Price Action / Fibo log แล้ว compile ผ่าน `0 errors, 0 warnings`

แต่ยังไม่ได้พิสูจน์ว่า fields ใหม่ออกจริงใน `ea_mirror.log` จาก Strategy Tester

Checkpoint AW จึงเป็น approval package สำหรับอนุมัติ future no-trade diagnostic run แบบแคบมาก เพื่อยืนยันเฉพาะว่า log fields ใหม่ทำงานจริง

## Future Run Scope ที่เสนอ

รันใน checkpoint ถัดไปเท่านั้น หลังจาก Checkpoint AW ถูก review/merge และผู้ใช้ให้ approval phrase ชัดเจน

- Symbol: `GOLD#`
- Timeframe: `H1`
- Date range: `2026-03-01` ถึง `2026-03-08`
- จำนวน run: exactly one run
- Mode: Strategy Tester only
- Optimization: disabled
- Live/demo/forward: prohibited
- Market orders: prohibited
- Pending orders: prohibited
- Position modification: prohibited
- Lot/risk increase: prohibited
- Profitability interpretation: prohibited

เหตุผลที่เลือกช่วงนี้:

- อยู่ในกลุ่ม AQ windows เดิมที่เคย PASS no-trade diagnostic
- ช่วงสั้นพอสำหรับ field verification
- ไม่ใช่การเลือกเพื่อดู profit เพราะ run ต้องมี total trades = 0

## Required Effective Config Assertions

ก่อนรัน checkpoint ถัดไป ต้องยืนยัน effective config:

- `InpEnablePriceActionFibo=true`
- `InpPriceActionFiboDiagnosticsOnly=true`
- `InpPAFUsePendingOrders=false`
- `InpPAFMaxPendingOrders=0`
- `InpManageExistingPositions=false`
- `InpRequireStrategyTester=true`
- `InpPAFLogOnlyOnNewBar=true`
- `InpLiveTradingEnabled=true` เฉพาะเพื่อผ่าน internal tester gate เท่านั้น ไม่ใช่ approval สำหรับ demo/live
- Optimization disabled
- Strategy Tester only
- No existing/open position in tester context

## Required New Field Assertions

หลังรัน checkpoint ถัดไป ต้องพบ fields เหล่านี้ใน `ea_mirror.log` อย่างน้อยหนึ่ง diagnostic line:

- `direction_context=`
- `direction_reason=`
- `entry_reference_price=`
- `bar_open=`
- `bar_high=`
- `bar_low=`
- `bar_close=`
- `atr=`
- `ema_fast=`
- `ema_slow=`
- `bb_width_percent=`

ถ้า fields เหล่านี้ไม่ครบ ให้ถือว่า field verification fail และห้ามทำ shadow outcome run ต่อ

## Stop Conditions

ต้องหยุดทันทีถ้าเกิดข้อใดข้อหนึ่ง:

- effective config mismatch
- Strategy Tester ไม่ได้ถูกใช้
- optimization enabled
- demo/live/forward environment detected
- market order attempt
- pending order attempt
- position modification attempt
- baseline strategy fallback
- `SIGNAL_BUY` หรือ `SIGNAL_SELL` จาก PAF path
- missing `ea_mirror.log`
- missing MT5 report artifact
- fields ใหม่ไม่ปรากฏใน diagnostic line
- total trades มากกว่า `0`
- forbidden marker grep พบ order/pending/modify action

## Required Artifacts หลัง Future Run

checkpoint ถัดไปต้องเก็บ:

- RunId
- `case.json`
- `generated_tester.ini`
- `effective_preset.set`
- `process_info.json`
- `runner.log`
- `tester_log_excerpt.log`
- `ea_mirror.log`
- `mt5_report.htm`
- `parsed_result.json`
- `status.json`
- grep summary สำหรับ forbidden markers
- summary ว่า fields ใหม่ปรากฏครบหรือไม่
- no-trade confirmation
- baseline fallback confirmation

## Forbidden Markers

ต้อง grep/check อย่างน้อย:

- `OrderSend`
- `Buy(`
- `Sell(`
- `BuyLimit`
- `SellLimit`
- `BuyStop`
- `SellStop`
- `PositionModify`
- `SIGNAL_BUY`
- `SIGNAL_SELL`
- baseline strategy fallback markers

## Approval Phrase ที่ต้องใช้ก่อนรันจริง

ผู้ใช้ต้องพิมพ์ข้อความนี้ก่อน Checkpoint AX จะ execute ได้:

```text
Approved to execute Checkpoint AX one-run PAF diagnostic field verification with symbol GOLD# timeframe H1 date range 2026-03-01 to 2026-03-08 using official AK runner/parser workflow.
```

ถ้า approval phrase ไม่มี date range ชัดเจน หรือ date range ยาวกว่า 7 วัน ต้อง block execution และสร้าง approval checkpoint ใหม่

## สิ่งที่ Checkpoint AW ไม่อนุมัติ

Checkpoint AW ไม่อนุมัติ:

- market order
- pending order
- position modification
- strategy entry implementation
- strategy exit implementation
- optimization
- lot/risk increase
- demo/live forward test
- profitability claim

## Decision

```text
PAF_FIELD_VERIFICATION_APPROVAL_PACKAGE_CREATED
EXECUTION_STILL_BLOCKED_UNTIL_USER_APPROVAL
ORDER_PATH_STILL_BLOCKED
NO_OPTIMIZATION_APPROVED
NO_PROFITABILITY_CLAIM
```

## Progress Estimate

- Research system readiness: ประมาณ `59%`
- PAF diagnostic readiness: ประมาณ `53%`
- PAF field verification readiness: พร้อมรอ approval phrase
- PAF order implementation readiness: ยังไม่พร้อม
- Demo/live readiness: `0%`
- Profit proof: `0%`

