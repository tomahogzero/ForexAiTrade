# Checkpoint CX: Approval Package สำหรับ Multi-Window PAF Field Stability

วันที่: 2026-07-09

## สถานะของ Checkpoint นี้

Checkpoint CX เป็น approval package เท่านั้น

ยังไม่รัน MT5, ไม่รัน Strategy Tester, ไม่แก้ EA/source code, ไม่แก้ presets, ไม่ optimize, ไม่เพิ่ม lot/risk และไม่ตีความกำไร

## เหตุผลที่ต้องมี CX

Checkpoint CV ยืนยันแล้วว่า field diagnostics-only จาก Checkpoint CT ถูก log และ parse ได้ครบในหนึ่งหน้าต่างสั้น:

- RunId: `run_20260709_182444`
- Symbol: `GOLD#`
- Timeframe: `H1`
- Window: `2026-03-01` ถึง `2026-03-08`
- `total_trades=0`
- `paf_diagnostic_count=97`
- `forbidden_action_marker_count=0`
- `baseline_fallback_marker_count=0`

Checkpoint CW ตีความ artifact แล้วว่า field presence ผ่าน แต่ข้อมูลยังน้อยและยังไม่มี multi-window stability หลังเพิ่ม CT fields

ดังนั้น CX จึงกำหนดกรอบสำหรับ future diagnostic run แบบหลายหน้าต่าง เพื่อดูว่า direction-gap buckets เสถียรพอสำหรับการวิเคราะห์ต่อหรือไม่

## Future Run Scope ที่เสนอ

ยังไม่อนุมัติให้รันใน checkpoint นี้

ถ้าจะรันใน checkpoint ถัดไป ต้องมี approval phrase แยก

Future scope:

- Symbol: `GOLD#`
- Timeframe: `H1`
- Strategy Tester only
- Diagnostic-only
- No optimization
- No demo/live/forward test
- No market orders
- No pending orders
- No position modification
- No lot/risk increase
- No profitability interpretation
- Use official AK runner/parser workflow
- Stop only the exact MT5 process started by the runner

## Proposed Windows

ใช้หลายหน้าต่างสั้น ไม่ใช่ parameter search:

| Window | Date from | Date to | Purpose |
|---|---|---|---|
| CX-W1 | `2026-03-08` | `2026-03-15` | ตรวจ field presence หลัง CV window |
| CX-W2 | `2026-03-15` | `2026-03-22` | ตรวจ distribution ของ gap buckets |
| CX-W3 | `2026-03-22` | `2026-03-29` | ตรวจ stability เพิ่มอีกช่วง |

CV window `2026-03-01` ถึง `2026-03-08` ใช้เป็น reference เท่านั้น ไม่ควรนับซ้ำเป็น run ใหม่ถ้าไม่จำเป็น

## Required Effective Config Assertions

ก่อน future run ต้องยืนยัน:

- `InpEnablePriceActionFibo=true`
- `InpPriceActionFiboDiagnosticsOnly=true`
- `InpPAFUsePendingOrders=false`
- `InpPAFMaxPendingOrders=0`
- `InpManageExistingPositions=false`
- `InpRequireStrategyTester=true`
- `InpPAFLogOnlyOnNewBar=true`
- CT explainability fields enabled by current source
- Optimization disabled
- Strategy Tester only
- No existing/open position in tester context

## Required Field Presence Checks

ทุก window ต้องมี field ต่อไปนี้ใน `ea_mirror.log`:

- `paf_fibo_ema_fast_value`
- `paf_fibo_ema_slow_value`
- `paf_fibo_ema_gap_points`
- `paf_fibo_ema_slope_state`
- `paf_fibo_price_vs_ema_state`
- `paf_fibo_trend_alignment_state`
- `paf_fibo_pullback_side`
- `paf_fibo_direction_gap_reason`
- `paf_zone_touch_state`
- `paf_rejection_candle_direction`
- `paf_rejection_wick_side`
- `paf_rejection_body_ratio`
- `paf_rejection_wick_ratio`
- `paf_zone_direction_gap_reason`

Parser output ต้องมี:

- `paf_direction_gap_bucket_counts`
- `paf_fibo_direction_gap_reason_counts`
- `paf_zone_direction_gap_reason_counts`

## Stop Conditions

future run ต้องหยุดและถือว่า fail/inconclusive ถ้าเกิดข้อใดข้อหนึ่ง:

- effective config ไม่ตรง diagnostic-only settings
- optimization enabled
- demo/live/forward environment detected
- market order attempt
- pending order attempt
- position modification attempt
- baseline strategy fallback
- `SIGNAL_BUY` หรือ `SIGNAL_SELL` จาก PAF path
- missing `ea_mirror.log`
- missing `mt5_report.htm`
- missing `paf_diagnostics.json`
- CT field ใด field หนึ่งหายจาก diagnostic lines
- parser ไม่สร้าง gap reason summaries
- runner ไม่สามารถระบุ spawned MT5 PID ได้

## Required Artifacts After Future Run

แต่ละ window ต้องมี:

- `case.json`
- `generated_tester.ini`
- `effective_preset.set`
- `process_info.json`
- `runner.log`
- `tester_log_excerpt.log`
- `ea_mirror.log`
- `mt5_report.htm`
- `parsed_result.json`
- `paf_diagnostics.json`
- `paf_diagnostics_summary.md`
- `status.json`

Aggregate ที่ต้องสร้างหลัง future run:

- multi-window field presence summary
- direction-gap bucket comparison
- no-trade confirmation summary
- forbidden action grep/check summary
- baseline fallback confirmation summary

## Pass Criteria

ถือว่า future CX execution ผ่านเฉพาะด้าน diagnostics ถ้า:

- ทุก window มี `execution_status=PASS`
- ทุก window มี `report_artifact_status=FOUND`
- ทุก window มี `total_trades=0`
- ทุก window มี `paf_diagnostics_status=FOUND`
- ทุก window มี CT fields ครบ
- ทุก window มี parser gap reason summaries
- forbidden action marker count = `0`
- baseline fallback marker count = `0`
- no-trade confirmation ผ่านจาก report และ EA logs

## Fail / Inconclusive Criteria

ถือว่า fail หรือ inconclusive ถ้า:

- report/log artifact หาย
- มี trade ใด ๆ
- มี order attempt ใด ๆ
- มี position modification
- มี baseline fallback
- field presence ไม่ครบ
- parser output ไม่ครบ
- window ใด window หนึ่ง config mismatch

## Interpretation Rules

ห้ามตีความเป็นกำไรหรือความพร้อมเทรด

สิ่งที่อนุญาตให้ตีความ:

- field presence เสถียรหรือไม่
- direction-gap bucket distribution คล้ายหรือต่างจาก CV มากแค่ไหน
- gap reasons ยังเป็นกลุ่มเดิมหรือเกิดกลุ่มใหม่
- จำนวน usable direction เพิ่มพอให้วิเคราะห์ต่อหรือไม่

สิ่งที่ยังห้าม:

- ห้ามสรุปว่า strategy ทำกำไรได้
- ห้ามอนุมัติ order logic
- ห้ามเพิ่ม filter เพื่อ optimize
- ห้ามปรับ parameter
- ห้ามเริ่ม demo/live

## Approval Phrase สำหรับ Checkpoint ถัดไป

หากต้องการรันจริง ต้องใช้ approval phrase แยก:

`Approved to execute Checkpoint CY multi-window CT field-presence diagnostic with symbol GOLD# timeframe H1 windows 2026-03-08 to 2026-03-15, 2026-03-15 to 2026-03-22, and 2026-03-22 to 2026-03-29 using official AK runner/parser workflow.`

## Recommendation

หลัง CX ถูก review/merge แล้ว checkpoint ถัดไปควรเป็น Checkpoint CY execution เฉพาะเมื่อผู้ใช้ approve ด้วย phrase ข้างต้นเท่านั้น

PAF ยังต้องคงสถานะ:

`NOT_READY_FOR_ORDER_LOGIC`
