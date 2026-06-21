# Checkpoint C: Case-Level Scoring And Controlled Matrix Run

วันที่: 2026-06-21

Checkpoint C เพิ่มการสรุปผลระดับ case และรัน controlled matrix subset แบบจำกัดเท่านั้น ไม่ใช่การ optimize และไม่ใช่หลักฐานว่าระบบจะทำกำไรในอนาคต

## ข้อจำกัดของ Checkpoint นี้

- ไม่ optimize parameters
- ไม่เพิ่ม MicroTrend
- ไม่เปลี่ยน strategy entry/exit logic เพื่อไล่กำไร
- ไม่ claim profitability
- ไม่รัน full matrix
- ไม่เริ่ม live หรือ demo forward test

## ทำไม Checkpoint B น่าสนใจแต่ยังไม่พอ

Checkpoint B ของ `EURUSD_H1_10000` มี validation และ out-of-sample เป็นบวก แต่ train ติดลบและจำนวน trade ใน train ต่ำ

ผลนี้น่าสนใจเพราะ:

- validation เป็นบวก
- out-of-sample เป็นบวก
- report parse ได้ครบ
- risk gates ทำงาน

แต่ยังไม่พอเพราะ:

- train net profit ติดลบ
- train trade count ต่ำกว่าเกณฑ์
- ยังเป็นเพียง backtest
- ยังไม่ได้ทดสอบหลาย symbol/timeframe อย่างเป็นระบบ
- ยังไม่ได้ forward test บน demo

ดังนั้น Checkpoint C เปลี่ยนจากการมอง phase เดียวเป็นการมอง case-level classification

## ทำไม train loss เป็น warning

Train loss ไม่ได้แปลว่าระบบต้องถูกทิ้งทันที แต่เป็น warning สำคัญ เพราะ:

- strategy อาจไม่เสถียรในบางสภาพตลาด
- validation/OOS ที่ดีอาจเกิดจากช่วงตลาดเฉพาะ
- จำนวน trade ใน train น้อยทำให้ความน่าเชื่อถือต่ำ

ถ้า validation และ out-of-sample ผ่าน แต่ train แพ้หรือ trade ต่ำ case จะถูกจัดเป็น:

```text
TRAIN_FAILED_VALIDATION_OOS_PASS
```

ซึ่งแปลว่า "น่าสนใจสำหรับ research ต่อ" แต่ยังไม่ใช่ candidate ที่แข็งแรง

## ทำไม validation และ out-of-sample สำคัญกว่า train profit

Train profit อาจเกิดจาก overfitting ได้ง่าย โดยเฉพาะถ้าใช้ผล train เพื่อเลือก parameter

Validation และ out-of-sample สำคัญกว่าเพราะ:

- ช่วยลดโอกาสเลือกค่าที่พอดีกับอดีตมากเกินไป
- ช่วยดูว่าพฤติกรรมยังอยู่รอดในข้อมูลที่ไม่ได้ใช้เลือกค่าหรือไม่
- เหมาะกับปรัชญา survival-first มากกว่าการไล่กำไรสูงสุดใน train

ถึงอย่างนั้น validation/OOS ที่ดีเพียงอย่างเดียวก็ยังไม่ใช่ proof of future profitability

## Case-Level Classifications

Checkpoint C เพิ่ม case-level classification ดังนี้:

| Classification | ความหมาย |
|---|---|
| `EXECUTION_FAILED` | มี phase ที่ runner/tester/report/parser ล้มเหลว |
| `INCOMPLETE_PHASES` | มี phase ไม่ครบ train/validation/out_of_sample |
| `INSUFFICIENT_TOTAL_TRADES` | validation + out_of_sample มีจำนวน trade ไม่พอตามเกณฑ์ |
| `TRAIN_FAILED_VALIDATION_OOS_PASS` | validation และ OOS ผ่าน แต่ train ติดลบหรือไม่พอ |
| `VALIDATION_OOS_PASS` | validation และ OOS เป็นบวก แต่ยังไม่ผ่านทุก gate สำหรับ provisional |
| `PROVISIONAL_RESEARCH_CANDIDATE` | ผ่าน gate เชิง research เบื้องต้น แต่ยังไม่ใช่ final candidate |
| `REJECTED` | validation/OOS ไม่ผ่านหรือผลไม่สนับสนุน |
| `NO_RISK_BUDGET` | risk budget ต่ำกว่า broker minimum lot จนไม่สามารถทดสอบการเข้า trade ได้อย่างมีนัยสำคัญ |

## Provisional Candidate Gate

`PROVISIONAL_RESEARCH_CANDIDATE` ต้องผ่านอย่างน้อย:

- validation net profit > 0
- out_of_sample net profit > 0
- validation + out_of_sample trades รวมกัน >= 150
- validation trades >= 50
- out_of_sample trades >= 50
- relative drawdown <= 20%
- profit factor >= 1.10 ทั้ง validation และ out_of_sample
- ไม่มี infrastructure failure
- train ไม่ควรเป็น warning หลัก เช่น ติดลบหรือ trade ต่ำมาก

คำว่า provisional ยังไม่ใช่ approval และไม่ใช่ proof ว่าจะทำกำไรในอนาคต

## Controlled Matrix Subset

Checkpoint C รันเฉพาะ 3 cases ต่อไปนี้ ครบ train, validation, out_of_sample:

- `EURUSD_H1_10000`
- `USDJPY_HASH_H1_10000`
- `GOLD_HASH_H4_30000`

ไม่ได้รัน full matrix

Run ล่าสุด:

```text
research/runs/run_20260621_173616/
```

Summary:

```text
research/runs/run_20260621_173616/research_summary_for_run.md
research/results/research_summary.md
```

## วิธีอ่านผล

อ่านตามลำดับ:

1. `Case-Level Summary`
2. `Phase Results`
3. `Phase Classifications`
4. `Failed Gates`
5. `Warnings`

ให้ดู case-level ก่อน phase-level เพราะ phase เดียวที่ดีอาจไม่พอหากอีก phase ล้มเหลวหรือต่ำกว่าเกณฑ์

## ทำไมสิ่งนี้ยังไม่ใช่ optimization

Checkpoint C ใช้ parameter ที่มีอยู่แล้วและรัน subset ที่กำหนดไว้ล่วงหน้า ไม่มีการ search parameter, ไม่มีการเลือกค่าที่ทำกำไรสูงสุด และไม่มีการปรับ strategy logic

เป้าหมายคือทดสอบ pipeline และ classification เท่านั้น

## ทำไมยังไม่ควรเริ่ม live/demo forward test

ยังไม่ควรเริ่ม forward test เพราะ:

- matrix ยังไม่ครบ
- ยังไม่มี robustness review ที่สมบูรณ์
- GOLD# ยังมี risk/broker minimum lot behavior ที่ต้องตรวจต่อ
- USDJPY# และบาง phase ยังไม่ผ่าน gates
- ผล backtest ไม่ใช่ผลลัพธ์ในตลาดอนาคต

ขั้นถัดไปควรเป็น review ผล Checkpoint C และปรับ research process ก่อน ไม่ใช่เปิดระบบเทรดจริง

