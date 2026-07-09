# Checkpoint DA: แพ็กอนุมัติการเก็บข้อมูล PAF เพิ่ม

วันที่: 2026-07-09

## สถานะ

Checkpoint DA เป็นเอกสารอนุมัติล่วงหน้าเท่านั้น

ไม่มีการรัน MT5 ไม่มีการรัน Strategy Tester ไม่มีการแก้ EA/source code ไม่มีการแก้ preset ไม่มีการ optimize ไม่มีการเพิ่ม lot/risk และไม่มีการตีความกำไร

## เหตุผล

Checkpoint CZ รวมผลจาก CV และ CY แล้วพบว่า pipeline แบบ no-trade diagnostic ทำงานได้ แต่ข้อมูลยังไม่พอสำหรับการตีความ rule อย่างมั่นคง

ผลรวมจาก CV + CY:

| Metric | Count |
|---|---:|
| Total diagnostic rows | 274 |
| Possible setup rows | 91 |
| Usable direction rows | 63 |
| No-setup direction not required | 183 |
| Trend alignment conflict | 12 |
| Wick too small | 11 |
| Price between EMAs | 5 |

Gate เดิมจาก Checkpoint CI:

- diagnostic interpretation ต้องการ usable direction rows อย่างน้อย `100`
- rule-candidate discussion ต้องการ usable direction rows อย่างน้อย `300`

ผลปัจจุบัน:

- usable direction rows = `63`
- diagnostic interpretation gate = `FAIL`
- rule-candidate gate = `FAIL`

ดังนั้น PAF ยังคงเป็น:

`NOT_READY_FOR_ORDER_LOGIC`

## ขอบเขต future Checkpoint DB

ถ้าผู้ใช้อนุมัติในอนาคต Checkpoint DB จะเป็นการรัน diagnostic-only เพิ่มเท่านั้น:

- Symbol: `GOLD#`
- Timeframe: `H1`
- Strategy Tester only
- ใช้ official AK runner/parser workflow
- ไม่ optimize
- ไม่ demo/live/forward test
- ไม่ส่ง market order
- ไม่ส่ง pending order
- ไม่แก้ position
- ไม่เพิ่ม lot/risk
- ไม่ตีความกำไร

## หน้าต่างข้อมูลที่เสนอ

เพื่อเพิ่ม usable direction rows ให้เข้าใกล้หรือเกิน gate `100` เสนอให้เพิ่ม 4 weekly windows ต่อจาก CY:

| Window | Date range |
|---|---|
| DB-W1 | `2026-03-29` to `2026-04-05` |
| DB-W2 | `2026-04-05` to `2026-04-12` |
| DB-W3 | `2026-04-12` to `2026-04-19` |
| DB-W4 | `2026-04-19` to `2026-04-26` |

เหตุผล:

- CV + CY มี 4 weekly windows และได้ usable direction rows `63`
- เฉลี่ยประมาณ `15.75` usable rows ต่อสัปดาห์
- ต้องการอย่างน้อยอีก `37` usable rows เพื่อผ่าน gate `100`
- เพิ่ม 4 windows เป็น buffer เผื่อบางสัปดาห์มี setup ต่ำ

นี่ไม่ใช่ optimization และไม่ใช่การเลือกช่วงเพื่อหากำไร แต่เป็นการเพิ่มข้อมูล diagnostic ให้ sample เพียงพอก่อนตีความ

## Required Effective Config

ก่อนรัน DB ในอนาคตต้องยืนยัน effective config:

- `InpEnablePriceActionFibo=true`
- `InpPriceActionFiboDiagnosticsOnly=true`
- `InpPAFUsePendingOrders=false`
- `InpPAFMaxPendingOrders=0`
- `InpManageExistingPositions=false`
- `InpRequireStrategyTester=true`
- `InpPAFLogOnlyOnNewBar=true`
- `InpAllowedSymbolsCsv` ต้องยอมรับ `GOLD#`
- ใช้ actual runtime symbol จาก `_Symbol`
- Optimization disabled
- Strategy Tester only

## Stop Conditions

ต้องหยุดทันทีถ้าพบ:

- effective config mismatch
- market order attempt
- pending order attempt
- position modification attempt
- baseline strategy fallback
- optimization enabled
- demo/live/forward environment
- missing report artifact
- missing EA mirror log
- missing PAF diagnostics
- stale artifact reuse
- forbidden action marker
- symbol/timeframe/date range ไม่ตรง scope

## Artifact Requirements

แต่ละ window ใน future DB ต้องมี:

- `status.json`
- `generated_tester.ini`
- `effective_preset.set`
- effective config snapshot
- `runner.log`
- Strategy Tester report
- tester log excerpt
- `ea_mirror.log`
- parsed report/result
- PAF diagnostic parser output
- forbidden action grep/check summary
- no-trade confirmation
- no-baseline-fallback confirmation

ห้ามใช้ artifact เก่ามายืนยันผลใหม่

## Pass Criteria สำหรับ Future DB

Future DB จะถือว่า execution ผ่านเฉพาะเมื่อ:

- ทุก window มี `execution_status=PASS`
- ทุก window มี report artifact
- ทุก window มี PAF diagnostics
- `total_trades=0` ทุก window
- forbidden action markers = `0`
- baseline fallback markers = `0`
- CT/field-presence parser keys ยังอยู่ครบ
- ไม่มี stale artifact reuse

หลังจากนั้นจึงค่อยทำ Checkpoint DC artifact review เพื่อรวม CV + CY + DB

## Data Sufficiency Target

เป้าหมายของ DB คือเพิ่มจำนวน usable direction rows:

- ถ้ารวม CV + CY + DB แล้ว usable direction rows >= `100`:
  - อนุญาตให้ทำ diagnostic interpretation review ใน checkpoint ถัดไป
  - ยังไม่อนุญาต order logic
- ถ้ายังต่ำกว่า `100`:
  - ต้องเก็บข้อมูลเพิ่มหรือทบทวน diagnostic scope
- ถ้ายังต่ำกว่า `300`:
  - ยังไม่ควรเริ่ม rule-candidate discussion

## Approval Phrase สำหรับ Future DB

การรัน DB ยังถูก block จนกว่าผู้ใช้จะส่งข้อความนี้แบบชัดเจน:

`Approved to execute Checkpoint DB PAF diagnostic data collection expansion with symbol GOLD# timeframe H1 windows 2026-03-29 to 2026-04-05, 2026-04-05 to 2026-04-12, 2026-04-12 to 2026-04-19, and 2026-04-19 to 2026-04-26 using official AK runner/parser workflow.`

## ข้อห้าม

Checkpoint DA และ future DB ไม่อนุญาต:

- optimize parameters
- เพิ่ม lot/risk
- claim profitability
- demo/live forward test
- สร้าง market order logic
- สร้าง pending order logic
- แก้ exit/position management logic
- แปลง diagnostic classification เป็น signal ซื้อขาย

## Recommendation

หลัง DA ควรให้ reviewer ตรวจเอกสารนี้ก่อน ถ้าผ่านและผู้ใช้อนุมัติด้วย approval phrase ข้างต้น จึงค่อยทำ Checkpoint DB แบบ one-scope multi-window diagnostic-only run

ความคืบหน้าโดยประมาณ:

- Research infrastructure readiness: `91%`
- PAF diagnostic readiness: `79%`
- PAF data sufficiency toward diagnostic interpretation: `63%` ของ gate 100 usable rows
- PAF order-logic readiness: `0%`
- Demo/live readiness: `0%`
