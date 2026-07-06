# Checkpoint AH: One-Run Retry Approval Package หลัง Report Runner Hardening

วันที่จัดทำ: 2026-07-07

## สถานะ

Checkpoint AH เป็นเอกสารอนุมัติล่วงหน้าเท่านั้น

ยังไม่ได้รัน MT5, ยังไม่ได้รัน Strategy Tester, ยังไม่ได้ spawn `terminal64.exe`, ยังไม่ได้เปลี่ยน EA/source code, ยังไม่ได้เปลี่ยน presets, ยังไม่ได้ optimize, ยังไม่ได้เพิ่ม lot/risk และยังไม่ได้ claim profitability

## เป้าหมาย

หลัง Checkpoint AG merge แล้ว runner ถูกปรับให้ใช้ report path แบบ relative ใต้ MT5 Data Folder และ copy report artifacts กลับเข้า case folder ได้ดีขึ้น

Checkpoint AH จึงกำหนดกรอบสำหรับ retry หนึ่งครั้งในอนาคต เพื่อทดสอบว่า runner ที่แก้แล้วสามารถผลิตและเก็บ MT5 report artifact ได้ครบหรือไม่

เป้าหมายของ retry คือ artifact/diagnostic เท่านั้น ไม่ใช่การหากำไร

## Execution Target ที่เสนอ

- Approved runner/source baseline: `f0d8a6b`
- Commit: `Merge pull request #25 from tomahogzero/research/checkpoint-ag-mt5-report-runner-hardening`
- ถ้าจะใช้ commit ใหม่กว่า `f0d8a6b` ต้องพิสูจน์ก่อนว่าไม่มีการเปลี่ยน:
  - `MQL5/`
  - `presets/`
  - execution runner ที่เกี่ยวกับ MT5
- ถ้ามี EA/source, preset, หรือ runner behavior เปลี่ยน ต้องหยุดและสร้าง checkpoint review ใหม่

## Narrow Future Retry Scope

retry ในอนาคตต้องแคบเท่านี้เท่านั้น:

- Symbol: `GOLD#`
- Timeframe: H1
- Date range: `2026-06-01` ถึง `2026-07-01`
- Strategy Tester only
- One run only
- No optimization
- No demo/live/forward test
- No market orders
- No pending orders
- No position modification
- No lot/risk increase
- No profitability interpretation

ช่วงเวลานี้เป็นช่วงเดียวกับ Checkpoint AC เพื่อเทียบ artifact behavior หลัง runner hardening ไม่ใช่เพื่อเลือก parameter

## Verified User Evidence

หลักฐานที่ผู้ใช้ให้ไว้ก่อนหน้า:

- MT5 Data Folder: `C:\Users\tomah\AppData\Roaming\MetaQuotes\Terminal\BB16F565FAAA6B23A20C26C49416FF05`
- Terminal folder: `C:\Program Files\XM Global MT5`
- Terminal executable expected: `C:\Program Files\XM Global MT5\terminal64.exe`
- Gold symbol: `GOLD#`
- Gold H1 history: yes
- Artifact root: `G:\AiServer\Codex\ForexAiTrade\mt5_artifacts`
- Other MT5 running: must be rechecked immediately before retry

## Required Report Path Mode

retry ต้องใช้ report request แบบ relative ใต้ MT5 Data Folder:

```ini
Report=ForexAiTradeResearch\<RunId>\<CaseId>\mt5_report
ReplaceReport=1
ShutdownTerminal=1
```

ห้ามใช้ absolute path แบบ:

```ini
Report=G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\...\mt5_report
```

เพราะ Checkpoint AC ใช้ absolute path แล้วเกิด `PARTIAL_TESTER_PASS_REPORT_MISSING`

## Expected Artifact Locations

ก่อนรันต้อง pre-create:

```text
C:\Users\tomah\AppData\Roaming\MetaQuotes\Terminal\BB16F565FAAA6B23A20C26C49416FF05\ForexAiTradeResearch\<RunId>\<CaseId>\
```

และต้องเขียน marker:

```text
report_preflight_marker.txt
```

หลังรัน runner ต้อง copy กลับมาที่:

```text
G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\<RunId>\<CaseId>\
```

ต้องค้นหาอย่างน้อย:

- `mt5_report`
- `mt5_report.htm`
- `mt5_report.html`
- `mt5_report.xml`
- `mt5_report.png`
- `mt5_report-hst.png`
- `mt5_report-mfemae.png`
- `mt5_report-holding.png`

## Pre-Run Required Assertions

ก่อน retry ต้องยืนยันทั้งหมด:

- `terminal64.exe` ไม่ได้รันอยู่ก่อนเริ่ม หรือถ้ามีต้องหยุดและขอ approval ใหม่
- Terminal executable มีอยู่จริงที่ `C:\Program Files\XM Global MT5\terminal64.exe`
- MT5 Data Folder มีอยู่จริง
- Artifact root เขียนได้
- Terminal report folder สร้างได้
- `report_preflight_marker.txt` เขียนได้
- `Report=` ใน `generated_tester.ini` เป็น relative path ตามที่กำหนด
- `Optimization=0`
- Symbol เป็น `GOLD#`
- Timeframe เป็น H1
- Date range เป็น `2026-06-01` ถึง `2026-07-01`
- `InpEnablePriceActionFibo=true`
- `InpPriceActionFiboDiagnosticsOnly=true`
- `InpPAFUsePendingOrders=false`
- `InpPAFMaxPendingOrders=0`
- `InpManageExistingPositions=false`
- `InpRequireStrategyTester=true`
- `InpPAFLogOnlyOnNewBar=true`
- ไม่มี existing/open position ใน tester context

## Stop Conditions

ต้องหยุดทันทีและไม่รัน ถ้าพบข้อใดข้อหนึ่ง:

- commit/source target ไม่ตรงและยังไม่ได้พิสูจน์ drift guard
- `MQL5/` หรือ `presets/` เปลี่ยนจาก approved target
- runner behavior เปลี่ยนหลัง `f0d8a6b` โดยไม่มี review ใหม่
- `terminal64.exe` ยังรันอยู่ก่อนเริ่มและไม่สามารถควบคุมได้
- terminal path หรือ data folder ไม่ชัดเจน
- report folder หรือ marker เขียนไม่ได้
- `Report=` กลายเป็น absolute artifact path
- optimization enabled
- symbol/timeframe/date range ไม่ตรง approval
- effective config ไม่ใช่ diagnostic-only
- มี market order attempt
- มี pending order attempt
- มี position modification attempt
- มี baseline strategy fallback
- มี demo/live/forward environment

## Required Post-Run Artifacts

ถ้ามี execution checkpoint ในอนาคต ต้องเก็บ:

- RunId
- `generated_tester.ini`
- `effective_config_snapshot.set`
- `process_info.json`
- `runner.log`
- `tester_log_excerpt.log`
- `ea_mirror.log`
- `status.json`
- `post_run_guardrail_summary.md`
- forbidden action grep/check summary
- Price Action/Fibo diagnostic classification summary
- `mt5_report.htm` หรือ report artifact ที่ MT5 สร้างจริง
- report companion graph files ถ้ามี
- confirmation ว่า no market order / no pending order / no position modification
- confirmation ว่า no baseline fallback

## Approval Phrase สำหรับอนาคต

ห้ามรันจนกว่าผู้ใช้จะพิมพ์ approval phrase ใหม่หลัง Checkpoint AH merge:

```text
Approved to execute Checkpoint AI one-run Gold no-trade diagnostic retry with symbol GOLD# timeframe H1 date range 2026-06-01 to 2026-07-01 using runner-hardened relative MT5 report paths.
```

## สิ่งที่ Checkpoint AH ไม่ได้อนุมัติ

- ไม่อนุมัติ live trading
- ไม่อนุมัติ demo forward test
- ไม่อนุมัติ optimization
- ไม่อนุมัติ lot/risk increase
- ไม่อนุมัติการใช้ผลลัพธ์เป็น proof of profitability
- ไม่อนุมัติการแก้ strategy logic

## ผลลัพธ์ที่คาดหวังจาก retry ในอนาคต

ผลที่ต้องการคือคำตอบด้าน infrastructure:

1. Runner หลัง Checkpoint AG สามารถสร้างและ copy `mt5_report.htm` ได้หรือไม่
2. ถ้า report ยังหาย สถานะใหม่แยกปัญหาได้ชัดเจนกว่าเดิมหรือไม่
3. no-trade diagnostic path ยังปลอดภัยตาม guardrails หรือไม่

ไม่ควรตีความ profit, drawdown หรือ equity curve เป็นสัญญาณว่าระบบพร้อมเทรด

