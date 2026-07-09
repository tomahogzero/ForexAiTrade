# Checkpoint CO: PAF Direction Context Diagnostic Validation Approval

Checkpoint CO เป็น approval package เท่านั้น

Checkpoint นี้ไม่รัน MT5, ไม่รัน Strategy Tester, ไม่แก้ EA/source, ไม่แก้ presets, ไม่ optimize, และไม่ตีความผลเป็นกำไร

## เหตุผล

Checkpoint CN เพิ่ม `paf_*` direction context fields แล้ว แต่ยังไม่ได้พิสูจน์ด้วย Strategy Tester ว่า field ใหม่ถูกเขียนลง log จริง และช่วยลด / อธิบาย `DIRECTION_MISSING` ได้ดีขึ้นหรือไม่

ดังนั้น checkpoint ถัดไปควรเป็น diagnostic validation run แบบแคบมาก ไม่ใช่การทดลองทำกำไร

## Future Checkpoint CP ที่ขออนุมัติล่วงหน้า

Future Checkpoint CP สามารถทำได้เมื่อผู้ใช้อนุมัติชัดเจนเท่านั้น:

- รัน Strategy Tester หนึ่งครั้งเท่านั้น
- Symbol: `GOLD#` เท่านั้น เว้นแต่ผู้ใช้ระบุใหม่
- Timeframe: `H1` เท่านั้น
- Date range: short diagnostic window ไม่เกิน 1 เดือน
- ใช้ source commit หลัง CN merge: `c74296b` เว้นแต่มี checkpoint ใหม่อนุมัติ source/preset drift
- ใช้ official AK runner/parser workflow
- ไม่มี optimization
- ไม่มี demo/live/forward test
- ไม่มี market order
- ไม่มี pending order
- ไม่มี position modification
- ไม่มี lot/risk increase
- ไม่มี profitability interpretation

## Required Effective Config Assertions

ก่อนรัน future CP ต้องยืนยันค่า config จริง:

- `InpEnablePriceActionFibo=true`
- `InpPriceActionFiboDiagnosticsOnly=true`
- `InpPAFUsePendingOrders=false`
- `InpPAFMaxPendingOrders=0`
- `InpManageExistingPositions=false`
- `InpRequireStrategyTester=true`
- `InpPAFLogOnlyOnNewBar=true`
- Strategy Tester only
- Optimization disabled
- No existing/open position in tester context

## Required CN Field Evidence

หลัง future CP run ต้องมีหลักฐานว่า log มี field ต่อไปนี้:

- `paf_candidate_direction`
- `paf_direction_source`
- `paf_direction_confidence`
- `paf_direction_reason`
- `paf_direction_is_usable_for_first_touch`
- `paf_trend_context`
- `paf_pullback_side`
- `paf_ema_fast_value`
- `paf_ema_slow_value`
- `paf_ema_fast_slope`
- `paf_ema_slow_slope`
- `paf_fibo_zone_level`
- `paf_zone_side`
- `paf_rejection_side`
- `paf_candle_body_direction`
- `paf_wick_side`
- `paf_rejection_strength`
- `paf_break_direction`
- `paf_retest_side`
- `paf_break_level`

## Stop Conditions

Future CP ต้องหยุดทันทีถ้าเจอ:

- effective config mismatch
- optimization enabled
- demo/live/forward environment detected
- market order attempt
- pending order attempt
- position modification attempt
- baseline strategy fallback
- missing `paf_*` direction context fields
- log too noisy เพราะ `InpPAFLogOnlyOnNewBar` ไม่ effective
- source/preset drift จาก approved target โดยไม่มี checkpoint ใหม่

## Required Artifacts After Future CP Run

ต้องเก็บ:

- RunId
- Strategy Tester report/log path ถ้ามี
- EA mirror log
- effective config snapshot
- generated tester config
- parser output
- direction completeness summary
- guardrail grep/check summary
- no-trade confirmation
- no baseline fallback confirmation

## Pass Criteria

Future CP ผ่านได้เฉพาะด้าน diagnostics ถ้า:

- run completed หรือมี artifact เพียงพอให้วิเคราะห์
- EA mirror log มี `PriceActionFibo diagnostic:` lines
- log มี `paf_*` fields จาก Checkpoint CN
- parser อ่าน field ใหม่ได้
- no-trade confirmation ผ่านจาก log/report ที่มี
- no baseline fallback confirmation ผ่าน
- ไม่มี forbidden order/modify markers

## Fail / Inconclusive Criteria

ต้องถือว่า fail หรือ inconclusive ถ้า:

- ไม่มี EA mirror log
- ไม่มี diagnostic lines
- ไม่มี `paf_*` fields
- parser อ่าน field ใหม่ไม่ได้
- มี order/modify marker
- มี baseline fallback marker
- ไม่มี artifact เพียงพอให้ยืนยัน no-trade

## Approval Phrase สำหรับรันจริง

ก่อน future CP execution ต้องมีข้อความอนุมัติจากผู้ใช้:

`Approved to execute Checkpoint CP one-run PAF direction-context diagnostic validation with symbol GOLD# timeframe H1 date range YYYY-MM-DD to YYYY-MM-DD using official AK runner/parser workflow.`

## สถานะ

Checkpoint CO ไม่ใช่การรันจริง

ยังไม่พิสูจน์ว่า `DIRECTION_MISSING` ลดลง

ยังไม่พร้อมสำหรับ order logic

ยังไม่พร้อมสำหรับ demo/live

ยังไม่ใช่ profitability proof
