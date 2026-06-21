# ForexAiTrade Current Checkpoint Status

วันที่: 2026-06-19

เอกสารนี้เป็น safe checkpoint เท่านั้น ไม่มีการ optimize parameters, ไม่มีการ claim profitability, ไม่มีการเปลี่ยน strategy entry/exit logic เพิ่ม และไม่มีการรัน MT5 test เพิ่มใน checkpoint นี้

## สรุปสถานะปัจจุบัน

โปรเจกต์อยู่ในสถานะ checkpoint หลังจากมีการทำงานด้าน safety, XM symbol handling, smoke test, และ batch runner reliability บางส่วนไปแล้ว แต่ research pipeline แบบเต็มยังถือว่าไม่ complete

เป้าหมายของ checkpoint นี้คือหยุด scope expansion และเก็บสถานะปัจจุบันเป็น package ที่ตรวจสอบต่อได้

## ไฟล์ที่มีการเปลี่ยน/สร้างที่เกี่ยวข้อง

ไฟล์หลักที่เปลี่ยนหรือสร้างในช่วงล่าสุด:

- `scripts/run_mt5_research_batch.ps1`
- `MQL5/Experts/ForexAiTrade/ForexAiTrade.mq5`
- `MQL5/Include/ForexAiTrade/Inputs.mqh`
- `research/research_matrix.json`
- `tools/research_report_parser.py`
- `tools/research_score.py`
- `tools/generate_research_summary.py`
- `docs/13A_Checkpoint_Process_Safety_And_Matrix.md`
- `docs/13_Controlled_Research_Pipeline.md`
- `docs/14_MT5_Batch_Runner_Reliability.md`
- `docs/15_Robustness_Scoring_Method.md`
- `docs/16_Dedicated_MT5_Research_Instance_TH.md`
- `docs/17_Current_Research_Pipeline_Status_TH.md`
- `docs/18_Current_Checkpoint_Status_TH.md`
- `docs/verification/compile_after_checkpoint_A.log`
- `docs/verification/compile_after_research_pipeline.log`

หมายเหตุ: repository นี้ไม่มี git metadata ที่ใช้งานได้ใน workspace ปัจจุบัน จึงสรุปจากไฟล์ที่พบและงานที่ทำใน session นี้

## งานที่ completed

- เพิ่ม/ตรวจ input `InpManagePositionsOnlyOnNewBar=false`
- แยก position management timing ออกจาก new-bar entry gate
- คง safety gates เดิมไว้ ได้แก่:
  - `InpLiveTradingEnabled`
  - `InpDemoSafeMode`
  - `InpRequireStrategyTester`
  - `InpManageExistingPositions`
- ตรวจ batch runner ว่าใช้ `Start-Process -PassThru`
- batch runner เก็บ spawned process ID
- timeout handler ใช้ `Stop-Process -Id $process.Id -Force` เฉพาะ process ที่ runner เปิดเอง
- ไม่พบ bulk `Get-Process terminal64 | Stop-Process` ใน runner
- สร้าง `research/research_matrix.json`
- สร้างเอกสาร checkpoint/process safety
- compile EA ล่าสุดผ่าน `0 errors, 0 warnings`
- สร้าง package checkpoint zip ตามคำขอนี้

## งานที่ not completed

- ยังไม่ถือว่า research pipeline แบบเต็ม complete
- ยังไม่ควรใช้ผล smoke/integration เป็นหลักฐานกำไร
- ยังไม่ได้ทำ parameter optimization
- ยังไม่ได้ทำ full historical train/validation/out-of-sample campaign
- ยังไม่ได้ทำ demo forward test ระยะยาว
- ยังไม่ได้ finalize robustness scoring สำหรับการคัดเลือก parameter set จริง
- ยังไม่ได้ทำ report parser ให้รับประกันว่าครอบคลุมทุก MT5 locale/report format

## MT5 batch run status

ใน checkpoint นี้:

- ไม่ได้ start MT5 batch run ใหม่
- ไม่ได้ run Strategy Tester ใหม่
- ไม่ได้ kill หรือ close MT5 terminal ใด ๆ

จาก artifacts ที่มีอยู่ก่อนหน้า พบว่ามี batch/integration run เก่าใน:

```text
research/runs/
```

รันล่าสุดที่มี report parse ได้:

```text
research/runs/run_20260619_221606/
```

เคสในรันนี้:

- `EURUSD_H1_10000_out_of_sample`: `PASS`
- `USDJPY_HASH_H1_10000_out_of_sample`: `PASS`
- `GOLD_HASH_H4_10000_out_of_sample`: `PASS`

รันเก่าบางชุดยังมีสถานะ `NO_REPORT` และควรถือเป็น debug artifacts ไม่ใช่ผลวิจัย

## MT5 process status

ตรวจด้วย `Get-Process terminal64 -ErrorAction SilentlyContinue`

ผลล่าสุด:

```text
No terminal64 process found.
```

ไม่มี MT5 process ค้างจาก runner ณ ตอนทำ checkpoint นี้

## Reports generated

พบ report ที่ generate แล้วในรันล่าสุด:

```text
research/runs/run_20260619_221606/EURUSD_H1_10000_out_of_sample/mt5_report.htm
research/runs/run_20260619_221606/USDJPY_HASH_H1_10000_out_of_sample/mt5_report.htm
research/runs/run_20260619_221606/GOLD_HASH_H4_10000_out_of_sample/mt5_report.htm
```

ไฟล์ parsed result มีอยู่ใน case folders ของรันเดียวกัน

## Timeout handler safety confirmation

ใน `scripts/run_mt5_research_batch.ps1` พบ logic สำคัญ:

```text
Start-Process ... -PassThru
Stop-Process -Id $process.Id -Force
```

ไม่พบ bulk terminal kill pattern เช่น:

```text
Get-Process terminal64 | Stop-Process
```

ดังนั้น timeout handler ใน runner ปัจจุบันถูกจำกัดให้ stop เฉพาะ process ที่ runner start เอง

## Known issues

- Research pipeline แบบเต็มยัง incomplete
- มี debug runs เก่าที่ status เป็น `NO_REPORT` ปนอยู่ใน `research/runs/`
- Summary รวมอาจรวมรันเก่าที่ fail ด้วย จึงควรดู `run_20260619_221606` แยกเมื่อต้องการรันล่าสุดที่ parse ได้
- ผล backtest/smoke test ไม่ใช่ profitability proof
- GOLD# มีเคสที่ risk budget ต่ำกว่า broker minimum lot ซึ่งเป็น safety behavior ที่ควรตรวจต่อก่อนเพิ่ม risk/deposit
- ควรใช้ dedicated MT5 research instance เท่านั้น ไม่ควรใช้ terminal ที่มี live trading

## Package contents

ไฟล์ zip checkpoint รวมโฟลเดอร์:

- `MQL5/`
- `scripts/`
- `tools/`
- `docs/`
- `presets/`
- `research/`
- `smoke_test_artifacts/`

ไม่รวม:

- `.ex5`
- `__pycache__`
- `.pyc`

