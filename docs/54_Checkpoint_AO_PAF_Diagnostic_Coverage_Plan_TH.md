# Checkpoint AO: PAF Diagnostic Coverage Plan

วันที่จัดทำ: 2026-07-07

## สถานะ

Checkpoint AO เป็น planning / approval-preparation เท่านั้น

ไม่ได้รัน MT5, ไม่ได้รัน Strategy Tester, ไม่ได้ spawn `terminal64.exe`, ไม่ได้แก้ EA/source code, ไม่ได้แก้ presets, ไม่ได้ optimize, ไม่ได้เพิ่ม lot/risk, ไม่ได้เปิด market order, ไม่ได้เปิด pending order และไม่ได้ claim profitability

## เหตุผล

Checkpoint AM และ AN พิสูจน์แล้วว่า:

- official AK runner/parser workflow ใช้งานได้
- Gold PAF diagnostic-only run สร้าง MT5 report ได้
- `Total trades=0`
- forbidden order markers = `0`
- baseline fallback markers = `0`
- `ea_mirror.log` เป็น authoritative source ได้

แต่ข้อมูลยังมีแค่หนึ่ง diagnostic window:

```text
GOLD# H1
2026-06-01 ถึง 2026-07-01
```

ข้อมูลหนึ่งเดือนยังไม่พอสำหรับตัดสินใจ implement market entry หรือ pending order เพราะอาจเจอเฉพาะสภาวะตลาดบางแบบ เช่น trend/breakout บางช่วง หรือ spread abnormal บางชั่วโมง

## Current Evidence

จาก Checkpoint AM:

- PAF diagnostic count: `417`
- No-trade count: `502`
- `NO_SETUP`: `304`
- `POSSIBLE_FIBO_PULLBACK`: `57`
- `POSSIBLE_ZONE_REJECTION`: `41`
- `POSSIBLE_BREAK_RETEST`: `15`
- trend regime: `327`
- breakout regime: `90`
- Total trades: `0`
- Forbidden markers: `0`
- Baseline fallback markers: `0`

## Coverage Gap

ช่องว่างหลักตอนนี้:

1. มีเพียงหนึ่งเดือนของ `GOLD#` H1
2. ยังไม่มี diagnostic coverage ในเดือนที่ตลาด sideway/volatile ต่างจากเดือน June 2026
3. ยังไม่รู้ว่า PAF classifications กระจุกตัวใน session ไหน
4. ยังไม่รู้ว่า spread spikes กระทบ diagnostic setup มากแค่ไหนในช่วงอื่น
5. ยังไม่รู้ว่า `POSSIBLE_FIBO_PULLBACK`, `POSSIBLE_ZONE_REJECTION`, และ `POSSIBLE_BREAK_RETEST` มี persistence หรือเป็น noise
6. ยังไม่มี multi-window comparison ก่อนคิดเรื่อง entry/SL/TP/pending order

## Proposed No-Trade Diagnostic Windows

ถ้าต้องเก็บข้อมูลเพิ่มใน Checkpoint AP ควรเป็น no-trade diagnostics เท่านั้น และควรแยก run เป็นหน้าต่างสั้น ๆ ไม่เกิน 1 เดือนต่อ run

ชุดที่เสนอ:

| Window | Symbol | Timeframe | Purpose | Run Type |
|---|---|---|---|---|
| AP-W1 | `GOLD#` | H1 | Repeat recent style window for stability check | no-trade diagnostic |
| AP-W2 | `GOLD#` | H1 | Different month to compare regime/classification distribution | no-trade diagnostic |
| AP-W3 | `GOLD#` | H1 | Stress window with visible volatility/spread behavior if user identifies one | no-trade diagnostic |

วันที่ยังไม่ควรกำหนดเองโดย Codex ต้องให้ผู้ใช้ approve เป็น concrete dates ก่อนรันจริง

## Required Config for Any Future Diagnostic Window

ทุก window ต้องยืนยัน:

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

`InpLiveTradingEnabled=true` ใช้เฉพาะใน Strategy Tester เพื่อผ่าน internal tester gate เท่านั้น ไม่ใช่ approval สำหรับ demo/live chart

## Stop Conditions for Future Runs

ต้องหยุดทันทีถ้าพบ:

- config mismatch
- date range เกิน 1 เดือนต่อ window
- optimization enabled
- market order attempt
- pending order attempt
- position modification attempt
- baseline fallback
- no report artifact
- no `ea_mirror.log`
- stale artifact reuse
- unrelated `terminal64.exe` process ที่ควบคุมไม่ได้

## Required Outputs for Future Runs

สำหรับแต่ละ window ต้องมี:

- RunId
- `generated_tester.ini`
- `effective_config_snapshot.set`
- `process_info.json`
- `runner.log`
- `mt5_report.htm`
- `ea_mirror.log`
- `tester_log_excerpt.log`
- `paf_diagnostics.json`
- `paf_diagnostics_summary.md`
- forbidden action grep summary
- no-trade confirmation
- baseline fallback confirmation

หลังจบหลาย windows ต้องมี aggregate:

- classification distribution by window
- regime distribution by window
- no-trade reason distribution by window
- spread stats by window
- setup density by month/window
- recommendation whether PAF is worth implementation-spec work

## Decision Gate Before Implementation

ยังไม่ควร implement entry/pending order จนกว่าจะมีอย่างน้อย:

- 3 no-trade diagnostic windows
- ทุก window มี `Total trades=0`
- forbidden markers = `0`
- baseline fallback markers = `0`
- PAF setup classifications ไม่ได้เกิดจาก spread spike อย่างเดียว
- มี distribution ของ classifications ที่ไม่กระจุกแค่หนึ่งช่วงเวลา
- มีแผน risk model สำหรับ Gold ที่ไม่ force broker min lot

## What Not To Do Yet

ยังไม่ควร:

- เปิด market order
- เปิด pending order
- เพิ่ม Fibo/Grid/Pending strategy จริง
- optimize parameter
- เพิ่ม lot/risk
- claim 2-5% ต่อเดือน
- เริ่ม demo/live forward test

## Recommended Next Checkpoint

Checkpoint AP ควรเป็น approval package สำหรับ multi-window no-trade diagnostic เท่านั้น

ตัวอย่าง approval phrase ในอนาคต:

```text
Approved to execute Checkpoint AP multi-window PAF no-trade diagnostics for GOLD# H1 with windows YYYY-MM-DD to YYYY-MM-DD, YYYY-MM-DD to YYYY-MM-DD, and YYYY-MM-DD to YYYY-MM-DD using official AK runner/parser workflow.
```

แต่ละ window ต้องไม่เกิน 1 เดือน และยังต้องเป็น no-trade diagnostic เท่านั้น

## Progress ประเมินล่าสุด

หลัง Checkpoint AO:

- EA / safety / risk guardrails: `90%`
- MT5 runner + artifact pipeline: `85%`
- PAF no-trade diagnostic workflow: `65%`
- Gold-specific diagnostic evidence: `40%`
- PAF implementation readiness: `25%`
- Demo/live readiness: `0%`
- Profitability proof: `0%`

ภาพรวมถ้าวัดถึง “ระบบวิจัยที่พร้อมทดลอง strategy อย่างควบคุมได้”: ประมาณ `47%`

ถ้าวัดถึง “บอทพร้อมเงินจริง”: ยังประมาณ `10-15%`

เหตุผลที่ progress เพิ่มไม่มาก: AO เป็นแผน coverage ไม่ใช่ข้อมูล backtest/diagnostic ใหม่ และยังไม่อนุมัติการเปิด order

