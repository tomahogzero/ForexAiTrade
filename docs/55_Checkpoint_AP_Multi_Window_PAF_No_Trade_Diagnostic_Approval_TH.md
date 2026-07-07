# Checkpoint AP: Multi-Window PAF No-Trade Diagnostic Approval

วันที่จัดทำ: 2026-07-07

## สถานะ

Checkpoint AP เป็นเอกสาร approval package เท่านั้น

ไม่ได้รัน MT5, ไม่ได้รัน Strategy Tester, ไม่ได้ spawn `terminal64.exe`, ไม่ได้แก้ EA/source code, ไม่ได้แก้ presets, ไม่ได้ optimize, ไม่ได้เพิ่ม lot/risk, ไม่ได้เปิด market order, ไม่ได้เปิด pending order, ไม่ได้ modify position และไม่ได้ claim profitability

## เป้าหมาย

เตรียมกรอบอนุมัติสำหรับ Checkpoint AQ ในอนาคต เพื่อเก็บข้อมูล Price Action / Fibo diagnostics แบบ no-trade หลายช่วงเวลา ก่อนคิดเรื่อง implement entry หรือ pending order จริง

Checkpoint AM พิสูจน์แล้วว่า workflow official AK runner/parser สามารถสร้าง artifact ได้สำหรับ `GOLD#` H1 หนึ่งเดือน แต่ข้อมูลหนึ่งเดือนยังไม่พอสำหรับตัดสินใจว่า PAF logic ควรถูกพัฒนาเป็น strategy จริงหรือไม่

## ขอบเขตของ Future Checkpoint AQ

Future Checkpoint AQ ถ้าได้รับอนุมัติ ต้องเป็น:

- Symbol: `GOLD#` เท่านั้น
- Timeframe: `H1` เท่านั้น
- Strategy Tester เท่านั้น
- Run แบบ diagnostic-only เท่านั้น
- ไม่เกิน 3 windows
- แต่ละ window ต้องไม่เกิน 1 เดือน
- ไม่ optimization
- ไม่ demo/live/forward test
- ไม่ market orders
- ไม่ pending orders
- ไม่ position modification
- ไม่ lot/risk increase
- ไม่ profitability interpretation

## Date Windows

Checkpoint AP ยังไม่กำหนดวันที่เอง ต้องรอผู้ใช้อนุมัติวันที่จริง

| Window | Symbol | Timeframe | Date Range | Purpose |
|---|---|---|---|---|
| AQ-W1 | `GOLD#` | H1 | `NEED_USER_APPROVAL_1_FROM` to `NEED_USER_APPROVAL_1_TO` | ตรวจซ้ำช่วงหนึ่งเดือนที่ต่างจาก AM |
| AQ-W2 | `GOLD#` | H1 | `NEED_USER_APPROVAL_2_FROM` to `NEED_USER_APPROVAL_2_TO` | ตรวจ distribution ของ PAF classifications ในสภาพตลาดอีกแบบ |
| AQ-W3 | `GOLD#` | H1 | `NEED_USER_APPROVAL_3_FROM` to `NEED_USER_APPROVAL_3_TO` | ตรวจช่วงที่ผู้ใช้เห็นว่ามี volatility หรือ spread behavior น่าสนใจ |

ทุก window ต้องเป็น concrete dates ในรูปแบบ `YYYY-MM-DD to YYYY-MM-DD`

ถ้าวันที่ใดก็ตามเกิน 1 เดือน ต้อง block execution และต้องสร้าง approval checkpoint ใหม่

## Required Effective Config Assertions

ก่อนรัน future Checkpoint AQ ต้องยืนยัน effective config ทุก window:

- `InpLiveTradingEnabled=true`
- `InpDemoSafeMode=true`
- `InpRequireStrategyTester=true`
- `InpEnablePriceActionFibo=true`
- `InpPriceActionFiboDiagnosticsOnly=true`
- `InpPAFUsePendingOrders=false`
- `InpPAFMaxPendingOrders=0`
- `InpPAFLogOnlyOnNewBar=true`
- `InpManageExistingPositions=false`
- `InpAllowedSymbolsCsv=GOLD#`
- `InpCanonicalSymbolName=GOLD`
- `InpBrokerGoldSymbolName=GOLD#`
- Optimization disabled
- Strategy Tester only

`InpLiveTradingEnabled=true` ใช้เฉพาะเพื่อผ่าน internal Strategy Tester gate เท่านั้น ไม่ใช่ approval สำหรับ demo/live chart

Diagnostic classifications เป็น observation labels เท่านั้น ไม่ใช่ entry signals

## Stop Conditions

ต้องหยุดทันทีและถือว่า run ไม่ผ่าน หากพบ:

- config mismatch
- date range เกิน 1 เดือนต่อ window
- terminal path ไม่ชัดเจน
- data folder ไม่ชัดเจน
- report folder เขียนไม่ได้
- มี `terminal64.exe` อื่นที่ควบคุมไม่ได้
- `/config` handoff ไม่ชัดเจน
- stale artifacts ถูก reuse เป็นหลักฐาน
- optimization enabled
- demo/live/forward environment detected
- market order attempt
- pending order attempt
- position modification attempt
- baseline strategy fallback
- missing `mt5_report.htm`
- missing `ea_mirror.log`
- missing PAF diagnostics summary

## Required Artifacts Per Window

แต่ละ window ต้องมี artifact อย่างน้อย:

- RunId
- case folder
- `generated_tester.ini`
- effective config snapshot
- `process_info.json`
- `runner.log`
- `status.json`
- `mt5_report.htm`
- MT5 report companion graph files ถ้ามี
- `parsed_result.json`
- `ea_mirror.log`
- `tester_log_excerpt.log`
- `paf_diagnostics.json`
- `paf_diagnostics_summary.md`
- forbidden action grep/check summary
- post-run guardrail summary
- no-trade confirmation
- no baseline fallback confirmation

## Required Aggregate Outputs After Future AQ

หลังครบทุก window ต้องสรุป:

- classification distribution by window
- regime distribution by window
- no-trade reason distribution by window
- spread statistics by window
- setup density by window
- comparison against Checkpoint AM
- whether diagnostics are stable enough for implementation-spec work
- whether spread/regime filters dominate diagnostics too much

## Decision Gate Before Any Strategy Implementation

ยังไม่ควร implement entry/pending order จนกว่าจะมีอย่างน้อย:

- 3 no-trade diagnostic windows
- `Total trades=0` ทุก window
- forbidden markers = `0` ทุก window
- baseline fallback markers = `0` ทุก window
- PAF classifications ไม่กระจุกตัวจาก spread spike อย่างเดียว
- มี distribution พอให้แยก noise กับ setup ที่น่าสนใจ
- Gold risk-budget guardrails ยังไม่ถูก bypass

ถ้าทุก window ผ่าน safety และมี diagnostic distribution ที่อ่านได้ รอบถัดไปควรเป็น implementation specification เท่านั้น ยังไม่ใช่การเปิด order

ถ้า classifications น้อยเกินไป, noisy เกินไป, หรือถูก spread/regime blocks ครอบงำ ควรทำ diagnostics เพิ่มหรือ reject PAF Gold path for now

## Future Approval Phrase

การรันจริงใน Checkpoint AQ ยังถูก block จนกว่าผู้ใช้จะส่งข้อความอนุมัติแบบนี้:

```text
Approved to execute Checkpoint AQ multi-window PAF no-trade diagnostics for GOLD# H1 with windows YYYY-MM-DD to YYYY-MM-DD, YYYY-MM-DD to YYYY-MM-DD, and YYYY-MM-DD to YYYY-MM-DD using official AK runner/parser workflow.
```

ทุกวันที่ต้องเป็นวันที่จริง และแต่ละช่วงต้องไม่เกิน 1 เดือน

## สิ่งที่ยังห้ามทำ

- ห้ามเปิด market order
- ห้ามเปิด pending order
- ห้าม modify position
- ห้ามเพิ่ม Fibo/Grid/Pending strategy จริง
- ห้าม optimize parameters
- ห้ามเพิ่ม lot/risk
- ห้าม claim 2-5% ต่อเดือน
- ห้ามเริ่ม demo/live forward test
- ห้ามใช้ diagnostic labels เป็น entry signals

## Progress ประเมินหลัง Checkpoint AP

- EA / safety / risk guardrails: `90%`
- MT5 runner + artifact pipeline: `85%`
- PAF no-trade diagnostic workflow: `65%`
- Gold-specific diagnostic evidence: `40%`
- PAF implementation readiness: `25%`
- Demo/live readiness: `0%`
- Profitability proof: `0%`

ภาพรวมถ้าวัดถึง "ระบบวิจัยที่พร้อมทดลอง strategy อย่างควบคุมได้": ประมาณ `48%`

ถ้าวัดถึง "บอทพร้อมเงินจริง": ยังประมาณ `10-15%`

เหตุผลที่ progress เพิ่มน้อย: AP เป็น approval package ไม่ใช่ diagnostic data ใหม่ และยังไม่อนุมัติการเปิด order
