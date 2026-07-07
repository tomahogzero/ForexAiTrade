# Checkpoint AK: PAF Diagnostic Runner / Parser Integration

วันที่จัดทำ: 2026-07-07

## สถานะ

Checkpoint AK เป็นงาน integration ฝั่ง runner/parser เท่านั้น

ไม่ได้รัน MT5, ไม่ได้รัน Strategy Tester, ไม่ได้แก้ EA/source code, ไม่ได้แก้ presets, ไม่ได้ optimize, ไม่ได้เพิ่ม lot/risk, ไม่ได้เปิด order และไม่ได้ claim profitability

## เหตุผล

Checkpoint AI พิสูจน์แล้วว่า Gold no-trade diagnostic สามารถสร้าง `mt5_report.htm` ได้จริงเมื่อใช้ runner-hardened relative report path

Checkpoint AJ ตรวจ artifact แล้วพบว่า:

- MT5 report ยืนยัน `Total Trades=0` และ `Total Deals=0`
- ไม่มี forbidden order/pending/modify markers
- ไม่มี baseline fallback markers
- `ea_mirror.log` มี Price Action/Fibo diagnostic count ที่เชื่อถือได้ `418`
- `status.json` เดิมมี combined count `601` เพราะรวม `tester_log_excerpt.log` ซึ่งมี duplicate บางส่วน

ดังนั้น Checkpoint AK แก้ปัญหาที่ workflow ยังไม่ reusable:

1. Runner ต้องสร้าง PAF diagnostic config ได้จาก matrix/case metadata อย่างเป็นทางการ
2. Parser ต้องยึด `ea_mirror.log` เป็น authoritative source
3. Tester excerpt ต้องนับแยก ไม่รวมซ้ำใน main diagnostic totals

## ไฟล์ที่เพิ่ม/แก้

- `scripts/run_mt5_research_batch.ps1`
- `tools/paf_diagnostic_parser.py`
- `research/paf_diagnostic_matrix_template.json`
- `docs/50_Checkpoint_AK_PAF_Diagnostic_Runner_Parser_Integration_TH.md`
- `docs/ai/tasks/checkpoint-ak-paf-diagnostic-runner-parser-integration.md`
- `docs/ai/current-status.md`

## Runner Integration

`scripts/run_mt5_research_batch.ps1` รองรับ case metadata ใหม่:

- `enable_price_action_fibo`
- `price_action_fibo_diagnostics_only`
- `paf_use_pending_orders`
- `paf_max_pending_orders`
- `paf_log_only_on_new_bar`
- `paf_entry_timeframe`
- `paf_higher_timeframe`
- `manage_existing_positions`
- `diagnostic_only`

เมื่อ case เปิด `enable_price_action_fibo=true` และ `price_action_fibo_diagnostics_only=true` runner จะ:

- เขียน effective config สำหรับ PAF diagnostic-only
- บังคับใช้ Strategy Tester gate ผ่าน `InpRequireStrategyTester=true`
- ไม่เปิด pending orders เมื่อ `paf_use_pending_orders=false`
- ไม่จัดการ position เมื่อ `manage_existing_positions=false`
- สร้าง `paf_diagnostics.json`
- สร้าง `paf_diagnostics_summary.md`
- สร้าง aggregate summary เฉพาะ selected run

## Parser Integration

เพิ่ม `tools/paf_diagnostic_parser.py`

หลักการนับ:

- ใช้ `ea_mirror.log` เป็น authoritative source เมื่อมีไฟล์
- ใช้ `tester_log_excerpt.log` เป็นหลักฐานประกอบเท่านั้น
- ไม่รวม duplicate จาก tester excerpt เข้า main totals
- แยก output เป็น:
  - `paf_diagnostics.json`
  - `paf_diagnostics_summary.md`
  - `research/results/paf_diagnostics_all_cases.csv`
  - `research/results/paf_diagnostics_summary.md`

ข้อมูลที่ parser สรุป:

- diagnostic count
- no-trade count
- classification distribution
- regime distribution
- no-trade reason distribution
- spread statistics
- forbidden action marker count
- baseline fallback marker count
- no-trade confirmation
- baseline fallback confirmation

## Parser Validation จาก Artifact เดิม

ทดสอบ parser กับ artifact เดิมของ Checkpoint AI โดยไม่รัน MT5 ใหม่:

```text
RunId: run_20260707_020500_checkpoint_ai_gold_no_trade_retry
Case: GOLD_HASH_H1_PAF_DIAG_RETRY_20260601_20260701
Authoritative source: ea_mirror.log
Diagnostic count: 418
No-trade count: 502
Total trades from MT5 report: 0
Forbidden action marker count: 0
Baseline fallback marker count: 0
No-trade confirmation: PASS_FROM_REPORT_AND_EA_LOGS
Baseline fallback confirmation: PASS_FROM_EA_LOGS
```

ผลนี้ยืนยันว่า parser ใหม่ไม่นับ duplicate จาก `tester_log_excerpt.log` เข้ากับ main totals

## Matrix Template

เพิ่ม `research/paf_diagnostic_matrix_template.json` เป็นแม่แบบเท่านั้น

ไฟล์นี้ยังไม่ใช่ approval ให้รัน MT5 และยังต้องใส่ date range ที่ได้รับอนุมัติก่อนใช้งานจริง

ค่า safety ที่แม่แบบกำหนด:

- `enable_price_action_fibo=true`
- `price_action_fibo_diagnostics_only=true`
- `paf_use_pending_orders=false`
- `paf_max_pending_orders=0`
- `paf_log_only_on_new_bar=true`
- `manage_existing_positions=false`
- `enable_exit_telemetry=false`
- `log_position_modify_events=false`

## สิ่งที่ยังไม่ได้ทำ

- ยังไม่ได้รัน MT5 เพิ่ม
- ยังไม่ได้พิสูจน์ผล diagnostic run ใหม่ด้วย runner integration นี้
- ยังไม่ได้แปลง diagnostic classification เป็น entry signal
- ยังไม่ได้อนุมัติ pending order
- ยังไม่ได้อนุมัติ market order
- ยังไม่ได้อนุมัติ demo/live forward test

## Guardrails

Checkpoint AK ยืนยัน:

- ไม่มีการแก้ strategy entry/exit logic
- ไม่มีการเปิด live trading default
- ไม่มี martingale
- ไม่มี uncontrolled grid
- ไม่มี recovery lot multiplication
- ไม่มีการเพิ่ม lot/risk
- ไม่มี optimization
- ไม่มี profitability claim

## ขั้นต่อไปที่ปลอดภัย

Checkpoint AL ควรเป็น approval package หรือ self-review สำหรับการใช้ runner/parser integration นี้กับ one-run diagnostic เท่านั้น

ก่อนรัน MT5 อีกครั้งต้องมี approval ชัดเจนเรื่อง:

- symbol
- timeframe
- date range ไม่เกินขอบเขตที่อนุมัติ
- Strategy Tester only
- no optimization
- no market orders
- no pending orders
- no position modification
- artifact paths
