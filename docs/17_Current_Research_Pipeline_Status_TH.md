# ForexAiTrade Current Research Pipeline Status

วันที่: 2026-06-19

เอกสารนี้สรุปสถานะล่าสุดของ Controlled Research Pipeline เพื่อส่งให้ GPT หรือผู้รีวิวช่วยตรวจต่อได้

## สถานะล่าสุด

- EA compile ผ่านแล้ว: `0 errors, 0 warnings`
- Batch runner รุ่นใหม่ไม่ใช้การ kill `terminal64` แบบเหมารวมแล้ว
- Runner ควบคุมเฉพาะ PID ที่ตัวเองเปิดด้วย `Start-Process -PassThru`
- Integration smoke run ล่าสุดผ่านครบ 3 เคส
- MT5 report ถูก export เป็น `.htm` และ copy เข้า case folder ได้แล้ว
- Parser อ่าน metric หลักจาก MT5 HTML report ได้แล้ว
- ยังไม่มีการ optimize parameters
- ยังไม่มีการ claim profitability
- ยังไม่มีการเปิด live trading default
- ไม่มี martingale/grid recovery logic

## Run ล่าสุดที่ผ่าน

RunId:

```text
run_20260619_221606
```

ตำแหน่ง artifacts:

```text
research/runs/run_20260619_221606/
```

ไฟล์สำคัญในแต่ละ case:

- `case.json`
- `generated_tester.ini`
- `effective_preset.set`
- `process_info.json`
- `runner.log`
- `tester_log_excerpt.log`
- `ea_mirror.log`
- `mt5_report.htm`
- `parsed_result.json`
- `status.json`

## Integration Result

| Case | Execution Status | Research Classification | Notes |
|---|---|---|---|
| EURUSD_H1_10000_out_of_sample | PASS | VALID_RESULT | Report parse ได้ มี trade เพียงพอสำหรับ smoke-level review |
| USDJPY_HASH_H1_10000_out_of_sample | PASS | INSUFFICIENT_TRADES | Report parse ได้ แต่ trade count ต่ำเกินเกณฑ์ research |
| GOLD_HASH_H4_10000_out_of_sample | PASS | NO_RISK_BUDGET | ไม่เปิด trade เพราะ broker minimum lot เกิน risk budget ที่กำหนด |

## Parsed Metrics จากรันล่าสุด

| Symbol | TF | Deposit | Net Profit | Profit Factor | Max DD | Relative DD | Trades | Max Consecutive Losses |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| EURUSD | H1 | 10000 | 41.03 | 1.18 | 59.65 | 0.59% | 62 | 4 |
| USDJPY# | H1 | 10000 | -30.79 | 0.48 | 39.83 | 0.40% | 12 | 4 |
| GOLD# | H4 | 10000 | 0.00 | 0.00 | 0.00 | 0.00% | 0 | 0 |

## Important Interpretation

ผลด้านบนเป็น smoke/integration evidence เท่านั้น ไม่ใช่หลักฐานว่าระบบทำกำไรได้ในอนาคต

เป้าหมายของเฟสนี้คือพิสูจน์ว่า:

- runner เปิด/ปิด MT5 ได้อย่างปลอดภัย
- ไม่ไปปิด MT5 process อื่น
- สร้าง artifacts แยกราย case ได้
- export report จาก MT5 ได้
- parse report ได้
- scoring แยก execution status ออกจาก research verdict ได้
- safety/risk gate ทำงาน โดยเฉพาะเคส GOLD# ที่ risk ต่ำเกิน minimum lot

## Files Added/Updated In This Phase

- `scripts/run_mt5_research_batch.ps1`
- `research/research_matrix.json`
- `tools/research_report_parser.py`
- `tools/research_score.py`
- `tools/generate_research_summary.py`
- `docs/13_Controlled_Research_Pipeline.md`
- `docs/14_MT5_Batch_Runner_Reliability.md`
- `docs/15_Robustness_Scoring_Method.md`
- `docs/16_Dedicated_MT5_Research_Instance_TH.md`
- `docs/17_Current_Research_Pipeline_Status_TH.md`
- `docs/verification/compile_after_research_pipeline.log`

## Notes For Reviewer

โปรดรีวิวโดยเน้นความปลอดภัยและความน่าเชื่อถือของ pipeline ก่อน ไม่ควร optimize หรือปรับ strategy เพื่อไล่กำไรจากรอบ smoke test นี้

ประเด็นที่ควรดูต่อ:

- parser ครอบคลุม MT5 report format จาก broker/locale อื่นพอหรือยัง
- classification thresholds เหมาะกับ train/validation/OOS หรือไม่
- GOLD# risk budget ควรใช้ deposit/risk/SL ที่ทำให้ lot sizing ไม่ต่ำกว่า broker minimum โดยยังคุมความเสี่ยงได้หรือไม่
- ควรแยก latest-run summary ออกจาก all-run historical summary เพื่อไม่ให้รัน debug เก่าปนกับรันที่ผ่านแล้ว

