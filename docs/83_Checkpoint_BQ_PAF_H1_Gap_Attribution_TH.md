# Checkpoint BQ: PAF H1 Gap Attribution

เอกสารนี้สรุปผลการตรวจสอบช่องว่างของข้อมูล `GOLD#` H1 จาก Checkpoint BP แบบ offline เท่านั้น

รอบนี้ไม่ได้รัน MT5, ไม่ได้รัน Strategy Tester, ไม่ได้เปลี่ยน EA/source code, ไม่ได้เปลี่ยน preset, ไม่ได้ optimize parameter, และไม่ได้สรุปผลกำไร

## เป้าหมาย

Checkpoint BP รัน offline PAF pipeline กับไฟล์ H1 CSV จริงได้ถึงขั้น normalization แต่ validator หยุดด้วยเหตุผล:

`detected gaps larger than expected timeframe step: 6`

เป้าหมายของ Checkpoint BQ คือแยกประเภท gap ทั้ง 6 จุดว่าเป็น:

- market/weekend closure ที่อาจเป็นพฤติกรรมปกติของตลาด
- session gap ตาม broker
- history/data gap ที่ต้องตรวจเพิ่ม

## Input ที่ตรวจสอบ

- Bars CSV: `research/results/checkpoint_bp_real_csv_pipeline/paf_lookahead_bars.csv`
- Bar count: `139`
- Coverage from: `2026-03-02 01:00:00`
- Coverage to: `2026-03-10 00:00:00`

## ผลการแยกประเภท Gap

| ประเภท | จำนวน |
|---|---:|
| `SHORT_SESSION_OR_HISTORY_GAP` | 5 |
| `WEEKEND_MARKET_CLOSURE` | 1 |
| รวม gap ที่มากกว่า 1 ชั่วโมง | 6 |

## รายละเอียด Gap

| Previous time | Next time | Delta hours | Missing H1 bars est. | Classification |
|---|---|---:|---:|---|
| 2026-03-02 23:00:00 | 2026-03-03 01:00:00 | 2.0 | 1 | `SHORT_SESSION_OR_HISTORY_GAP` |
| 2026-03-03 23:00:00 | 2026-03-04 01:00:00 | 2.0 | 1 | `SHORT_SESSION_OR_HISTORY_GAP` |
| 2026-03-04 23:00:00 | 2026-03-05 01:00:00 | 2.0 | 1 | `SHORT_SESSION_OR_HISTORY_GAP` |
| 2026-03-05 23:00:00 | 2026-03-06 01:00:00 | 2.0 | 1 | `SHORT_SESSION_OR_HISTORY_GAP` |
| 2026-03-06 23:00:00 | 2026-03-09 00:00:00 | 49.0 | 48 | `WEEKEND_MARKET_CLOSURE` |
| 2026-03-09 22:00:00 | 2026-03-10 00:00:00 | 2.0 | 1 | `SHORT_SESSION_OR_HISTORY_GAP` |

## การตีความ

ผลนี้แปลว่า gap ไม่ได้เป็น weekend closure ทั้งหมด

ช่องว่าง Friday to Monday จำนวน 1 จุดน่าจะสอดคล้องกับตลาดปิดช่วง weekend แต่ gap อีก 5 จุดเป็นช่องว่างรายวันประมาณ 2 ชั่วโมง ซึ่งอาจเกิดจาก broker session, market close ช่วงสั้น, export setting, หรือข้อมูล history ที่ขาด

ดังนั้นยังไม่ควร bypass validator และยังไม่ควรรัน joiner ต่อโดยอัตโนมัติ

## การตัดสินใจของ Checkpoint BQ

- `GAP_ATTRIBUTION_DONE`
- `WEEKEND_MARKET_CLOSURE_1`
- `SHORT_SESSION_OR_HISTORY_GAP_5`
- `GAPS_REQUIRE_MANUAL_REVIEW`
- `JOINER_STILL_BLOCKED`
- `VALIDATOR_NOT_BYPASSED`
- `MT5_NOT_RUN`
- `STRATEGY_TESTER_NOT_RUN`
- `EA_SOURCE_NOT_CHANGED`
- `PRESETS_NOT_CHANGED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`

## ข้อเสนอรอบถัดไป

Checkpoint ถัดไปควรเป็นการรีวิว policy ของ validator สำหรับข้อมูล H1 ของ Gold/XM:

- ยืนยันว่า gap รายวัน 23:00 -> 01:00 เป็น broker session ปกติหรือไม่
- กำหนด rule แบบ explicit สำหรับ market-session gap ที่อนุญาตได้
- แยก weekend closure ออกจาก true missing data
- ห้าม bypass validator แบบกว้างๆ
- ห้ามรัน joiner จนกว่า gap policy จะถูก review และบันทึกชัดเจน

รอบนี้ยังไม่ใช่หลักฐานความพร้อมสำหรับ order, pending order, demo, หรือ live trading
