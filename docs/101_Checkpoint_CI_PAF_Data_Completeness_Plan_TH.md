# Checkpoint CI: PAF Data Completeness Plan

Checkpoint CI เป็นแผนแก้ความสมบูรณ์ของข้อมูล Price Action / Fibo diagnostic ก่อนคิดเรื่อง order logic

รอบนี้เป็น documentation / planning เท่านั้น:

- ไม่รัน MT5
- ไม่รัน Strategy Tester
- ไม่แก้ EA/source code
- ไม่แก้ presets
- ไม่เพิ่ม order logic
- ไม่เพิ่ม market order
- ไม่เพิ่ม pending order
- ไม่เพิ่ม position modification
- ไม่ optimize
- ไม่เพิ่ม lot/risk
- ไม่สรุป profitability
- ไม่อนุมัติ demo/live

## เหตุผลที่ต้องทำ Checkpoint CI

Checkpoint CG และ CH พบว่า PAF offline first-touch diagnostics ยังไม่พร้อมใช้สร้างกฎเข้า order

ปัญหาหลัก:

- Rows ทั้งหมด: `33`
- Relabel-ready rows: `17`
- Direction-missing rows: `14`
- Data-missing rows: `2`
- Classification รวม: `NOT_READY_FOR_ORDER_LOGIC`

ถ้ารีบเพิ่ม order logic ตอนนี้ จะเสี่ยงสร้างกฎจากข้อมูลที่ยังไม่ครบและ sample เล็กเกินไป

## Data Completeness Definition

ข้อมูล diagnostic หนึ่งแถวควรพร้อมประเมิน first-touch ก็ต่อเมื่อมีข้อมูลเหล่านี้ครบ:

- `signal_time` หรือเวลาที่ใช้จับคู่กับ bars
- `symbol`
- `timeframe`
- `classification`
- `session_bucket`
- `spread_bucket`
- `regime`
- `direction`
- `entry_reference_price`
- `intended_sl`
- `intended_tp`
- `lookahead_bars_available`
- `offline_atr_14` ถ้าใช้ ATR analysis
- first-touch label สำหรับ horizon ที่ต้องการ

ถ้าขาด `direction`, `intended_sl`, หรือ `intended_tp` ไม่ควรนับเป็น relabel-ready row

## Current Blockers

### Blocker 1: Direction Missing

`DIRECTION_MISSING` มี `14` จาก `33` rows

ผลกระทบ:

- ไม่รู้ว่าควรวัด TP/SL ฝั่ง buy หรือ sell
- first-touch label กลายเป็นใช้ไม่ได้
- attribution บิด เพราะกลุ่มที่ประเมินได้เหลือน้อย

เป้าหมายก่อนเดินต่อ:

- ลด `DIRECTION_MISSING` ให้เหลือต่ำกว่า `10%` ของ diagnostic rows
- หรือถ้ายังลดไม่ได้ ต้องแยกเป็น `UNUSABLE_FOR_FIRST_TOUCH` อย่างชัดเจน

### Blocker 2: Relabel-ready Sample Size

Relabel-ready rows มีเพียง `17`

ผลกระทบ:

- session attribution ยังสรุปไม่ได้
- setup classification ยังสรุปไม่ได้
- spread/regime attribution ยังสรุปไม่ได้
- overfit risk สูงมาก

เป้าหมายก่อนคิด order logic:

- อย่างน้อย `100` relabel-ready rows ต่อ symbol/timeframe/window group สำหรับ diagnostic reading
- อย่างน้อย `300` relabel-ready rows ก่อนพิจารณา rule candidate
- กระจายหลายช่วงเวลา ไม่ใช่กระจุกในไม่กี่วัน

ตัวเลขนี้เป็น research guardrail ไม่ใช่การรับประกันผลกำไร

### Blocker 3: Missing Intended SL/TP Context

First-touch ที่ดีต้องรู้ว่า TP/SL ตั้งจากอะไร

ต้องเก็บหรือ reconstruct ให้ได้:

- entry reference
- SL reference
- TP reference
- SL distance points
- TP distance points
- ATR at signal
- R multiple target ถ้ามี

ถ้าไม่มีข้อมูลนี้ จะบอกไม่ได้ว่า `SL_FIRST` มาจาก entry timing, stop distance, TP distance, หรือ zone quality

## Required Field Map

| Field | Required | Reason |
|---|---:|---|
| `signal_time` | Yes | ใช้ join กับ bars |
| `symbol` | Yes | รองรับ broker symbol เช่น `GOLD#` |
| `timeframe` | Yes | แยก H1/H4/M30 |
| `classification` | Yes | แยก setup type |
| `direction` | Yes | จำเป็นต่อ TP/SL first-touch |
| `entry_reference_price` | Yes | ใช้คำนวณระยะ |
| `intended_sl` | Yes | ใช้วัด SL_FIRST |
| `intended_tp` | Yes | ใช้วัด TP_FIRST |
| `session_bucket` | Recommended | ใช้ attribution |
| `spread_bucket` | Recommended | ใช้ attribution |
| `regime` | Recommended | ใช้ attribution |
| `offline_atr_14` | Recommended | ใช้ volatility context |
| `source_run_id` | Yes | ป้องกันปน run |
| `source_file` | Yes | audit trail |

## Proposed Diagnostic Gates

ก่อนอนุญาตให้เพิ่ม order logic ในอนาคต ต้องผ่าน gate เหล่านี้:

1. `direction_missing_rate <= 10%`
2. `data_missing_rate <= 5%`
3. `relabel_ready_rows >= 100` สำหรับ diagnostic interpretation
4. `relabel_ready_rows >= 300` ก่อนพิจารณา rule candidate
5. มี `entry_reference_price`, `intended_sl`, `intended_tp` ครบ
6. มี sample หลายช่วงเวลา ไม่ใช่ช่วงเดียว
7. ไม่มีการใช้ OOS เพื่อจูน parameter
8. ยังแยก execution status ออกจาก performance interpretation

ถ้า gate ไม่ผ่าน:

- สถานะต้องเป็น `NOT_READY_FOR_ORDER_LOGIC`
- ห้ามเพิ่ม market/pending order
- ห้ามเพิ่ม filter ที่ใช้เงินจริงหรือ backtest order
- ห้ามเพิ่ม lot/risk เพื่อชดเชยข้อมูลน้อย

## Recommended Next Implementation Checkpoint

Checkpoint CJ ควรเป็น tooling-only/data-audit checkpoint:

- เพิ่มเครื่องมือ audit completeness จาก PAF joined CSV
- วัด missing rate ต่อ field
- วัด relabel-ready count ต่อ classification/session/regime
- สร้าง report ว่าแถวไหนหาย `direction`, `SL`, `TP`, หรือ bars
- ไม่เปลี่ยน EA/source
- ไม่เปลี่ยน presets
- ไม่รัน MT5
- ไม่เปลี่ยน first-touch labels

ตัวอย่าง output ที่ควรมีใน CJ:

- `research/results/checkpoint_cj_paf_data_completeness/completeness_summary.md`
- `research/results/checkpoint_cj_paf_data_completeness/completeness_summary.json`
- `research/results/checkpoint_cj_paf_data_completeness/missing_fields_by_row.csv`
- `research/results/checkpoint_cj_paf_data_completeness/readiness_by_classification.csv`

## Why Not Strategy Changes Yet

ยังไม่ควรทำ strategy changes เพราะ:

- ข้อมูลที่ใช้ประเมิน direction ยังหายมาก
- sample ที่พร้อมใช้จริงมีเพียง `17`
- Fibo Pullback ยัง `SL_FIRST_DOMINANT`
- session/spread/regime ยังแยกผลไม่ชัด
- ยังไม่มีหลักฐานว่า SL_FIRST เกิดจาก logic, SL distance, TP distance, หรือข้อมูลไม่ครบ

## Current Decision

`DATA_COMPLETENESS_WORK_REQUIRED`

`ORDER_LOGIC_NOT_APPROVED`

`NOT_READY_FOR_ORDER_LOGIC`

## Guardrail Confirmation

- `MT5_NOT_RUN`
- `STRATEGY_TESTER_NOT_RUN`
- `EA_SOURCE_NOT_CHANGED`
- `PRESETS_NOT_CHANGED`
- `ORDER_LOGIC_NOT_APPROVED`
- `OPTIMIZATION_NOT_APPROVED`
- `LOT_RISK_NOT_INCREASED`
- `PROFITABILITY_NOT_CLAIMED`
- `DEMO_LIVE_NOT_APPROVED`

