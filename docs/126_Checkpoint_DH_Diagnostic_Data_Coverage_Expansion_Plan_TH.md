# Checkpoint DH: แผนเพิ่ม Coverage ข้อมูล Diagnostic สำหรับ Fibo Pullback

วันที่: 2026-07-09

## สถานะ

Checkpoint DH เป็นเอกสารแผนและแพ็กเกจอนุมัติล่วงหน้าเท่านั้น

ไม่มีการรัน MT5 ไม่มีการรัน Strategy Tester ไม่มีการแก้ EA/MQL5 ไม่มีการแก้ preset ไม่มีการแก้ trading logic ไม่มีการ optimize ไม่มีการเพิ่ม lot/risk ไม่มีการเพิ่ม order logic และไม่มีการตีความกำไร

PAF / Price Action Fibo ยังเป็น diagnostic-only และยังคงสถานะ:

`NOT_READY_FOR_ORDER_LOGIC`

## เหตุผล

Checkpoint DG ตีความ row-level Fibo Pullback slice จาก Checkpoint DF แล้วพบว่า diagnostic context ดีขึ้น แต่ยังไม่ผ่าน gate สำคัญ:

| Metric | Current |
|---|---:|
| Fibo Pullback rows | 128 |
| Fibo usable first-touch rows | 85 |
| Fibo direction gap rows | 43 |
| Usable first-touch share | 66.4% |
| Direction gap share | 33.6% |
| SELL rows | 53 |
| BUY rows | 32 |
| DIRECTION_UNKNOWN rows | 43 |
| Diagnostic windows | 8 |

Gate ปัจจุบัน:

| Gate | Requirement | Current | Decision |
|---|---:|---:|---|
| Fibo usable first-touch rows | >= 150 | 85 | FAIL |
| Diagnostic windows | >= 12 | 8 | FAIL |
| Rule-candidate readiness | approved gate | not approved | FAIL |
| Order logic readiness | approved rule candidate | not approved | FAIL |

ดังนั้น DH ไม่ควรเสนอ rule-candidate และไม่ควรเสนอ order logic แต่ควรวางแผนเพิ่มข้อมูล diagnostic อย่างปลอดภัยก่อน

## เป้าหมายของ Future Diagnostic Coverage Run

ถ้าผู้ใช้อนุมัติใน checkpoint ถัดไป การรันในอนาคตควรมีเป้าหมายเฉพาะการเพิ่ม coverage:

- เพิ่มจำนวน diagnostic windows จาก `8` เป็นอย่างน้อย `12`
- เพิ่ม Fibo usable first-touch rows จาก `85` ไปทาง `150+`
- รักษาเงื่อนไข no-trade ทั้งหมด
- เก็บ artifact ให้ครบเพื่อให้ checkpoint ถัดไปตรวจสอบก่อนสรุปผล

เนื่องจากค่าเฉลี่ยเดิมคือประมาณ `10.6` Fibo usable rows ต่อ window การเพิ่มเพียง 4 windows อาจเพิ่มได้แค่ประมาณ `42` rows และอาจยังไม่ถึง `150` ดังนั้น DH เสนอให้ future run ใช้ 7 windows ต่อเนื่องหลังชุด DB เพื่อเพิ่มโอกาสให้ sample เข้าใกล้หรือเกิน `150` โดยไม่เลือกช่วงจากผลกำไรหรือผลลัพธ์ย้อนหลัง

## Target Windows สำหรับ Future Checkpoint DI

Scope ที่เสนอเป็น `GOLD#` H1 Strategy Tester diagnostic-only โดยใช้ช่วงเวลาต่อเนื่องหลังข้อมูลเดิม:

| Window | Date range |
|---|---|
| DI-W1 | `2026-04-26` to `2026-05-03` |
| DI-W2 | `2026-05-03` to `2026-05-10` |
| DI-W3 | `2026-05-10` to `2026-05-17` |
| DI-W4 | `2026-05-17` to `2026-05-24` |
| DI-W5 | `2026-05-24` to `2026-05-31` |
| DI-W6 | `2026-05-31` to `2026-06-07` |
| DI-W7 | `2026-06-07` to `2026-06-14` |

ผลหลัง DI ถ้ารันครบจะทำให้จำนวน windows รวมเพิ่มจาก `8` เป็น `15` ซึ่งผ่าน gate ขั้นต่ำ `12` windows

การเลือกช่วงนี้เป็นการต่อเนื่องตามปฏิทิน ไม่ใช่การเลือกช่วงเพื่อหากำไร ไม่ใช่ optimization และไม่ใช่การเลือก parameter

## Strict No-Trade Requirements

Future DI ต้องเป็น diagnostic-only เท่านั้น:

- `InpEnablePriceActionFibo=true`
- `InpPriceActionFiboDiagnosticsOnly=true`
- `InpPAFUsePendingOrders=false`
- `InpPAFMaxPendingOrders=0`
- `InpManageExistingPositions=false`
- `InpRequireStrategyTester=true`
- Strategy Tester only
- Optimization disabled
- Demo/live/forward test disabled
- ใช้ actual runtime symbol จาก `_Symbol`
- `InpAllowedSymbolsCsv` ต้องรองรับ broker-specific `GOLD#`
- total trades ต้องเป็น `0` ทุก window
- forbidden action markers ต้องเป็น `0`
- baseline fallback markers ต้องเป็น `0`

ห้ามตีความ `BUY`, `SELL`, `HIGH confidence`, หรือ `first-touch usable` เป็น signal เข้า order

## Required Artifacts

Future DI ต้องเก็บ artifact ต่อ window อย่างน้อย:

- `status.json`
- `case.json`
- `process_info.json`
- `generated_tester.ini`
- `effective_preset.set`
- `runner.log`
- Strategy Tester report
- tester log excerpt
- `ea_mirror.log`
- parsed result/report
- PAF diagnostic parser output
- forbidden action grep/check summary
- no-trade confirmation
- no-baseline-fallback confirmation
- Fibo Pullback row-level slice summary หลังรวมกับ CV + CY + DB + DI

ทุก research run ต้องแยก `execution_status` ออกจาก strategy performance เสมอ Losing หรือไม่มี trade ไม่ได้แปลว่า execution fail ถ้า artifact และ safety gate ถูกต้อง

## Stop Conditions

Future DI ต้องหยุดและจัดเป็น blocked/fail-safe ทันทีถ้าพบ:

- effective config mismatch
- symbol/timeframe/date range ไม่ตรง scope
- ใช้ symbol hardcoded แทน `_Symbol`
- optimization enabled
- demo/live/forward environment
- market order attempt
- pending order attempt
- position modification attempt
- RiskManager bypass
- lot/risk เพิ่มขึ้น
- baseline strategy fallback
- forbidden action marker มากกว่า `0`
- total trades มากกว่า `0`
- missing report artifact
- missing EA mirror log
- missing PAF diagnostics
- stale artifact reuse
- MT5 runner พยายามหยุด process ที่ตัวเองไม่ได้เริ่ม

ถ้า stop condition เกิดขึ้น ห้าม rerun เพิ่มเอง ต้องทำ checkpoint review ก่อน

## Exact Approval Phrase สำหรับ Future DI

Future DI ยังถูก block จนกว่าผู้ใช้จะส่งข้อความนี้แบบชัดเจน:

`Approved to execute Checkpoint DI diagnostic-only GOLD# H1 PAF/Fibo coverage expansion with Strategy Tester only, no optimization, no demo/live forward test, no EA or preset changes, no order logic, total trades must remain 0, using windows 2026-04-26 to 2026-05-03, 2026-05-03 to 2026-05-10, 2026-05-10 to 2026-05-17, 2026-05-17 to 2026-05-24, 2026-05-24 to 2026-05-31, 2026-05-31 to 2026-06-07, and 2026-06-07 to 2026-06-14 with the official AK runner/parser workflow.`

ข้อความอื่นที่คลุมเครือ เช่น "run it", "go ahead", หรือ "continue" ไม่พอสำหรับการรัน MT5

## Review Gate ก่อน Execution

ก่อนเริ่ม Future DI ต้องตรวจอีกครั้งว่า:

- branch/worktree สะอาดและ base มาจาก `origin/main`
- DH scope ยังตรงกับ status ล่าสุด
- ไม่มี PR ใหม่ที่เปลี่ยน PAF diagnostics, runner, preset, หรือ symbol handling โดยยังไม่ได้ review
- user approval phrase ตรงทุกคำ
- future run ยังเป็น Strategy Tester diagnostic-only
- ไม่มีการขอ optimize หรือเพิ่ม risk

ถ้า gate ใดไม่ผ่าน ต้องทำ checkpoint review ใหม่แทนการรัน

## Review Gate หลัง Execution

หลัง Future DI ถ้าได้รับอนุมัติและรันจริงแล้ว ต้องมี checkpoint review แยกต่างหากก่อนคุย rule-candidate:

- รวม CV + CY + DB + DI
- ตรวจจำนวน windows จริง
- ตรวจ Fibo usable first-touch rows ว่าถึง `150+` หรือไม่
- ตรวจ total usable direction rows เทียบ gate `300`
- ตรวจ BUY/SELL/UNKNOWN distribution
- ตรวจ `PRICE_BETWEEN_EMAS` และ `TREND_ALIGNMENT_CONFLICT`
- ตรวจ low-window weakness
- ตรวจ no-trade, forbidden marker, และ baseline fallback
- แยก execution status ออกจาก strategy interpretation

แม้ Future DI จะผ่าน execution และเพิ่ม rows ได้มากขึ้น ก็ยังไม่อนุมัติ order logic จนกว่า review gate จะผ่านและมี checkpoint ใหม่อนุมัติชัดเจน

## Verdict

- `DH_APPROVAL_PLAN_CREATED`
- `FIBO_COVERAGE_EXPANSION_SCOPE_DEFINED`
- `FUTURE_DI_REQUIRES_EXACT_APPROVAL`
- `MT5_NOT_RUN`
- `STRATEGY_TESTER_NOT_RUN`
- `EA_MQL5_NOT_CHANGED`
- `PRESETS_NOT_CHANGED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_ORDER_LOGIC_APPROVED`
- `NO_PROFITABILITY_CLAIM`
- `PAF_NOT_READY_FOR_ORDER_LOGIC`

## Progress Estimate

- Research infrastructure readiness: `93%`
- PAF diagnostic pipeline readiness: `87%`
- PAF diagnostic interpretation readiness: `66%`
- Fibo Pullback interpretation readiness: `62%`
- PAF rule-candidate readiness: `36%`
- PAF order-logic readiness: `0%`
- Demo/live readiness: `0%`
