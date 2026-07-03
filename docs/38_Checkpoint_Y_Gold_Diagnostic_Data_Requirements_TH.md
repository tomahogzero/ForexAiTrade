# Checkpoint Y: Gold Diagnostic Data Requirements and No-Trade Signal Logging Plan

วันที่จัดทำ: 2026-07-04

## สถานะของ checkpoint นี้

Checkpoint Y เป็นเอกสารวางแผน diagnostic เท่านั้น

Checkpoint นี้ไม่รัน MT5, ไม่รัน Strategy Tester, ไม่แก้ EA/source code, ไม่แก้ presets, ไม่ optimize, ไม่เพิ่ม lot/risk, ไม่ claim profitability และไม่อนุมัติ demo/live trading

## เป้าหมาย

ต่อจาก Checkpoint X ที่วางกรอบวิจัยทอง 2-5% ต่อเดือนแบบ aggressive research target แล้ว Checkpoint Y กำหนดว่า "ต้องเก็บข้อมูลอะไร" ก่อนจะตัดสินใจเพิ่ม logic หรือรันทดสอบทองจริง

เป้าหมายหลัก:

- ทำให้การวิจัยทองไม่กลายเป็นการไล่กำไรย้อนหลัง
- แยก execution proof ออกจาก strategy performance
- แยก Gold profile ออกจาก EURUSD/forex profile
- เตรียม no-trade diagnostic logging ก่อนมี order ใด ๆ
- ลดภาระ manual ของผู้ใช้โดยให้ Codex + GPT review ทำงานร่วมกันได้มากขึ้นภายใต้ guardrails

## Why diagnostics first

ทองวิ่งแรงจริง แต่ความแรงไม่ใช่ edge โดยอัตโนมัติ

ก่อนจะถามว่า "ทำกำไร 2-5% ต่อเดือนได้ไหม" ต้องตอบคำถามเหล่านี้ก่อน:

- สัญญาณเกิดช่วง session ไหน
- signal ถูก reject เพราะ spread, risk budget, stops level, หรือ regime unsafe มากแค่ไหน
- false breakout เกิดบ่อยแค่ไหน
- trend continuation หรือ mean reversion เหมาะกับช่วงไหน
- stop loss ถูกชนเพราะ entry แย่, stop แคบเกิน, spread/slippage, หรือข่าว
- broker minimum lot ทำให้ risk budget ใช้งานไม่ได้หรือไม่
- drawdown กระจุกในข่าวแรงหรือ session ใด session หนึ่งหรือไม่

## Required Gold symbol diagnostics

ทุก future Gold diagnostic run ต้องเก็บ:

- actual broker symbol เช่น `GOLD#` หรือ `GOLDm#`
- canonical symbol เช่น `GOLD`
- timeframe
- signal timeframe
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
- spread at init
- spread at signal
- broker server time
- account currency
- deposit assumption

ถ้าข้อมูล symbol metadata ขาดหรือผิด ต้องจัดเป็น `EXECUTION_BLOCKED_SYMBOL_METADATA_INVALID`

## Required no-trade signal diagnostics

ก่อนเปิด market order หรือ pending order ใด ๆ Gold strategy path ต้องสามารถ log diagnostic-only signal ได้:

- bar time
- actual symbol
- canonical symbol
- timeframe
- session bucket
- market regime
- strategy family candidate
- classification label
- no-trade reason
- signal direction candidate ถ้ามี แต่ต้องไม่ส่งเป็น `SIGNAL_BUY` / `SIGNAL_SELL`
- entry reference price
- invalidation level
- hypothetical SL distance
- hypothetical TP distance
- hypothetical R multiple
- ATR value
- ADX value
- EMA slope
- Bollinger width
- spread points
- allowed/not allowed by risk gates
- reject reason

Diagnostic classification เป็น observation label เท่านั้น ไม่ใช่ entry signal

## Required risk-budget diagnostics

Gold ต้องมี risk-budget diagnostics ก่อนทุก research run:

- configured risk percent
- risk money
- hypothetical SL distance
- raw lot
- normalized lot
- broker minimum lot
- actual risk if min lot is used
- whether min lot violates risk budget
- estimated minimum deposit needed for min lot without violating risk
- margin estimate if available
- decision:
  - `RISK_BUDGET_OK`
  - `LOT_BELOW_MINIMUM`
  - `MIN_LOT_WOULD_VIOLATE_RISK`
  - `MARGIN_INSUFFICIENT`
  - `SYMBOL_METADATA_INVALID`

ห้าม force minimum lot ถ้าทำให้ risk เกิน config

## Required session diagnostics

Gold diagnostic ต้องแยกอย่างน้อย:

- Asia
- London
- New York
- London/New York overlap
- Other / Unknown

ต้องเก็บ:

- signal count by session
- rejected signal count by session
- spread average/max by session
- unsafe regime count by session
- hypothetical R distribution by session
- event-window overlap by session

## Required regime diagnostics

ต้องเก็บ:

- trend
- breakout
- sideway
- mixed
- unsafe

และเหตุผลของ regime:

- ADX
- ATR volatility
- EMA slope
- Bollinger Band width
- spread filter
- missing/invalid indicators

## Required event / macro diagnostics

Checkpoint Y ยังไม่ต้อง integrate economic calendar แต่ future plan ต้องรองรับ event tags:

- CPI
- NFP
- FOMC
- rate decision
- central bank speech
- high-impact USD news
- abnormal spread window
- market open/rollover

ถ้าไม่มี calendar data ให้ log `EVENT_CONTEXT_UNKNOWN` แทนการเดา

## Required execution artifact diagnostics

ก่อนรัน MT5 ต้องมี Checkpoint W-style verified artifact path:

- exact source branch and commit
- exact terminal64.exe path
- exact data folder
- exact tester config path
- exact effective config path
- absolute report path
- writable report folder marker
- terminal log folder
- tester log folder
- EA/mirror log folder
- stale artifact guard

ถ้า artifact path ไม่ชัด ห้ามรัน

## Forbidden actions for Gold diagnostic phase

ห้าม:

- market orders
- pending orders
- position modification
- fallback to baseline strategy without explicit diagnostic label
- MT5 optimization
- demo/live forward test
- lot/risk increase
- martingale
- uncontrolled grid
- recovery lot multiplication
- no-stop-loss zone holding
- forced broker minimum lot

## Pass / fail criteria for future no-trade Gold diagnostic run

Future diagnostic run จะผ่านเฉพาะเมื่อ:

- Strategy Tester report/log ถูกสร้างจริง
- EA/mirror diagnostic log ถูกสร้างจริง
- symbol metadata ถูก log ครบ
- diagnostic classifications มีอยู่
- no-trade reasons มีอยู่
- ไม่มี market order
- ไม่มี pending order
- ไม่มี position modification
- ไม่มี `SIGNAL_BUY` / `SIGNAL_SELL` จาก Gold diagnostic path
- ไม่มี baseline fallback ที่ไม่ถูก label
- artifact timestamps ตรงกับ RunId

ถ้าขาด artifact ต้องเป็น `FAILED_NO_TESTER_ARTIFACTS / INCONCLUSIVE`

## Autonomy and merge policy proposal

เพื่อลดภาระผู้ใช้ใน GitHub workflow สามารถใช้กติกานี้ในอนาคตได้ ถ้าผู้ใช้อนุมัติเป็น standing instruction:

Codex อาจ merge PR เองได้เฉพาะเมื่อครบทุกข้อ:

- PR เป็น docs-only หรือ research-plan-only
- ไม่มี MQL5/source code changes
- ไม่มี preset changes
- ไม่มี scripts ที่รัน MT5 หรือเปลี่ยน execution behavior
- ไม่มี MT5 run
- ไม่มี optimization
- ไม่มี lot/risk increase
- GPT review ผ่าน `PASS`
- artifact audit ผ่าน
- PR เป็น draft/open และไม่มี merge conflict

Codex ต้องไม่ auto-merge ถ้า:

- มี MQL5 changes
- มี presets changes
- มี Python/shell runner changes ที่อาจกระทบ execution
- มี MT5/Strategy Tester run
- มีผล backtest/performance ใหม่
- มีการอนุมัติ execution หรือ live/demo
- GPT เป็น `NEEDS_FIX` หรือ `CONDITIONAL_PASS`

ถ้าไม่ได้รับ standing instruction ชัดเจน ให้ Codex เปิด PR + GPT review แล้วหยุดรอผู้ใช้ merge

## Recommended next checkpoint

ถ้า Checkpoint Y ผ่าน GPT review:

Checkpoint Z ควรเป็น `Gold No-Trade Diagnostic Execution Approval Pack`

Checkpoint Z ยังไม่ควรรัน MT5 แต่จะล็อก:

- symbol: `GOLD#` หรือ `GOLDm#` ตาม Market Watch จริง
- timeframe
- date range ไม่เกิน 1 เดือน
- exact terminal/data/report/log paths
- effective config assertions
- stop conditions
- artifact requirements

MT5 run จริงควรเกิดใน checkpoint หลังจากนั้นเท่านั้น และต้องเป็น one-run diagnostic เท่านั้น

