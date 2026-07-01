# Checkpoint S: เอกสารขออนุมัติการรัน Diagnostic แบบห้ามเทรด 1 ครั้ง

วันที่สร้าง: 2026-07-02

## เป้าหมาย

Checkpoint S เป็นเอกสารขออนุมัติสำหรับการรัน Strategy Tester แบบ diagnostic-only จำนวน 1 ครั้งในอนาคต

Checkpoint นี้ยังไม่รัน MT5, ยังไม่รัน Strategy Tester, ไม่แก้ EA/source code, ไม่แก้ preset, ไม่ optimize, ไม่เพิ่ม lot/risk และไม่อนุมัติ demo/live trading

## สถานะปัจจุบัน

- PR #8 / Checkpoint R merge แล้ว
- GPT Review Agent สำหรับ PR #8 ให้ผล PASS
- Checkpoint R วางกรอบ approval pack แล้ว
- การรันจริงยังถูก block จนกว่าจะมีคำอนุมัติแยกอย่างชัดเจนหลัง review Checkpoint S

## Branch / Commit ที่เสนอสำหรับการรันในอนาคต

ถ้ามีการอนุมัติแยกในอนาคต ให้ใช้ EA source จาก:

- Branch: `main`
- Commit: `cd1b5118e4c443d240f63553abcabce18f2a0982`
- ความหมาย: merge commit ของ PR #8 / Checkpoint R

ถ้า Checkpoint S ถูก merge ก่อนการรัน ต้องตรวจซ้ำว่า EA/source code และ presets ไม่เปลี่ยนจาก commit ที่เสนอไว้

## ขอบเขตการรันในอนาคต

การรันในอนาคตต้องจำกัดแคบมาก:

- Symbol: EURUSD เท่านั้น
- Timeframe: H1 เท่านั้น
- ช่วงเวลาสั้นเพื่อ diagnostic เท่านั้น
- Strategy Tester เท่านั้น
- รันเพียง 1 ครั้ง
- ห้าม optimization
- ห้าม demo/live/forward test
- ห้าม market order
- ห้าม pending order
- ห้ามแก้ position
- ห้ามเพิ่ม lot/risk
- ห้ามตีความเรื่อง profitability

## Config ที่ต้องตรวจสอบก่อนรัน

ก่อนเริ่มรันในอนาคต ต้องบันทึก effective config และตรวจให้ครบ:

- `InpEnablePriceActionFibo=true`
- `InpPriceActionFiboDiagnosticsOnly=true`
- `InpPAFUsePendingOrders=false`
- `InpPAFMaxPendingOrders=0`
- `InpManageExistingPositions=false`
- `InpRequireStrategyTester=true`
- `InpPAFLogOnlyOnNewBar=true`
- ไม่มี existing/open position ใน tester context
- optimization disabled
- Strategy Tester เท่านั้น

ถ้าข้อใดไม่ตรงหรือพิสูจน์ไม่ได้ ห้ามเริ่มรัน

## เงื่อนไขหยุดทันที

ต้องหยุดทันทีและถือว่า fail หากพบ:

- config mismatch
- มี market order attempt
- มี pending order attempt
- มี position modification attempt
- baseline strategy fallback
- log ถี่เกินไป
- optimization enabled
- ตรวจพบ demo/live/forward environment

## Artifact ที่ต้องมีหลังการรันในอนาคต

ถ้ามีการอนุมัติและรันจริงในอนาคต ต้องเก็บ:

- RunId
- Strategy Tester report/log path
- effective config snapshot
- forbidden action grep/check summary
- Price Action / Fibo diagnostic classification summary
- no-trade confirmation
- no baseline fallback confirmation

## สิ่งที่ Checkpoint S ยังไม่อนุมัติ

Checkpoint S ยังไม่อนุมัติ:

- การรัน MT5 ตอนนี้
- การรัน Strategy Tester ตอนนี้
- การรันมากกว่า 1 ครั้ง
- optimization
- demo/live/forward testing
- market orders
- pending orders
- position modification
- lot/risk increase
- profitability interpretation

## ประตูถัดไป

หลัง Checkpoint S ถูก review แล้ว ผู้ใช้ต้องให้คำอนุมัติแยกอีกครั้งก่อนจึงจะรัน Strategy Tester diagnostic แบบห้ามเทรด 1 ครั้งได้

จนกว่าจะมีคำอนุมัตินั้น การรันจริงยังถูก block
