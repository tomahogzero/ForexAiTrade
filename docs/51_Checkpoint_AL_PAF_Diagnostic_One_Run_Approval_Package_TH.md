# Checkpoint AL: PAF Diagnostic One-Run Approval Package

วันที่จัดทำ: 2026-07-07

## สถานะ

Checkpoint AL เป็น approval package / planning-only เท่านั้น

ไม่ได้รัน MT5, ไม่ได้รัน Strategy Tester, ไม่ได้ spawn `terminal64.exe`, ไม่ได้แก้ EA/source code, ไม่ได้แก้ presets, ไม่ได้ optimize, ไม่ได้เพิ่ม lot/risk, ไม่ได้เปิด order และไม่ได้ claim profitability

## พื้นฐานจาก Checkpoint AK

Checkpoint AK เพิ่ม official runner/parser support สำหรับ Price Action/Fibo diagnostic-only workflow แล้ว:

- runner รองรับ PAF diagnostic case metadata
- parser ใช้ `ea_mirror.log` เป็น authoritative diagnostic source
- `tester_log_excerpt.log` ถูกนับแยกเพื่อกัน duplicate count
- artifact เดิมของ Checkpoint AI parse ได้ `418` diagnostics ไม่ใช่ combined duplicate `601`

Checkpoint AL จึงเตรียม approval สำหรับการรัน diagnostic รอบถัดไปด้วย workflow ใหม่นี้ แต่ยังไม่อนุมัติการรันจริง

## Proposed Future Execution Target

เป้าหมาย source/preset สำหรับ future execution:

```text
Source branch: main
Source commit: 621463d056d559a5c4cdc05a6175d70bb0a73430
Basis: PR #29 / Checkpoint AK merged
```

ถ้า commit ใหม่กว่านี้ถูกใช้ก่อนรันจริง ต้องตรวจและบันทึกว่า:

- EA/source code ไม่เปลี่ยนจาก target commit
- presets ไม่เปลี่ยนจาก target commit
- runner/parser changes ใหม่ไม่เปลี่ยน safety assumptions

ถ้า EA/source code หรือ presets เปลี่ยน ต้อง block execution และต้องมี checkpoint review ใหม่ก่อนรัน

## Proposed Future Diagnostic Scope

ขอบเขตที่เสนอสำหรับ checkpoint ถัดไป:

- Symbol: `GOLD#` เท่านั้น
- Timeframe: `H1` เท่านั้น
- Date range: `NEED_USER_APPROVAL`
- Maximum date range: 1 month
- Strategy Tester only
- One run only
- No optimization
- No demo/live/forward test
- No market orders
- No pending orders
- No position modification
- No lot/risk increase
- No profitability interpretation

## Required User Approval Phrase

ก่อนรันจริง ผู้ใช้ต้องพิมพ์ approval phrase แบบมีวันที่ชัดเจน:

```text
Approved to execute Checkpoint AM one-run PAF diagnostic with symbol GOLD# timeframe H1 date range YYYY-MM-DD to YYYY-MM-DD using official AK runner/parser workflow.
```

ถ้า date range เกิน 1 เดือน ให้ block execution และต้องทำ approval checkpoint ใหม่

## Required Pre-Run Environment Evidence

ก่อนรันจริงต้องตรวจและบันทึก:

- `terminal64.exe` path:
  - `C:\Program Files\XM Global MT5\terminal64.exe`
- MT5 Data Folder:
  - `C:\Users\tomah\AppData\Roaming\MetaQuotes\Terminal\BB16F565FAAA6B23A20C26C49416FF05`
- Report/artifact root:
  - `G:\AiServer\Codex\ForexAiTrade\mt5_artifacts`
- No unrelated `terminal64.exe` process running before execution
- Report folder writable
- Preflight marker can be written
- Strategy Tester history exists for `GOLD#` H1 in the approved date range
- Optimization disabled
- Dedicated spawned MT5 PID captured
- Runner may stop only the spawned PID

## Required Effective Config Assertions

ก่อนรันจริงต้องยืนยันจาก generated/effective config:

- `InpLiveTradingEnabled=true`
- `InpDemoSafeMode=true`
- `InpRequireStrategyTester=true`
- `InpEnablePriceActionFibo=true`
- `InpPriceActionFiboDiagnosticsOnly=true`
- `InpPAFUsePendingOrders=false`
- `InpPAFMaxPendingOrders=0`
- `InpPAFLogOnlyOnNewBar=true`
- `InpManageExistingPositions=false`
- `InpMirrorLogsToFile=true`
- `InpMirrorLogsUseCommonFolder=true`
- `InpAllowedSymbolsCsv=GOLD#`
- `InpCanonicalSymbolName=GOLD`
- `InpBrokerGoldSymbolName=GOLD#`

หมายเหตุ: `InpLiveTradingEnabled=true` อนุญาตเฉพาะใน Strategy Tester เพื่อผ่าน internal tester gate เท่านั้น ไม่ใช่ approval สำหรับ demo/live chart

## Stop Conditions

ต้องหยุดทันทีถ้าพบ:

- config mismatch
- date range เกิน 1 เดือน
- terminal path ไม่ชัดเจน
- MT5 data folder ไม่ชัดเจน
- report folder เขียนไม่ได้
- มี unrelated `terminal64.exe` running และควบคุมไม่ได้
- optimization enabled
- demo/live/forward environment detected
- any market order attempt
- any pending order attempt
- any position modification attempt
- baseline strategy fallback
- log noisy เพราะ `InpPAFLogOnlyOnNewBar` ไม่ทำงาน
- stale artifacts ถูกใช้เป็นหลักฐานแทน fresh artifacts

## Required Artifacts After Future Run

ถ้ามีการอนุมัติและรันใน checkpoint ถัดไป ต้องเก็บ:

- RunId
- `generated_tester.ini`
- effective config snapshot
- `process_info.json`
- `runner.log`
- Strategy Tester report path
- `mt5_report.htm`
- MT5 report companion images ถ้ามี
- `ea_mirror.log`
- `tester_log_excerpt.log`
- `paf_diagnostics.json`
- `paf_diagnostics_summary.md`
- aggregate `research/results/paf_diagnostics_all_cases.csv`
- aggregate `research/results/paf_diagnostics_summary.md`
- forbidden action grep/check summary
- no-trade confirmation
- no baseline fallback confirmation

## Forbidden Interpretation

ผล diagnostic รอบถัดไปห้ามตีความเป็น:

- proof of profitability
- signal approval
- pending order approval
- market order approval
- demo/live readiness
- เหตุผลให้เพิ่ม lot/risk

Diagnostic classifications เป็น observation labels เท่านั้น ไม่ใช่ entry signals

## Guardrails Confirmed

Checkpoint AL ยืนยัน:

- ไม่มีการรัน MT5
- ไม่มีการรัน Strategy Tester
- ไม่มีการแก้ EA/source code
- ไม่มีการแก้ presets
- ไม่มี optimization
- ไม่มีการเพิ่ม lot/risk
- ไม่มี martingale
- ไม่มี uncontrolled grid
- ไม่มี recovery lot multiplication
- ไม่มี profitability claim

## Next Safe Step

Checkpoint AM เท่านั้นที่อาจเป็น execution checkpoint ได้ และต้องเริ่มได้เฉพาะเมื่อผู้ใช้ให้ approval phrase พร้อม date range ที่ไม่เกิน 1 เดือน
