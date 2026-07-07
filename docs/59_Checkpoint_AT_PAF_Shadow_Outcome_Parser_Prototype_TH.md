# Checkpoint AT: PAF Shadow Outcome Parser Prototype

วันที่จัดทำ: 2026-07-07

## สถานะ

Checkpoint AT เป็น parser/research-output checkpoint สำหรับอ่าน artifact เดิมจาก Checkpoint AQ เท่านั้น

ไม่ได้รัน MT5, ไม่ได้รัน Strategy Tester, ไม่ได้ spawn `terminal64.exe`, ไม่ได้แก้ EA/source code, ไม่ได้แก้ presets, ไม่ได้ optimize, ไม่ได้เพิ่ม lot/risk, ไม่ได้เปิด market order, ไม่ได้เปิด pending order, ไม่ได้ modify position และไม่ได้ claim profitability

## เป้าหมาย

สร้าง prototype สำหรับอ่าน Price Action / Fibo diagnostic logs แล้วแปลงเป็น shadow outcome rows แบบไม่เปิดออเดอร์ เพื่อดูว่าข้อมูล diagnostic ที่มีอยู่เพียงพอสำหรับวัดผลสมมติฐานหรือยัง

เป้าหมายสำคัญคือห้ามเดาทิศทางย้อนหลัง ถ้า diagnostic event ไม่มี direction ต้องติดป้าย `DIRECTION_MISSING` และหยุดไม่ให้คำนวณ TP/SL outcome

## ไฟล์ที่เพิ่ม

- `tools/paf_shadow_outcome_labeler.py`
- `research/results/paf_shadow_outcomes_all_cases.csv`
- `research/results/paf_shadow_outcome_summary.json`
- `research/results/paf_shadow_outcome_summary.md`
- `research/results/checkpoint_at_shadow_outcome_parser_summary.md`
- `docs/59_Checkpoint_AT_PAF_Shadow_Outcome_Parser_Prototype_TH.md`
- `docs/ai/tasks/checkpoint-at-paf-shadow-outcome-parser-prototype.md`

## Input ที่ใช้

ใช้ artifact เดิมจาก Checkpoint AQ:

- RunId: `run_20260707_151857`
- Artifact root: `G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\run_20260707_151857`
- Symbol/timeframe: `GOLD#` H1
- Windows:
  - `2026-01-01` ถึง `2026-02-01`
  - `2026-02-01` ถึง `2026-03-01`
  - `2026-03-01` ถึง `2026-04-01`

Parser ใช้ `ea_mirror.log` เป็น authoritative source เมื่อมีไฟล์นี้ และ join ค่า spread จากบรรทัด `No trade` ที่ timestamp เดียวกันกับ diagnostic event

## ผลลัพธ์หลัก

จาก 3 windows ของ Checkpoint AQ:

- Diagnostic events ทั้งหมด: `954`
- `NO_SETUP` ที่ข้ามไป: `687`
- Possible setup rows ที่เขียนลง CSV: `267`
- Outcome label ทั้งหมด: `DIRECTION_MISSING`

แยกตาม possible setup classification:

| Classification | Count |
|---|---:|
| `POSSIBLE_FIBO_PULLBACK` | 145 |
| `POSSIBLE_ZONE_REJECTION` | 85 |
| `POSSIBLE_BREAK_RETEST` | 37 |

แยกตาม spread bucket:

| Spread bucket | Count |
|---|---:|
| `LOW_SPREAD` | 164 |
| `NORMAL_SPREAD` | 103 |

## การตีความ

ผลนี้ไม่ใช่ผลกำไร และไม่ใช่หลักฐานว่า Price Action / Fibo ใช้เทรดได้

ผลนี้บอกว่า workflow diagnostic มีจำนวน event พอให้เริ่มวิเคราะห์ต่อได้ แต่ข้อมูลยังไม่พอสำหรับ shadow TP/SL outcome เพราะ event ไม่มี `direction`

ดังนั้นห้าม:

- เดา buy/sell จากกราฟย้อนหลัง
- ใช้ผลนี้เป็น entry signal
- เปิด market order
- เปิด pending order
- modify position
- optimize parameter
- เพิ่ม lot/risk
- เริ่ม demo/live forward test

## ข้อจำกัดที่พบ

- Diagnostic event ไม่มี direction field
- Diagnostic event ไม่มี entry reference price / close price ที่ใช้เป็นจุดอ้างอิง
- Artifact ยังไม่มี OHLC/tick lookahead ที่ parser ใช้วัด TP/SL ได้
- Session bucket เป็นการ bucket ตาม broker/server time จาก timestamp ใน log เท่านั้น ไม่ใช่เวลาไทย
- Spread bucket เป็น reporting attribution เท่านั้น ไม่ใช่ตัวกรองเทรดจริง

## ทำไมไม่ควรลองแบบโหดในขั้นนี้

การลองแบบโหด เช่น ยอมให้ล้างพอร์ตเพื่อหา edge อาจใช้ได้เฉพาะใน sandbox research ที่ไม่มีออเดอร์จริงและไม่มีการเพิ่มความเสี่ยงจริง แต่ถ้าใช้กับ EA order path เร็วเกินไป จะทำให้ระบบเรียนรู้จาก noise และ overfit จากช่วงเวลาสั้น

แนวทางที่ปลอดภัยกว่าคือ:

- ใช้ no-order diagnostics เพื่อแยกว่าระบบเห็น setup ช่วงไหน
- เพิ่ม direction และ OHLC context แบบ deterministic
- ทำ shadow outcome หลายช่วงเวลา
- แยก regime, spread, session, volatility
- ค่อยตัดสินว่าควร research order path หรือ reject

## Decision

```text
PAF_SHADOW_OUTCOME_PARSER_PROTOTYPE_CREATED
AQ_SHADOW_OUTCOME_BLOCKED_BY_MISSING_DIRECTION
NO_ORDER_IMPLEMENTATION_APPROVED
NO_OPTIMIZATION_APPROVED
```

## Next Safe Step

Checkpoint AU ควรเป็น specification/approval checkpoint สำหรับเพิ่ม diagnostic fields ที่จำเป็น เช่น:

- direction context
- entry reference price
- close price
- ATR / volatility context
- optional exported OHLC window for no-order shadow labeling

ยังไม่ควร implement market order หรือ pending order จนกว่า shadow outcome จะมีข้อมูลเพียงพอและผ่านหลาย windows โดยไม่เดาทิศทางย้อนหลัง
