# Checkpoint BL: PAF Real CSV Offline Pipeline Preflight Result

วันที่จัดทำ: 2026-07-08

## สถานะ

Checkpoint BL ได้รับ approval phrase จากผู้ใช้เพื่อรัน offline PAF pipeline กับไฟล์ CSV จริง:

`G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\manual_exports\GOLD_HASH_H1_20260301_20260310_raw_mt5.csv`

ผลลัพธ์: `BLOCKED_TIMEFRAME_MISMATCH`

ไม่มีการรัน offline pipeline เพราะ preflight พบว่าไฟล์ CSV ที่ระบุมีลักษณะเป็น M1 ไม่ใช่ H1

## Guardrails

Checkpoint นี้:

- ไม่รัน MT5
- ไม่รัน Strategy Tester
- ไม่รัน offline pipeline
- ไม่แก้ EA/source code
- ไม่แก้ presets
- ไม่ optimize
- ไม่เพิ่ม lot/risk
- ไม่ claim profitability
- ไม่อนุมัติ order path
- ไม่อนุมัติ demo/live

## Approval Received

ข้อความอนุมัติที่ได้รับ:

`Approved to execute Checkpoint BL offline PAF pipeline on real GOLD# H1 bars CSV G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\manual_exports\GOLD_HASH_H1_20260301_20260310_raw_mt5.csv for RunId run_20260707_172236.`

## Preflight File Check

ไฟล์มีอยู่จริง:

- Path: `G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\manual_exports\GOLD_HASH_H1_20260301_20260310_raw_mt5.csv`
- Size: ประมาณ `645399` bytes
- Format: raw MT5-style CSV

Header ที่พบ:

```text
<DATE>	<TIME>	<OPEN>	<HIGH>	<LOW>	<CLOSE>	<TICKVOL>	<VOL>	<SPREAD>
```

ตัวอย่างแถวต้นไฟล์:

```text
2026.03.02	01:00:00	5300.25	5363.98	5300.25	5315.43	196	0	18
2026.03.02	01:01:00	5315.07	5328.55	5302.87	5318.81	481	0	105
2026.03.02	01:02:00	5318.00	5338.82	5314.50	5333.85	483	0	127
```

แถวเวลาเพิ่มทีละ 1 นาที จึงไม่ตรงกับ requirement `GOLD#` H1 bars CSV

## Why Pipeline Was Blocked

Checkpoint BK/BL-Prep ระบุว่าต้องใช้ `GOLD#` H1 bars CSV

ไฟล์ที่อนุมัติมามีลักษณะเป็น M1 data:

- `01:00:00`
- `01:01:00`
- `01:02:00`

ถ้ารัน joiner ด้วย M1 data ในขณะที่ diagnostic events และ horizon ถูกตั้งไว้สำหรับ H1 จะทำให้ผลลัพธ์ผิดความหมาย เช่น:

- horizon 48 อาจกลายเป็น 48 นาที ไม่ใช่ 48 ชั่วโมง
- event matching อาจไม่ใช่ bar basis เดียวกัน
- TP/SL shadow outcome อาจอ่านผิด
- ผลวิจัยอาจถูกตีความเกินจริง

ดังนั้น Codex จึงหยุดก่อนรัน pipeline

## Required Fix

ต้อง export ใหม่เป็น `GOLD#` H1 bars เท่านั้น

ช่วงเวลาที่ต้องการ:

`2026-03-01 00:00:00` ถึงอย่างน้อย `2026-03-10 23:59:59`

ชื่อไฟล์ที่แนะนำ:

`G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\manual_exports\GOLD_HASH_H1_20260301_20260310_raw_mt5_H1.csv`

หรือถ้าจะใช้ชื่อเดิม ให้แน่ใจว่าไฟล์ใหม่เป็น H1 จริง

## How To Confirm H1 Before Approval

เปิด CSV แล้วดูแถวแรก ๆ ควรเป็นเวลาเพิ่มทีละ 1 ชั่วโมง เช่น:

```text
2026.03.02	01:00:00
2026.03.02	02:00:00
2026.03.02	03:00:00
```

ไม่ควรเป็น:

```text
2026.03.02	01:00:00
2026.03.02	01:01:00
2026.03.02	01:02:00
```

## Future Approval Phrase

หลัง export H1 ใหม่แล้ว ให้ส่ง:

`Approved to execute Checkpoint BO offline PAF pipeline on real GOLD# H1 bars CSV <absolute_path_to_h1_csv> for RunId run_20260707_172236.`

ใช้ Checkpoint BO เพื่อแยกจาก Checkpoint BL ที่ถูก block แล้ว

## Decision

- `BL_APPROVAL_RECEIVED`
- `CSV_FILE_FOUND`
- `RAW_MT5_STYLE_CSV_DETECTED`
- `BLOCKED_TIMEFRAME_MISMATCH`
- `CSV_APPEARS_M1_NOT_H1`
- `OFFLINE_PIPELINE_NOT_RUN`
- `MT5_NOT_RUN`
- `STRATEGY_TESTER_NOT_RUN`
- `ORDER_PATH_STILL_BLOCKED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`

## Progress Estimate

- Research infrastructure readiness: `79%`
- PAF diagnostic readiness: `70%`
- PAF shadow-outcome readiness: `68%`
- Order implementation readiness: `0%`
- Demo/live readiness: `0%`

ความคืบหน้าไม่เพิ่ม เพราะข้อมูล CSV ที่ส่งมายังไม่ตรง timeframe ที่อนุมัติไว้
