# Checkpoint CU: PAF Field Presence Validation Approval Package

วันที่จัดทำ: 2026-07-09

## สถานะ

Checkpoint CU เป็น approval package เท่านั้น

ไม่ได้รัน MT5 ไม่ได้รัน Strategy Tester ไม่ได้แก้ EA/source code ไม่ได้แก้ preset ไม่ได้ optimize ไม่ได้เพิ่ม lot/risk และไม่ได้สรุปว่า strategy ทำกำไร

## ที่มา

Checkpoint CT เพิ่ม diagnostics-only PAF direction explainability fields และ compile ผ่าน:

- Commit target ที่เสนอสำหรับ validation: `fa56c3e` หรือ commit ล่าสุดของ PR #90 หลัง merge
- Compile result: `0 errors, 0 warnings`
- MT5 run ใน CT: ไม่ได้รัน
- Strategy Tester run ใน CT: ไม่ได้รัน
- PAF ยังคง diagnostic-only
- Order logic ยังถูก block

Checkpoint CU จึงเตรียม approval สำหรับการรัน Strategy Tester หนึ่งครั้งในอนาคต เพื่อพิสูจน์เฉพาะว่า field ใหม่ถูกเขียนลง EA mirror log และ parser อ่านได้จริง

## ขอบเขต Future Run ที่เสนอ

อนุมัติได้เฉพาะเมื่อผู้ใช้ให้ approval phrase แยกในอนาคต

- Run type: Strategy Tester diagnostic validation
- จำนวน run: 1 run เท่านั้น
- Symbol: `GOLD#`
- Timeframe: H1
- Date range: `2026-03-01` ถึง `2026-03-08`
- Optimization: disabled
- Demo/live/forward: ห้าม
- Market orders: ห้าม
- Pending orders: ห้าม
- Position modification: ห้าม
- Lot/risk increase: ห้าม
- Profitability interpretation: ห้าม

เหตุผลที่ใช้ window นี้: เป็น window เดิมจาก Checkpoint CP ที่ artifact path, no-trade behavior, และ baseline fallback guard เคยตรวจผ่านแล้ว จึงเหมาะสำหรับ validation เฉพาะ field presence

## Required Effective Config Assertions

ก่อนรันจริงในอนาคต ต้องยืนยัน effective config:

- `InpEnablePriceActionFibo=true`
- `InpPriceActionFiboDiagnosticsOnly=true`
- `InpPAFUsePendingOrders=false`
- `InpPAFMaxPendingOrders=0`
- `InpManageExistingPositions=false`
- `InpRequireStrategyTester=true`
- `InpPAFLogOnlyOnNewBar=true`
- Optimization disabled
- Strategy Tester only
- No existing/open position in tester context
- Source target must include Checkpoint CT field implementation

## Required Artifact Paths

future run ต้องเก็บอย่างน้อย:

- RunId
- Strategy Tester report
- tester log excerpt
- EA mirror log
- effective config snapshot
- generated tester config
- parser output
- forbidden action grep/check summary
- field presence summary
- no-trade confirmation
- baseline fallback confirmation

## Field Presence Checks

EA mirror log ต้องมี field ใหม่ต่อไปนี้อย่างน้อยหนึ่ง diagnostic line:

### Fibo Pullback Fields

- `paf_fibo_ema_fast_value=`
- `paf_fibo_ema_slow_value=`
- `paf_fibo_ema_gap_points=`
- `paf_fibo_ema_slope_state=`
- `paf_fibo_price_vs_ema_state=`
- `paf_fibo_trend_alignment_state=`
- `paf_fibo_pullback_side=`
- `paf_fibo_direction_gap_reason=`

### Zone Rejection Fields

- `paf_zone_touch_state=`
- `paf_rejection_candle_direction=`
- `paf_rejection_wick_side=`
- `paf_rejection_body_ratio=`
- `paf_rejection_wick_ratio=`
- `paf_zone_direction_gap_reason=`

Parser output ต้องมี:

- `paf_direction_gap_bucket_counts`
- `paf_fibo_direction_gap_reason_counts`
- `paf_zone_direction_gap_reason_counts`

## Pass Criteria

future run จะถือว่า field presence validation ผ่านเท่านั้นถ้า:

- Strategy Tester run completed
- report artifact exists
- EA mirror log exists
- PAF diagnostic lines exist
- every required CT field appears in EA mirror log
- parser output contains new gap reason counters
- total trades = `0`
- forbidden action marker count = `0`
- baseline fallback marker count = `0`
- no-trade confirmation is proven from report and EA logs
- no baseline fallback is proven from EA logs

## Fail / Stop Criteria

หยุดและถือว่า fail ถ้า:

- effective config mismatch
- optimization enabled
- demo/live/forward environment detected
- any market order attempt
- any pending order attempt
- any position modification attempt
- baseline strategy fallback
- missing EA mirror log
- missing Strategy Tester report
- missing any required CT field in diagnostic log
- parser crashes or omits new gap reason summaries
- log too noisy because `InpPAFLogOnlyOnNewBar` is ineffective

Forbidden markers:

- `SIGNAL_BUY`
- `SIGNAL_SELL`
- `OrderSend`
- `.Buy(`
- `.Sell(`
- `BuyLimit`
- `SellLimit`
- `BuyStop`
- `SellStop`
- `PositionModify`

## What This Future Run Must Not Prove

future run จะไม่พิสูจน์:

- profitability
- setup quality
- entry quality
- exit quality
- drawdown safety
- demo/live readiness
- order logic readiness

จุดประสงค์มีอย่างเดียว: ตรวจว่า CT fields ถูก log และ parse ได้จริงใน Strategy Tester แบบ no-trade

## Approval Phrase For Future CV Execution

ถ้าจะให้รันจริงใน checkpoint ถัดไป ให้ใช้ข้อความ:

`Approved to execute Checkpoint CV one-run PAF field presence validation with symbol GOLD# timeframe H1 date range 2026-03-01 to 2026-03-08 using CT diagnostics-only fields.`

## Decision

Checkpoint CU ยังไม่อนุมัติการรันเอง

MT5 execution ยังคง blocked จนกว่าจะมี approval phrase ข้างต้นแบบชัดเจน
